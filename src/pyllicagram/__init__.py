"""pyllicagram: Python wrapper for the Gallicagram API.

Calls the Gallicagram API directly from Python. Gallicagram enables to build
time series of keywords used in a set of French corpora.

The main functions of this package are a port to Python of the R package
rallicagram by Vincent Bagilet (https://github.com/vincentbagilet/rallicagram).
"""

from typing import List

from ._data import DATASETS, load_dataset
from ._graphs import (
    gallicagraph,
    gallicagraph_associated,
    gallicagraph_cooccur,
    gallicagraph_occur,
)
from ._params import error_param
from ._queries import (
    gallicagram,
    gallicagram_all,
    gallicagram_associated,
    gallicagram_associated_lexicon,
    gallicagram_cooccur,
    gallicagram_cooccur_lexicon,
    gallicagram_lexicon,
    gallicagram_with,
    gallicagram_with_month,
    get_same_stem,
)
from .legacy import (
    associated,
    associated_article,
    contain,
    cooccur_doc,
    joker,
    pyllicagram,
)

__version__ = "2.0.0"

__all__ = [
    "error_param",
    "gallicagram",
    "gallicagram_all",
    "gallicagram_associated",
    "gallicagram_associated_lexicon",
    "gallicagram_cooccur",
    "gallicagram_cooccur_lexicon",
    "gallicagram_lexicon",
    "gallicagram_with",
    "gallicagram_with_month",
    "gallicagraph",
    "gallicagraph_associated",
    "gallicagraph_cooccur",
    "gallicagraph_occur",
    "get_same_stem",
    "list_corpora",
    "list_subcorpora",
    "stopwords_gallica",
    "word_lemma_stem",
    # functions of pyllicagram 1.x
    "associated",
    "associated_article",
    "contain",
    "cooccur_doc",
    "joker",
    "pyllicagram",
]


def __getattr__(name: str):
    # The datasets are only read when they are used. Each access returns a copy.
    if name in DATASETS:
        return load_dataset(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    return sorted(set(globals()) | set(DATASETS))
