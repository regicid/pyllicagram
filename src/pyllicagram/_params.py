"""Validation and preparation of the parameters of the API calls."""

from __future__ import annotations

import numbers
import warnings
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
from urllib.parse import quote

import pandas as pd

from ._data import _corpora, _subcorpora

# Characters left as they are in a keyword: they are meaningful for the API
# ("*" is a wildcard, "," separates series, "_" is a placeholder, "+" is read
# as a space...) and rallicagram sends them unencoded. Everything else that
# cannot appear literally in a URL, such as accents, spaces or "&", is
# percent-encoded.
_URL_SAFE = "+*',_-.~()!:;/=@$"


def _is_number(value: Any) -> bool:
    """Equivalent of R's ``is.numeric`` for a single value."""
    return isinstance(value, numbers.Real) and not isinstance(value, bool)


def _plain_number(value: Any) -> Any:
    """Turn 1960.0 into 1960, so that it prints like in R (``paste(1960)``)."""
    if _is_number(value) and float(value).is_integer():
        return int(value)
    return value


def _is_vector(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, frozenset, pd.Series, pd.Index)) or (
        hasattr(value, "__array__") and getattr(value, "ndim", 0) > 0
    )


def _as_strings(
    value: Union[str, Iterable[str], None], message: str
) -> List[str]:
    """Turn a string or a vector of strings into a list of strings.

    A single string is a vector of length one, as in R. It must not be iterated
    over, as this would search each of its letters.
    """
    if isinstance(value, str):
        return [value]
    if _is_vector(value):
        strings = list(value)  # type: ignore[arg-type]
        if all(isinstance(item, str) for item in strings):
            return strings
    raise ValueError(message)


def _is_whole(value: Any) -> bool:
    return _is_number(value) and float(value).is_integer()


def _nb_words(keyword: str) -> int:
    """Number of words of a keyword.

    The API reads "+" as a space and ignores the spaces at the end of a keyword.
    """
    words = keyword.replace("+", " ").split(" ")
    while words and words[-1] == "":
        words.pop()
    return len(words)


def _corpus_info(corpus: str) -> pd.Series:
    corpora = _corpora()
    return corpora.loc[corpora["corpus"] == corpus].iloc[0]


def error_param(
    info_corpus: pd.Series,
    keyword: Any,
    corpus: str,
    from_: Any,
    to: Any,
    resolution: Any,
    n_of_level: Any,
    subcorpora: Any,
    func_type: Optional[str] = None,
) -> None:
    """Internal function to check for errors in the parameters.

    This internal function checks for errors in the specified parameters,
    including the validity of the time range, the keyword, and the resolution,
    based on the provided information about the corpus.

    It performs the following checks:

    - Validity of the time range: ensures that the specified time range
      (`from_` to `to`) is numeric and valid.
    - Validity of the keyword: checks whether the specified `keyword` is a
      character string and not a vector of strings.
    - Availability of the function: checks that the calling function is
      available for this corpus.
    - Reliability of the corpus: verifies that the specified time range falls
      within the reliable range of the given corpus.
    - Validity of the resolution: ensures that the specified `resolution` is
      one of "daily", "monthly", or "yearly".
    - Validity of `n_of_level`: ensures that it is "grams", or "articles" for
      the lemonde corpus.
    - Validity of the subcorpora: ensures that the specified subcorpora are
      valid.

    Parameters
    ----------
    info_corpus : pandas.Series
        The row of `list_corpora` describing the selected corpus.
    keyword : str
        The keyword for analysis.
    corpus : str
        The code of the corpus.
    from_ : int
        The starting year for the analysis.
    to : int
        The ending year for the analysis.
    resolution : str
        The desired resolution for the analysis ("daily", "monthly" or
        "yearly").
    n_of_level : str
        The type of object to compute the number of occurrences for or the
        level at which to compute co-occurrences.
    subcorpora : list of str or None
        The codes of the subcorpora.
    func_type : str or None, default None
        The kind of function being called: "with", "cooccur", "associated" or
        None. Its availability for this corpus is
        checked against the `available_func` column of `list_corpora`. This
        parameter has no counterpart in rallicagram, which infers it from the
        text of the call.

    Returns
    -------
    None
        This function does not return a value but may issue warnings or raise
        errors if any issues are found.

    Raises
    ------
    ValueError
        If one of the parameters is invalid.
    """
    # errors in from/to
    if not _is_number(from_) or not _is_number(to):
        raise ValueError(
            "'from' and 'to' should be numeric or 'earliest' or 'latest' "
            "respectively."
        )

    if not _is_whole(from_) or not _is_whole(to):
        raise ValueError("'from' and 'to' should be whole numbers")

    if from_ > to:
        raise ValueError("'from' cannot be larger than 'to'")

    # errors in keyword
    if not isinstance(keyword, str):
        if _is_vector(keyword) and all(isinstance(item, str) for item in keyword):
            raise ValueError(
                "'keyword' should be a character string and not a character vector"
            )
        raise ValueError("'keyword' should be a character string")

    # availability of the function for this corpus
    if func_type is not None:
        available = info_corpus["available_func"]
        if pd.isna(available) or func_type not in available:
            raise ValueError("This function is not supported for this corpus")

    # reliability of the corpus
    if from_ < info_corpus["reliable_from"]:
        warnings.warn(
            f"The {corpus} corpus is only reliable after "
            f"{info_corpus['reliable_from']}",
            stacklevel=4,
        )
    if to > info_corpus["reliable_to"]:
        warnings.warn(
            f"The {corpus} corpus is only reliable before "
            f"{info_corpus['reliable_to']}",
            stacklevel=4,
        )

    # error in resolution
    if not (isinstance(resolution, str) and resolution in _RESOLUTIONS_FR):
        raise ValueError("Resolution can only be daily, monthly or yearly.")

    # error in n_of_level
    if not (n_of_level == "grams" or (corpus == "lemonde" and n_of_level == "articles")):
        raise ValueError(
            "'n_of' and 'cooccur_level' can only be equal to 'grams' except for "
            "the Le Monde corpus, for which they can also be equal to 'articles'"
        )

    # error in subcorpora
    if subcorpora is not None:
        all_subcorpora = _subcorpora()
        valid_subcorpora = set(
            all_subcorpora.loc[all_subcorpora["corpus"] == corpus, "subcorpus"]
        )
        if not set(subcorpora) <= valid_subcorpora:
            raise ValueError(
                "Invalid subcorpus name for this corpus. Should be None or one "
                "of the ones specified in pyllicagram.list_subcorpora."
            )


_RESOLUTIONS_FR = {"yearly": "annee", "monthly": "mois", "daily": "jour"}


def prepare_param(
    keyword: Any,
    corpus: Any,
    from_: Any,
    to: Any,
    resolution: Any = "yearly",
    n_of_level: Any = "grams",
    subcorpora: Union[str, Sequence[str], None] = None,
    func_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Internal function to prepare the parameters to use them in the API call.

    Checks potential errors, translates the parameters and sets parameters for
    the API call.

    Parameters
    ----------
    keyword : str
        The keyword for analysis.
    corpus : str
        The code of the corpus. "press" and "books" are accepted as aliases of
        "presse" and "livres", to handle code written with a previous version
        of rallicagram.
    from_ : int or "earliest"
        The starting year for the analysis.
    to : int or "latest"
        The ending year for the analysis.
    resolution : str, default "yearly"
        The desired resolution ("daily", "monthly" or "yearly").
    n_of_level : str, default "grams"
        The type of object to compute the number of occurrences for or the
        level at which to compute co-occurrences.
    subcorpora : str or list of str, default None
        The codes of the subcorpora.
    func_type : str or None, default None
        The kind of function being called: "with", "cooccur", "associated" or
        None. See `error_param`.

    Returns
    -------
    dict
        Contains the cleaned parameters: `keyword` (lower case, encoded for a
        URL), `keyword_plain` (lower case, not encoded), `corpus`, `from`,
        `to`, `resolution_fr`, `resolution_en` and `subcorpora`.
    """
    # to handle code written with a previous version of the package
    corpus_french = {"press": "presse", "books": "livres"}.get(corpus, corpus) if (
        isinstance(corpus, str)
    ) else corpus

    # The "route à part" rows of list_corpora are not codes of the API
    corpora = [
        code for code in _corpora()["corpus"] if not code.startswith("route à part")
    ]
    if not isinstance(corpus_french, str) or corpus_french not in corpora:
        raise ValueError(
            "The corpus should be one of: " + ", ".join(corpora)
        )

    info_corpus = _corpus_info(corpus_french)

    from_numeric = (
        int(info_corpus["reliable_from"])
        if isinstance(from_, str) and from_ == "earliest"
        else from_
    )
    to_numeric = (
        int(info_corpus["reliable_to"])
        if isinstance(to, str) and to == "latest"
        else to
    )

    subcorpora_list: Optional[List[str]] = None
    if subcorpora is not None:
        subcorpora_list = _as_strings(
            subcorpora, "'subcorpora' must be a character vector."
        )

    # error in params
    error_param(
        info_corpus,
        keyword,
        corpus_french,
        from_numeric,
        to_numeric,
        resolution,
        n_of_level,
        subcorpora_list,
        func_type,
    )

    # resolutions
    if resolution in ("monthly", "daily") and info_corpus["resolution"] == "yearly":
        resol = "yearly"
        warnings.warn(
            "Resolution set to 'yearly', the finest resolution available",
            stacklevel=3,
        )
    elif resolution == "daily" and info_corpus["resolution"] == "monthly":
        resol = "monthly"
        warnings.warn(
            "Resolution set to 'monthly', the finest resolution available",
            stacklevel=3,
        )
    else:
        resol = resolution

    keyword_plain = keyword.lower()

    return {
        "keyword": quote(keyword_plain, safe=_URL_SAFE),
        "keyword_plain": keyword_plain,
        "corpus": corpus_french,
        "from": _plain_number(from_numeric),
        "to": _plain_number(to_numeric),
        "resolution_fr": _RESOLUTIONS_FR[resol],
        "resolution_en": resol,
        # "+" is read as a space by the API, which separates the codes
        "subcorpora": "+".join(
            quote(code, safe="") for code in (subcorpora_list or [])
        ),
    }
