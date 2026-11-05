"""The datasets, the package metadata and the URLs sent by rallicagram."""

import json
import subprocess
import sys
import warnings
from pathlib import Path

import pytest

import pyllicagram


def test_dimensions():
    assert pyllicagram.list_corpora.shape == (71, 9)
    assert pyllicagram.list_subcorpora.shape == (1040, 6)
    assert (pyllicagram.list_subcorpora["corpus"] == "persee").sum() == 368
    assert (pyllicagram.list_subcorpora["corpus"] == "cairn").sum() == 672
    assert len(pyllicagram.stopwords_gallica) == 1000
    assert pyllicagram.word_lemma_stem.shape == (142694, 3)


def test_special_words_are_not_missing():
    assert pyllicagram.word_lemma_stem.notna().all().all()
    assert pyllicagram.list_corpora["corpus"].is_unique
    assert pyllicagram.list_corpora["nb_words"].isna().sum() == 48
    assert pyllicagram.list_corpora["available_func"].isna().sum() == 5


def test_types():
    corpora = pyllicagram.list_corpora
    assert corpora["alt_base"].sum() == 33
    assert corpora.loc[corpora["corpus"] == "lemonde", "max_length"].iloc[0] == 3
    subcorpora = pyllicagram.list_subcorpora
    assert isinstance(subcorpora["disciplines"].iloc[0], list)
    assert subcorpora["subcorpus"].iloc[0] == "arss"
    assert subcorpora["disciplines"].iloc[0] == [
        "Économie", "Histoire", "Science politique", "Sociologie",
    ]
    exploded = subcorpora["disciplines"].explode().dropna()
    assert not exploded.isin(["", "NA"]).any()
    assert subcorpora.loc[subcorpora["subcorpus"] == "aopo", "disciplines"].iloc[0] == []
    cairn = subcorpora.loc[subcorpora["corpus"] == "cairn"]
    assert cairn["subcorpus"].is_unique
    assert cairn["reliable_from"].isna().all()
    assert subcorpora["reliable_from"].iloc[0] == 1985
    assert corpora.loc[corpora["corpus"] == "cairn", "corpus_name"].iloc[0] == "Cairn"


def test_datasets_are_copies():
    pyllicagram.list_corpora.drop(pyllicagram.list_corpora.index, inplace=True)
    pyllicagram.stopwords_gallica.clear()
    pyllicagram.list_subcorpora["disciplines"].iloc[0].clear()
    assert len(pyllicagram.list_corpora) == 71
    assert len(pyllicagram.stopwords_gallica) == 1000
    assert len(pyllicagram.list_subcorpora["disciplines"].iloc[0]) > 0


def test_unknown_attribute():
    with pytest.raises(AttributeError):
        pyllicagram.does_not_exist


def test_all_is_valid():
    for name in pyllicagram.__all__:
        assert getattr(pyllicagram, name) is not None


def test_version_matches_pyproject():
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    assert f'version = "{pyllicagram.__version__}"' in pyproject.read_text(encoding="utf-8")


def test_import_has_no_side_effect():
    # pyllicagram 1.x sent a request and disabled SSL verification when imported
    code = (
        "import ssl, socket\n"
        "default = ssl._create_default_https_context\n"
        "def forbidden(*a, **k): raise AssertionError('network at import')\n"
        "socket.socket.connect = forbidden\n"
        "import pyllicagram\n"
        "assert ssl._create_default_https_context is default\n"
    )
    subprocess.run([sys.executable, "-W", "ignore", "-c", code], check=True)


def _cases():
    path = Path(__file__).parent / "fixtures" / "r_urls.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _cases(), ids=lambda c: f"{c['fn']}-{sorted(c['args'].items())}")
def test_urls_are_those_of_rallicagram(case, api):
    """The URLs were checked against those sent by rallicagram: tools/r_parity."""
    args = {("from_" if k == "from" else k): v for k, v in case["args"].items()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            getattr(pyllicagram, case["fn"])(**args)
        except Exception:
            # the canned answers do not suit every expected failure
            pass
    assert api[: len(case["urls"])] == case["urls"]


_DOCUMENTED = [
    "error_param", "gallicagram", "gallicagram_all", "gallicagram_associated",
    "gallicagram_associated_lexicon", "gallicagram_cooccur",
    "gallicagram_cooccur_lexicon", "gallicagram_lexicon", "gallicagram_with",
    "gallicagram_with_month", "gallicagraph", "gallicagraph_associated",
    "gallicagraph_cooccur", "gallicagraph_occur", "get_same_stem",
]


def _all_documented():
    from pyllicagram import _params, _read

    functions = [getattr(pyllicagram, name) for name in _DOCUMENTED]
    return functions + [_params.prepare_param, _read.read_data_gallicagram, _read.tidy_gallicagram]


@pytest.mark.parametrize("function", _all_documented(), ids=lambda f: f.__name__)
def test_docstring_matches_signature(function):
    """Each parameter is documented, in order, with its actual default."""
    import inspect
    import re

    doc = inspect.getdoc(function)
    section = re.search(r"Parameters\n-+\n(.*?)(\n\n?Returns\n-+)", doc, re.S).group(1)
    entries = re.findall(r"^(\w+) : (.+)$", section, re.M)
    signature = inspect.signature(function).parameters
    assert [name for name, _ in entries] == list(signature)
    for name, description in entries:
        default = signature[name].default
        assert "{" not in description
        match = re.search(r", default (.+)$", description)
        if default is inspect.Parameter.empty:
            assert match is None, name
        else:
            assert match is not None, name
            assert match.group(1).strip('"') == str(default), name
