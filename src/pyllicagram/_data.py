"""Datasets shipped with pyllicagram.

The files in ``pyllicagram/data`` are exports of the datasets of the R package
rallicagram (0.2.0). The only changes are for Cairn, which rallicagram cannot
query: its row of list_corpora has its actual code, and list_subcorpora also
contains its reviews (see tools/update_cairn_subcorpora.py).
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources
from typing import List, Tuple

import pandas as pd

# In the corpus code/name columns and in the word lists, strings such as "null"
# or "nan" are genuine values. Only the literal "NA" written by the export
# marks a missing value, and only in the columns listed below.
_CORPORA_NA = {"nb_words": ["NA"], "available_func": ["NA"]}
_SUBCORPORA_NA = {"reliable_from": ["NA"], "reliable_to": ["NA"]}


def _read(name: str, **kwargs) -> pd.DataFrame:
    path = resources.files("pyllicagram").joinpath("data").joinpath(name)
    with path.open("rb") as handle:
        compression = "gzip" if name.endswith(".gz") else None
        return pd.read_csv(
            handle,
            encoding="utf-8",
            compression=compression,
            keep_default_na=False,
            **kwargs,
        )


@lru_cache(maxsize=1)
def _corpora() -> pd.DataFrame:
    """Internal, shared copy of ``list_corpora``. Must not be modified."""
    return _read("list_corpora.csv", na_values=_CORPORA_NA).astype(
        {"max_length": "int64", "alt_base": "bool"}
    )


@lru_cache(maxsize=1)
def _subcorpora() -> pd.DataFrame:
    """Internal, shared copy of ``list_subcorpora``. Must not be modified."""
    subcorpora = _read("list_subcorpora.csv", na_values=_SUBCORPORA_NA).astype(
        {"reliable_from": "Int64", "reliable_to": "Int64"}
    )
    # In the source data, the disciplines end with ";" or are "NA"
    subcorpora["disciplines"] = [
        [name for name in value.split(";") if name not in ("", "NA")]
        for value in subcorpora["disciplines"]
    ]
    return subcorpora


@lru_cache(maxsize=1)
def _stopwords() -> Tuple[str, ...]:
    """Internal, immutable copy of ``stopwords_gallica``."""
    return tuple(_read("stopwords_gallica.csv", dtype=str)["stopword"])


@lru_cache(maxsize=1)
def _word_lemma_stem() -> pd.DataFrame:
    """Internal, shared copy of ``word_lemma_stem``. Must not be modified."""
    return _read("word_lemma_stem.csv.gz", dtype=str)


def load_dataset(name: str):
    """Return a fresh copy of a dataset, which the caller is free to modify."""
    if name == "list_corpora":
        return _corpora().copy()
    if name == "list_subcorpora":
        subcorpora = _subcorpora().copy()
        subcorpora["disciplines"] = [
            list(value) for value in subcorpora["disciplines"]
        ]
        return subcorpora
    if name == "stopwords_gallica":
        words: List[str] = list(_stopwords())
        return words
    if name == "word_lemma_stem":
        return _word_lemma_stem().copy()
    raise KeyError(name)


DATASETS = ("list_corpora", "list_subcorpora", "stopwords_gallica", "word_lemma_stem")
