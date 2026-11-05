"""Port of tests/testthat/test-prepare_param.R, and more."""

import warnings

import numpy as np
import pytest

from pyllicagram import gallicagram
from pyllicagram._params import prepare_param


@pytest.mark.parametrize("keyword", [23, False, None])
def test_keyword_not_string(keyword):
    with pytest.raises(ValueError, match="^'keyword' should be a character string$"):
        gallicagram(keyword=keyword)


@pytest.mark.parametrize("keyword", [["avion", "patate"], ("avion",), np.array(["a", "b"])])
def test_keyword_vector(keyword):
    with pytest.raises(ValueError, match="and not a character vector"):
        gallicagram(keyword=keyword)


@pytest.mark.parametrize(
    "kwargs", [{"from_": "err"}, {"to": "err"}, {"from_": True}, {"to": None}, {"from_": "1960"}]
)
def test_from_to_not_numeric(kwargs):
    with pytest.raises(ValueError, match="'from' and 'to' should be numeric"):
        gallicagram(keyword="président", **kwargs)


@pytest.mark.parametrize("kwargs", [{"from_": 1960.5}, {"to": float("nan")}, {"to": float("inf")}])
def test_from_to_not_whole(kwargs):
    with pytest.raises(ValueError, match="should be whole numbers"):
        gallicagram("président", **kwargs)


def test_route_a_part_rows_are_not_codes(api):
    with pytest.raises(ValueError, match="The corpus should be one of") as error:
        gallicagram("a", corpus="route à part (persee+cairn)", from_=2010, to=2010)
    assert "route à part" not in str(error.value)
    assert ", cairn," in str(error.value)
    assert api == []


def test_from_larger_than_to():
    with pytest.raises(ValueError, match="'from' cannot be larger than 'to'"):
        gallicagram("président", from_=2000, to=1990)


@pytest.mark.parametrize("corpus", ["err", 3, None, ["lemonde"]])
def test_invalid_corpus(corpus):
    with pytest.raises(ValueError, match="The corpus should be one of"):
        gallicagram(keyword="président", corpus=corpus)


def test_invalid_resolution():
    with pytest.raises(ValueError, match="Resolution can only"):
        gallicagram(keyword="président", resolution="err")


@pytest.mark.parametrize(
    "corpus,expected", [("books", "yearly"), ("press", "monthly")]
)
def test_resolution_set(corpus, expected):
    with pytest.warns(UserWarning, match=f"Resolution set to '{expected}'"):
        output = gallicagram(
            "président", corpus=corpus, from_=1800, to=1820, resolution="daily"
        )
    assert set(output["resolution"]) == {expected}


@pytest.mark.parametrize(
    "corpus,from_,to,message",
    [
        ("press", 1700, 1740, "The presse corpus is only reliable after 1789"),
        ("books", 1800, 1970, "The livres corpus is only reliable before 1940"),
    ],
)
def test_non_reliable(corpus, from_, to, message):
    with pytest.warns(UserWarning, match=message):
        gallicagram("président", corpus, from_, to, "yearly")


def test_n_of_only_lemonde():
    with pytest.raises(ValueError, match="'n_of' and 'cooccur_level' can only"):
        gallicagram("président", corpus="presse", n_of="articles")


def test_subcorpora_validated():
    with pytest.raises(ValueError, match="Invalid subcorpus name"):
        gallicagram("président", corpus="persee", subcorpora="err", resolution="yearly")
    with pytest.raises(ValueError, match="Invalid subcorpus name"):
        gallicagram("président", corpus="lemonde", subcorpora="arss")


def test_earliest_latest_aliases_and_translation():
    param = prepare_param("Le Président", "press", "earliest", "latest", "monthly")
    assert param == {
        "keyword": "le%20pr%C3%A9sident",
        "keyword_plain": "le président",
        "corpus": "presse",
        "from": 1789,
        "to": 1950,
        "resolution_fr": "mois",
        "resolution_en": "monthly",
        "subcorpora": "",
    }


def test_url_characters():
    # what is meaningful for the API is sent as in rallicagram...
    assert prepare_param("l'état,ecolo*+a_", "lemonde", 1960, 1960)["keyword"] == (
        "l'%C3%A9tat,ecolo*+a_"
    )
    # ... and what would break the URL is encoded
    assert prepare_param("a&b#c%d", "lemonde", 1960, 1960)["keyword"] == "a%26b%23c%25d"


def test_numbers_print_as_integers():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        param = prepare_param("a", "lemonde", 1960.0, np.int64(1961))
    assert (str(param["from"]), str(param["to"])) == ("1960", "1961")
