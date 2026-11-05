"""Port of tests/testthat/test-gallicagram_{cooccur,associated,with}*.R, and more."""

import pytest

from pyllicagram import (
    gallicagram_associated,
    gallicagram_associated_lexicon,
    gallicagram_cooccur,
    gallicagram_cooccur_lexicon,
    gallicagram_with,
    gallicagram_with_month,
    get_same_stem,
    stopwords_gallica,
)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"keyword_1": ["avion", "patate"], "keyword_2": "test"},
        {"keyword_1": "test", "keyword_2": ["avion", "patate"]},
    ],
)
def test_cooccur_keywords(kwargs):
    with pytest.raises(ValueError, match="and not a character vector"):
        gallicagram_cooccur(**kwargs)


def test_cooccur_output(api):
    output = gallicagram_cooccur("président", "mauvais", from_=1960, to=1960, resolution="yearly")
    assert list(output.columns) == [
        "date", "keyword_1", "keyword_2", "n_cooccur", "n_total", "prop_cooccur",
        "year", "corpus", "resolution", "cooccur_level",
    ]
    assert output["cooccur_level"].iloc[0] == "4-grams"
    assert "/contain?corpus=lemonde" in api[0] and api[0].endswith("&count=True")


def test_cooccur_count_phrase_and_articles(api):
    output = gallicagram_cooccur("a", "b", from_=1960, to=1960, count_phrase=True, cooccur_level="articles", resolution="yearly")
    assert "gram" in output.columns
    assert output["cooccur_level"].iloc[0] == "articles"
    assert "/cooccur?corpus=lemonde" in api[0] and api[0].endswith("&count=False")


def test_cooccur_other_corpus_level():
    output = gallicagram_cooccur("a", "b", corpus="press", from_=1900, to=1900, resolution="yearly")
    assert output["cooccur_level"].iloc[0] == "3-grams"


def test_cooccur_lexicon_output(api):
    output = gallicagram_cooccur_lexicon(["a", "b"], ["c", "d"], from_=1960, to=1960, resolution="yearly")
    assert len(api) == 4
    assert len(output) == 1
    assert list(output.columns) == [
        "date", "n_cooccur", "n_total", "prop_cooccur", "year", "corpus", "resolution",
        "cooccur_level", "keyword_1", "keyword_2", "lexicon_1", "lexicon_2",
    ]
    row = output.iloc[0]
    assert (row["n_cooccur"], row["keyword_1"], row["lexicon_2"]) == (8, "a", "c+d")


def test_function_not_available_for_corpus():
    for function in (gallicagram_with, gallicagram_associated):
        with pytest.raises(ValueError, match="not supported for this corpus"):
            function("france", corpus="presse_moderne", from_=2020, to=2020)
    with pytest.raises(ValueError, match="not supported for this corpus"):
        gallicagram_cooccur("a", "b", corpus="20minutes", from_=2020, to=2020)


def test_keyword_text_does_not_affect_availability():
    # rallicagram looks for "with" in the text of the call
    from pyllicagram import gallicagram

    gallicagram("with", corpus="presse_moderne", from_=2020, to=2020, resolution="yearly")


def test_associated_errors():
    with pytest.raises(ValueError, match="and not a character vector"):
        gallicagram_associated(keyword=["avion", "patate"])
    with pytest.raises(ValueError, match="'distance' has to be larger than 0"):
        gallicagram_associated(keyword="son camarade de", distance=0)
    with pytest.raises(ValueError, match="'distance' should be numeric"):
        gallicagram_associated("a", distance="err")
    with pytest.raises(ValueError, match="only be set to 'articles' for the lemonde"):
        gallicagram_associated("a", corpus="presse", distance="articles")
    with pytest.raises(ValueError, match="cannot contain an apostrophe"):
        gallicagram_associated("l'ami")
    for n_results in ("err", -3, 0, 2.5):
        with pytest.raises(ValueError, match="'n_results' should be a positive whole"):
            gallicagram_associated("a", n_results=n_results)
    with pytest.raises(ValueError, match="'distance' should be a whole number"):
        gallicagram_associated("a", distance=1.5)


def test_associated_distance_too_large():
    with pytest.warns(UserWarning, match="Distance set to 'max'.+cannot be more than 3"):
        gallicagram_associated("camarade", corpus="lemonde", distance=5)


def test_associated_lengths_and_labels(api):
    assert gallicagram_associated("a", distance=1)["cooccur_level"].iloc[0] == "2-grams"
    assert "n_joker=all&length=2" in api[-1]
    assert gallicagram_associated("a")["cooccur_level"].iloc[0] == "3-grams"
    assert "n_joker=all&length=3" in api[-1]
    assert gallicagram_associated("a b", distance=1)["cooccur_level"].iloc[0] == "3-grams"
    articles = gallicagram_associated("a", distance="articles")
    assert articles["cooccur_level"].iloc[0] == "articles"
    assert "/associated_article?" in api[-1]


def test_associated_cleaning():
    output = gallicagram_associated("ami", stopwords=["de"], from_=1960, to=1960)
    # l'ami -> ami, the keyword itself. 1960 and a2 are numbers. d' -> "".
    assert list(output["associated_word"]) == ["khrouchtchev", "n'est", "null"]
    assert list(output["n_cooccur"]) == [14, 2, 1]
    assert list(output.columns) == [
        "associated_word", "n_cooccur", "keyword", "corpus", "from", "to", "cooccur_level",
    ]


def test_associated_options(api):
    keep = gallicagram_associated("ami", stopwords=None, remove_numbers=False, n_results=3)
    assert list(keep["associated_word"]) == ["de", "khrouchtchev", "1960"]
    assert "n_joker=4" in api[-1]  # n_results + number of words
    default = gallicagram_associated("ami", n_results="all")
    assert "de" not in set(default["associated_word"])
    assert "de" in stopwords_gallica[:500]


def test_associated_keeps_word_case_insensitive():
    output = gallicagram_associated("AMI", stopwords=None, n_results="all")
    assert "ami" not in set(output["associated_word"])


@pytest.fixture
def no_associated_word(monkeypatch):
    from pyllicagram import _read

    from .conftest import FakeResponse

    monkeypatch.setattr(_read.requests, "get", lambda url, **kw: FakeResponse("gram,tot\n"))


@pytest.mark.filterwarnings("error::FutureWarning")
def test_associated_without_results(no_associated_word):
    output = gallicagram_associated("zzqqxyzz", from_=2000, to=2000)
    assert len(output) == 0
    assert list(output.columns) == [
        "associated_word", "n_cooccur", "keyword", "corpus", "from", "to", "cooccur_level",
    ]
    assert len(gallicagram_associated_lexicon(["a", "b"], from_=2000, to=2000)) == 0


def test_associated_lexicon_keeps_results_of_other_keywords(monkeypatch):
    from pyllicagram import _read

    from .conftest import FakeResponse

    def get(url, **kwargs):
        text = "gram,tot\nparti,4\n" if "mot=a&" in url else "gram,tot\n"
        return FakeResponse(text)

    monkeypatch.setattr(_read.requests, "get", get)
    output = gallicagram_associated_lexicon(["zzz", "a"], from_=2000, to=2000)
    assert list(output["associated_word"]) == ["parti"]
    assert output["n_cooccur"].dtype.kind == "i"


def test_associated_articles_several_words():
    with pytest.warns(UserWarning, match="only available for keywords made of one word"):
        gallicagram_associated("le camarade", distance="articles")


def test_associated_plus_keyword(api):
    output = gallicagram_associated("ami+de", stopwords=None, distance=1, n_results="all")
    assert "length=3" in api[0]
    assert not {"ami", "de"} & set(output["associated_word"])


def test_associated_lexicon_word_on_one_row():
    output = gallicagram_associated_lexicon(
        ["camarade", "le camarade"], distance=1, stopwords=["de"], from_=1960, to=1960
    )
    assert output["associated_word"].is_unique
    assert output.loc[output["associated_word"] == "khrouchtchev", "n_cooccur"].iloc[0] == 28
    assert set(output["cooccur_level"]) == {"2-grams, 3-grams"}


def test_associated_lexicon_ignores_case_duplicates(api):
    gallicagram_associated_lexicon(["Ami", "ami"], from_=1960, to=1960)
    assert len(api) == 1


def test_cooccur_lexicon_ignores_case_duplicates(api):
    output = gallicagram_cooccur_lexicon(["A", "a"], ["b", "B"], from_=1960, to=1960, resolution="yearly")
    assert len(api) == 1
    assert (output["lexicon_1"].iloc[0], output["lexicon_2"].iloc[0]) == ("A", "b")


def test_cairn_functions(api):
    gallicagram_with("a", corpus="cairn", from_=2010, to=2011)
    gallicagram_associated("a", corpus="cairn", from_=2010, to=2011)
    assert "/joker_ngram?corpus=cairn&" in api[0] and "elias" not in api[0]
    assert "/associated_ngram?corpus=cairn&" in api[1] and "elias" not in api[1]
    with pytest.raises(ValueError, match="not supported for this corpus"):
        gallicagram_cooccur("a", "b", corpus="cairn", from_=2010, to=2011)


def test_associated_lexicon():
    with pytest.raises(ValueError, match="'lexicon' must be a character vector."):
        gallicagram_associated_lexicon(lexicon=3)
    with pytest.raises(ValueError, match="'distance' has to be larger than 0"):
        gallicagram_associated_lexicon(lexicon="son camarade de", distance=0)
    with pytest.warns(UserWarning, match="Distance set to 'max'"):
        gallicagram_associated_lexicon(lexicon="camarade", corpus="lemonde", distance=5, from_=2020)
    output = gallicagram_associated_lexicon(["a", "b"], stopwords=["de"], n_results=2, from_=1960, to=1960)
    assert list(output["associated_word"]) == ["khrouchtchev", "ami"]
    assert list(output["n_cooccur"]) == [28, 14]
    assert set(output["lexicon"]) == {"a+b"}
    assert set(output["keyword"]) == {"a"}


def test_with_errors():
    with pytest.raises(ValueError, match="and not a character vector"):
        gallicagram_with(keyword=["avion", "patate"])
    with pytest.raises(ValueError, match="'length' cannot be more than 3"):
        gallicagram_with("camarade", corpus="lemonde", length=5)
    with pytest.raises(ValueError, match="'length' cannot be more than 5"):
        gallicagram_with("camarade", corpus="books", length=8, from_=1860, to=1890)
    with pytest.raises(ValueError, match="'length' has to be larger"):
        gallicagram_with("son camarade de", length=2)
    with pytest.raises(ValueError, match="'length' should be numeric"):
        gallicagram_with("camarade", length="err")
    with pytest.raises(ValueError, match="'length' should be a whole number"):
        gallicagram_with("camarade", length=1.5)
    with pytest.raises(ValueError, match="'n_results' should be a positive whole"):
        gallicagram_with("camarade", n_results=-1)
    with pytest.raises(ValueError, match="'length' has to be larger"):
        gallicagram_with("a+b+c", length=2)
    with pytest.raises(ValueError, match="cannot contain an apostrophe"):
        gallicagram_with("l'ami")


def test_with_output(api):
    output = gallicagram_with("Le Camarade", from_=1960, to=1970, n_results="all", length=3)
    assert list(output.columns) == ["n_occur", "ngram", "keyword", "corpus", "from", "to"]
    assert output["keyword"].iloc[0] == "le camarade"
    assert output["ngram"].iloc[1] == "camarade null"
    assert api[0].endswith(
        "/joker_ngram?corpus=lemonde&mot=le%20camarade&from=1960&to=1970&n_joker=all&length=3"
    )


def test_with_month(api):
    output = gallicagram_with_month("camarade", year=1960, month=3, n_results=3)
    assert list(output.columns) == ["n_occur", "ngram", "keyword", "corpus", "year", "month"]
    assert api[0].endswith(
        "/joker_mois?corpus=lemonde&mot=camarade&year=1960&month=3&n_joker=3&length=2"
    )
    with pytest.raises(ValueError, match="'year' and 'month' should be numeric"):
        gallicagram_with_month("camarade", month="err")
    with pytest.raises(ValueError, match="'from' and 'to' should be numeric"):
        gallicagram_with_month("camarade", year="err")
    for month in (0, 13, 1.5):
        with pytest.raises(ValueError, match="'month' should be a whole number between"):
            gallicagram_with_month("camarade", month=month)
    assert gallicagram_with_month("Camarade")["keyword"].iloc[0] == "camarade"


def test_get_same_stem():
    assert get_same_stem("écologie") == [
        "écologie", "écologique", "écologiquement", "écologiques",
        "écologiste", "écologistes",
    ]
    with pytest.raises(ValueError, match="Keyword not in the dataset"):
        get_same_stem("motquinexistepasxyz")
