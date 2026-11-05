"""Port of tests/testthat/test-gallicagram*.R, and more."""

import pandas as pd
import pytest
import requests

from pyllicagram import _read, gallicagram, gallicagram_all, gallicagram_lexicon

from .conftest import FakeResponse


def test_columns_yearly():
    output = gallicagram("Président", from_=1960, to=1960, resolution="yearly")
    assert list(output.columns) == [
        "date", "keyword", "n_occur", "n_total", "prop_occur", "year",
        "corpus", "resolution", "n_of",
    ]
    row = output.iloc[0]
    assert str(row["date"].date()) == "1960-01-01"
    assert row["keyword"] == "président"
    assert row["prop_occur"] == 0.2
    assert row["n_of"] == "1-grams"


def test_columns_monthly_daily():
    monthly = gallicagram("a", from_=1960, to=1960)
    assert list(monthly.columns)[5:7] == ["year", "month"]
    assert [str(d.date()) for d in monthly["date"]] == ["1960-01-01", "1960-02-01"]
    daily = gallicagram("a", corpus="figaro", from_=1900, to=1900, resolution="daily")
    assert list(daily.columns)[5:8] == ["year", "month", "day"]
    assert [str(d.date()) for d in daily["date"]] == ["1900-01-01", "1900-01-02"]


def test_n_of_number_of_words():
    output = gallicagram("le président", from_=1960, to=1960, resolution="yearly")
    assert set(output["n_of"]) == {"2-grams"}


def test_routes(api):
    gallicagram("a", from_=1960, to=1960, n_of="articles")
    gallicagram("a", corpus="persee", from_=1990, to=1990, resolution="yearly",
                subcorpora=["arss", "rfsoc"])
    gallicagram("a", corpus="20minutes", from_=2020, to=2020)
    assert "/query_article?corpus=lemonde&mot=a&from=1960&to=1960&resolution=mois" in api[0]
    assert api[1].endswith(
        "/query_persee?corpus=persee&mot=a&from=1990&to=1990&resolution=annee&revue=arss+rfsoc"
    )
    assert api[2].endswith("&elias=true") and "/query_ngram?" in api[2]


def test_cairn(api):
    output = gallicagram(
        "a", corpus="cairn", from_=2010, to=2010, resolution="yearly", subcorpora=["ARSS", "ACO"]
    )
    assert set(output["corpus"]) == {"cairn"}
    assert api[0].endswith(
        "/query_cairn?corpus=cairn&mot=a&from=2010&to=2010&resolution=annee&revue=ARSS+ACO"
    )
    with pytest.warns(UserWarning, match="Resolution set to 'yearly'"):
        gallicagram("a", corpus="cairn", from_=2010, to=2010)
    # the codes are specific to each corpus
    with pytest.raises(ValueError, match="Invalid subcorpus name"):
        gallicagram("a", corpus="cairn", subcorpora="arss", resolution="yearly")
    with pytest.raises(ValueError, match="Invalid subcorpus name"):
        gallicagram("a", corpus="persee", subcorpora="ACO", resolution="yearly")


@pytest.mark.parametrize(
    "keyword,expected",
    [("velo+auto", "2-grams"), ("président ", "1-grams"), ("a b+c", "3-grams"), ("a", "1-grams")],
)
def test_n_of_counts_words_as_the_api(keyword, expected):
    output = gallicagram(keyword, from_=1960, to=1960, resolution="yearly")
    assert set(output["n_of"]) == {expected}


def test_articles_multiple_words_warns():
    with pytest.warns(UserWarning, match="only available for keywords made of one word"):
        gallicagram("le président", from_=1960, to=1960, n_of="articles")


def test_old_dates_are_not_lost(monkeypatch):
    # years before 1677 do not fit in nanoseconds
    monkeypatch.setattr(
        _read.requests, "get",
        lambda url, **kw: FakeResponse("n,annee,gram,total\n0,1380,a,5233\n"),
    )
    output = gallicagram("a", corpus="livres", from_=1700, to=1701, resolution="yearly")
    assert output["date"].iloc[0].year == 1380


@pytest.mark.parametrize("word", ["null", "none", "nan", "na", "1945", "true"])
def test_words_stay_text(monkeypatch, word):
    monkeypatch.setattr(
        _read.requests, "get",
        lambda url, **kw: FakeResponse(f"n,annee,gram,total\n2,1960,{word},10\n"),
    )
    output = gallicagram(word, from_=1960, to=1960, resolution="yearly")
    assert output["keyword"].iloc[0] == word


def test_empty_answer(monkeypatch):
    monkeypatch.setattr(
        _read.requests, "get", lambda url, **kw: FakeResponse("n,gram,annee,total\n")
    )
    output = gallicagram("a", from_=1960, to=1960, resolution="yearly")
    assert len(output) == 0
    assert "date" in output.columns


def test_http_error(monkeypatch):
    monkeypatch.setattr(
        _read.requests, "get", lambda url, **kw: FakeResponse("corpus invalide", 400)
    )
    with pytest.raises(requests.HTTPError, match="corpus invalide"):
        gallicagram("a", from_=1960, to=1960)


def test_zero_total_is_not_an_error(monkeypatch):
    monkeypatch.setattr(
        _read.requests, "get",
        lambda url, **kw: FakeResponse("n,annee,gram,total\n0,1960,a,0\n"),
    )
    output = gallicagram("a", from_=1960, to=1960, resolution="yearly")
    assert pd.isna(output["prop_occur"].iloc[0])


def test_all(api):
    with pytest.warns(UserWarning):
        output = gallicagram_all("le président")
    assert ["lemonde", "presse", "livres"] == list(output["corpus"].unique())
    assert set(output["n_of"]) == {"2-grams"}
    assert "corpus=lemonde&mot=le%20pr%C3%A9sident&from=1944&to=2023" in api[0]
    assert "corpus=presse&mot=le%20pr%C3%A9sident&from=1789&to=1949" in api[1]
    assert "corpus=livres&mot=le%20pr%C3%A9sident&from=1000&to=1939" in api[2]


def test_lexicon_not_vector():
    for lexicon in (3, [], [3]):
        with pytest.raises(ValueError, match="'lexicon' must be a character vector."):
            gallicagram_lexicon(lexicon=lexicon)


def test_lexicon_ignores_case_duplicates(api):
    output = gallicagram_lexicon(
        ["Camarade", "camarade", "ami"], from_=1960, to=1960, resolution="yearly"
    )
    assert len(api) == 2
    assert output["lexicon"].iloc[0] == "Camarade+ami"
    assert output["keyword"].iloc[0] == "Camarade"


def test_lexicon_sums(monkeypatch):
    counts = {"a": 2, "b": 5}

    def get(url, **kwargs):
        word = url.split("mot=")[1].split("&")[0]
        return FakeResponse(f"n,annee,gram,total\n{counts[word]},1960,{word},10\n")

    monkeypatch.setattr(_read.requests, "get", get)
    output = gallicagram_lexicon(["a", "b"], from_=1960, to=1960, resolution="yearly")
    assert len(output) == 1
    row = output.iloc[0]
    assert (row["keyword"], row["n_occur"], row["prop_occur"], row["lexicon"]) == (
        "a", 7, 0.7, "a+b",
    )


def test_single_string_lexicon_is_not_split_into_letters(api):
    output = gallicagram_lexicon("camarade", from_=1960, to=1960, resolution="yearly")
    assert len(api) == 1
    assert output["lexicon"].iloc[0] == "camarade"
