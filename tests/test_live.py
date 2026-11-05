"""Calls the real API, with: pytest -m live"""

import pytest

import pyllicagram as p

pytestmark = pytest.mark.live


def test_gallicagram():
    output = p.gallicagram("président", from_=1960, to=1960)
    assert output["n_occur"].iloc[0] == 1338
    assert output["n_total"].iloc[0] == 872943


def test_articles():
    assert p.gallicagram("président", from_=1960, to=1960, n_of="articles", resolution="yearly")["n_occur"].iloc[0] == 7294


def test_persee_subcorpora():
    output = p.gallicagram("république", corpus="persee", from_=1990, to=1991, resolution="yearly", subcorpora="arss")
    assert list(output["n_occur"]) == [13, 59]


def test_associated_and_with():
    assert p.gallicagram_associated("camarade", from_=1960, to=1970, n_results=1, distance=2)["associated_word"].iloc[0] == "khrouchtchev"
    assert p.gallicagram_with("camarade", from_=1960, to=1970, n_results=1)["ngram"].iloc[0] == "camarade de"
    assert len(p.gallicagram_with_month("camarade", n_results=2)) == 2


def test_cooccur():
    assert p.gallicagram_cooccur("président", "république", from_=1960, to=1960, resolution="yearly")["n_cooccur"].iloc[0] == 2673


def test_cairn():
    all_reviews = p.gallicagram("test", corpus="cairn", from_=2010, to=2011, resolution="yearly")
    assert list(all_reviews["n_occur"]) == [3016, 2569]
    one = p.gallicagram("test", corpus="cairn", from_=2010, to=2010, resolution="yearly", subcorpora="ARSS")
    two = p.gallicagram("test", corpus="cairn", from_=2010, to=2010, resolution="yearly", subcorpora=["ARSS", "ACO"])
    assert 0 < one["n_total"].iloc[0] < two["n_total"].iloc[0] < all_reviews["n_total"].iloc[0]
    assert len(p.gallicagram_with("république", corpus="cairn", from_=2010, to=2011, n_results=3)) == 3
    assert len(p.gallicagram_associated("république", corpus="cairn", from_=2010, to=2011, n_results=3)) == 3


def test_every_cairn_review_code_is_known_to_the_api():
    reviews = p.list_subcorpora
    codes = reviews.loc[reviews["corpus"] == "cairn", "subcorpus"]
    output = p.gallicagram(
        "la", corpus="cairn", from_=2020, to=2020, resolution="yearly", subcorpora=list(codes[:30])
    )
    assert output["n_total"].iloc[0] > 0


def test_associated_without_results():
    assert len(p.gallicagram_associated("zzqqxyzz", from_=2000, to=2000)) == 0
    assert len(p.gallicagram_associated_lexicon(["zzqqxyzz", "wwqqxyzz"], from_=2000, to=2000)) == 0


def test_plus_counts_as_two_words():
    output = p.gallicagram("vélo+auto", from_=1990, to=1990, resolution="yearly")
    assert output["n_of"].iloc[0] == "2-grams"
    assert output["n_total"].iloc[0] == 15502385


def test_trailing_space_is_one_word():
    assert p.gallicagram("président ", from_=1960, to=1960, resolution="yearly")["n_of"].iloc[0] == "1-grams"


def test_lexicon_case_duplicates_not_counted_twice():
    alone = p.gallicagram("camarade", from_=2000, to=2000, resolution="yearly")["n_occur"].iloc[0]
    both = p.gallicagram_lexicon(["Camarade", "camarade"], from_=2000, to=2000, resolution="yearly")
    assert both["n_occur"].iloc[0] == alone


def test_associated_lexicon_different_lengths():
    output = p.gallicagram_associated_lexicon(["camarade", "le camarade"], from_=1960, to=1961, distance=1)
    assert output["associated_word"].is_unique
    assert set(output["cooccur_level"]) == {"2-grams, 3-grams"}


def test_legacy():
    assert p.pyllicagram("francis", debut=1900, fin=1900, resolution="annee")["n"].iloc[0] == 8639
