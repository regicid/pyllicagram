"""The functions querying the Gallicagram API."""

from __future__ import annotations

import re
import warnings
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import pandas as pd

from ._data import _stopwords, _word_lemma_stem
from ._params import (
    _as_strings,
    _corpus_info,
    _is_number,
    _is_whole,
    _nb_words,
    _plain_number,
    prepare_param,
)
from ._read import BASE_URL, read_data_gallicagram, tidy_gallicagram

_APOSTROPHE_MESSAGE = (
    "'keyword' cannot contain an apostrophe. Specifying a keyword without the "
    "apostrophe will also return words associated with the apostrophe version "
    "of the keyword."
)
_LEXICON_MESSAGE = "'lexicon' must be a character vector."
_N_RESULTS_MESSAGE = "'n_results' should be a positive whole number or 'all'"
_ONE_WORD_MESSAGE = (
    "{} is only available for keywords made of one word: the API returns no "
    "results for longer keywords"
)
_ALL_RESULTS = 10000001

Year = Union[int, str]


def _elias(corpus: str) -> str:
    return "&elias=true" if _corpus_info(corpus)["alt_base"] else ""


def _check_n_results(n_results: Any) -> None:
    if isinstance(n_results, str) and n_results == "all":
        return
    if not _is_whole(n_results) or n_results < 1:
        raise ValueError(_N_RESULTS_MESSAGE)


def _as_lexicon(lexicon: Any) -> List[str]:
    """Turns a lexicon into a list of different keywords.

    The API ignores the case, so that "Camarade" and "camarade" are one keyword,
    which would otherwise be counted twice in the sums of the lexicon functions.
    """
    keywords = _as_strings(lexicon, _LEXICON_MESSAGE)
    if not keywords:
        raise ValueError(_LEXICON_MESSAGE)
    first_forms: Dict[str, str] = {}
    for keyword in keywords:
        first_forms.setdefault(keyword.lower(), keyword)
    return list(first_forms.values())


def _bind(outputs: List[pd.DataFrame]) -> pd.DataFrame:
    """Binds data frames by rows. Those without results do not affect the types."""
    filled = [output for output in outputs if not output.empty]
    return pd.concat(filled or outputs[:1], ignore_index=True)


def _check_length(keyword: str, corpus: str, length: Any) -> None:
    if not _is_number(length):
        raise ValueError("'length' should be numeric")

    if not _is_whole(length):
        raise ValueError("'length' should be a whole number")

    max_length_corpus = int(_corpus_info(corpus)["max_length"])
    if length > max_length_corpus:
        raise ValueError(
            f"'length' cannot be more than {max_length_corpus} for this corpus"
        )

    if length < _nb_words(keyword):
        raise ValueError(
            "'length' has to be larger than the number of words in 'keyword'"
        )


def _sum_by(output: pd.DataFrame, by: str, column: str) -> pd.Series:
    # skipna=False: as in R, a sum with a missing value is missing
    return output.groupby(by, dropna=False)[column].transform(
        lambda values: values.sum(skipna=False)
    )


def gallicagram(
    keyword: str,
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    resolution: str = "monthly",
    n_of: str = "grams",
    subcorpora: Union[str, Sequence[str], None] = None,
) -> pd.DataFrame:
    """Occurrences of a keyword in a Gallicagram corpus.

    Retrieves the proportion of occurrences of a keyword in one of the corpora
    by year, month or day.

    This function corresponds to the `query_ngram` route of the API or, for
    `n_of="articles"` and for the persee and cairn corpora, to the
    `query_article`, `query_persee` and `query_cairn` routes.

    Information regarding available characteristics of the corpus can be found
    in the `list_corpora` dataset.

    Parameters
    ----------
    keyword : str
        Keyword to search. The string cannot contain more words than the
        `max_length` for this corpus, as indicated in the `list_corpora`
        dataset. "*" is a wildcard that can be used at the end of words and
        will represent any set of letters, e.g. "ecolo*" will return the counts
        for all words starting with "ecolo".
    corpus : str, default "lemonde"
        The corpus to search. The list of available corpora can be found in the
        `list_corpora` dataset.
    from_ : int or "earliest", default "earliest"
        The starting year. If set to "earliest", it uses the earliest date at
        which the data is reliable for this corpus, as described in
        `list_corpora`. It is called `from` in rallicagram but `from` is a
        reserved word in Python.
    to : int or "latest", default "latest"
        The end year. If set to "latest", it uses the latest date at which the
        data is reliable for this corpus, as described in `list_corpora`.
    resolution : str, default "monthly"
        Can only be "daily", "monthly" or "yearly". The finest available resolution for the corpus selected can be found in
        the `resolution` column of the `list_corpora` dataset.
    n_of : str, default "grams"
        Either "grams" or "articles". The type of object to compute the number of occurrences for. If set to
        "grams", the function will compute the number of "grams" that correspond
        to the keyword for the given period. If set to "articles" (only available
        for lemonde and for unigrams, ie for keywords only made of one word),
        will compute the number of articles that contain the keyword for the
        given period.
    subcorpora : str or list of str, default None
        The subcorpora to consider. Only available for `corpus="persee"` and
        `corpus="cairn"`. The list of available subcorpora can be found in the
        `list_subcorpora` dataset. Their codes are specific to each corpus.

    Returns
    -------
    pandas.DataFrame
        With the `date` at the beginning of the period of a given observation,
        the `keyword`, the number of occurrences (`n_occur`), the total number
        of ngrams or articles over the period (`n_total`), the proportion of
        occurrences of the keyword over the period of a given observation
        (`prop_occur`), the `year` and potentially the `month` and `day` of the
        observation, the `corpus`, the `resolution` and whether the total number
        is a number of grams or articles (`n_of`).

    Examples
    --------
    >>> gallicagram("président")
    >>> gallicagram("république", corpus="cairn", from_=2010, to=2020, resolution="yearly", subcorpora=["ARSS", "ACO"])
    """
    param_clean = prepare_param(
        keyword, corpus, from_, to, resolution, n_of, subcorpora
    )

    if n_of == "articles" and _nb_words(keyword) > 1:
        # The API does not fail: it silently returns 0 articles
        warnings.warn(_ONE_WORD_MESSAGE.format("n_of = 'articles'"), stacklevel=2)

    if n_of == "articles" and param_clean["corpus"] == "lemonde":
        route = "query_article"
    elif param_clean["corpus"] == "persee":
        route = "query_persee"
    elif param_clean["corpus"] == "cairn":
        route = "query_cairn"
    else:
        route = "query_ngram"

    url = (
        f"{BASE_URL}{route}"
        f"?corpus={param_clean['corpus']}"
        f"&mot={param_clean['keyword']}"
        f"&from={param_clean['from']}"
        f"&to={param_clean['to']}"
        f"&resolution={param_clean['resolution_fr']}"
    )
    if param_clean["subcorpora"] != "":
        url += f"&revue={param_clean['subcorpora']}"
    url += _elias(param_clean["corpus"])

    output = tidy_gallicagram(
        url, param_clean["corpus"], param_clean["resolution_en"]
    ).rename(columns={"n": "n_occur", "total": "n_total", "prop": "prop_occur"})
    output["n_of"] = f"{_nb_words(keyword)}-grams" if n_of == "grams" else "articles"

    return output


def gallicagram_all(keyword: str) -> pd.DataFrame:
    """Occurrences of a keyword in all Gallicagram corpora.

    Retrieves the yearly proportion of occurrences of a keyword in the lemonde,
    books and press corpora, for the longest time range possible.

    As in rallicagram, the periods searched are 1944-2023 for lemonde, 1789-1949
    for press and 1000-1939 for books. They therefore go beyond the reliable
    periods of the lemonde and books corpora, which raises the corresponding
    warnings.

    Parameters
    ----------
    keyword : str
        Keyword to search. See `gallicagram`.

    Returns
    -------
    pandas.DataFrame
        See `gallicagram`.

    Examples
    --------
    >>> gallicagram_all("président")
    """
    return _bind(
        [
            gallicagram(
                keyword, corpus="lemonde", from_=1944, to=2023, resolution="yearly"
            ),
            gallicagram(
                keyword, corpus="press", from_=1789, to=1949, resolution="yearly"
            ),
            gallicagram(
                keyword, corpus="books", from_=1000, to=1939, resolution="yearly"
            ),
        ]
    )


def gallicagram_lexicon(
    lexicon: Union[str, Iterable[str]],
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    resolution: str = "monthly",
) -> pd.DataFrame:
    """Occurrences of a list of keywords in a Gallicagram corpus.

    Retrieves the proportion of occurrences of a list of keywords in one of the
    corpora by year, month or day.

    This function sums the outputs of calls of `gallicagram` obtained for each
    keyword in the list.

    Can typically be used with the function `get_same_stem`.

    If the keywords do not all have the same number of words, their totals
    differ: the output then has one row per date and number of words, each with
    the same sum of occurrences but its own `n_total` and `prop_occur`.

    A keyword present several times in the list, whatever its case, is counted
    once.

    Parameters
    ----------
    lexicon : list of str
        Keywords to search. Can contain up to the `max_length` of the corpus, as
        indicated in the `list_corpora` dataset.
    corpus : str, default "lemonde"
        The corpus to search. See `gallicagram`.
    from_ : int or "earliest", default "earliest"
        The starting year. See `gallicagram`.
    to : int or "latest", default "latest"
        The end year. See `gallicagram`.
    resolution : str, default "monthly"
        Can only be "daily", "monthly" or "yearly". See `gallicagram`.

    Returns
    -------
    pandas.DataFrame
        With the `date` at the beginning of the period of a given observation,
        the first `keyword` in the list, typically the main one, the number of
        occurrences (`n_occur`), the total number of ngrams over the period of a
        given observation (`n_total`), the proportion of occurrences of the
        keywords over this period (`prop_occur`), the `year` and potentially the
        `month` and `day` of the observation, the `corpus`, the `resolution`,
        `n_of` and the entire `lexicon`.

    Examples
    --------
    >>> gallicagram_lexicon(["président", "présidentiel"])
    """
    # to check for errors
    prepare_param("a", corpus, from_, to, resolution)
    keywords = _as_lexicon(lexicon)

    output = _bind(
        [gallicagram(keyword, corpus, from_, to, resolution) for keyword in keywords]
    )
    output["keyword"] = keywords[0]
    output["n_occur"] = _sum_by(output, "date", "n_occur")
    output["prop_occur"] = output["n_occur"] / output["n_total"]
    output = output.drop_duplicates().reset_index(drop=True)
    output["lexicon"] = "+".join(keywords)

    return output


def gallicagram_cooccur(
    keyword_1: str,
    keyword_2: str,
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    resolution: str = "monthly",
    count_phrase: bool = False,
    cooccur_level: str = "grams",
) -> pd.DataFrame:
    """Close co-occurrences of two keywords in a Gallicagram corpus.

    Retrieves the proportion of close co-occurrences of two keywords in a
    corpus by year or month.

    Close co-occurrences correspond to the number of 3-grams (4-grams in the
    Le Monde corpus) that contain the two keywords.

    This function is only available for the corpora for which the
    `available_func` column of the `list_corpora` dataset contains "cooccurr".

    It corresponds to the `contain` route of the API or, for
    `cooccur_level="articles"`, to the `cooccur` route.

    Parameters
    ----------
    keyword_1 : str
        One of the two keywords to search.
    keyword_2 : str
        The other keyword to search.
    corpus : str, default "lemonde"
        The corpus to search. See `gallicagram`.
    from_ : int or "earliest", default "earliest"
        The starting year. See `gallicagram`.
    to : int or "latest", default "latest"
        The end year. See `gallicagram`.
    resolution : str, default "monthly"
        For press and lemonde can be either "yearly" or "monthly". For books can
        only be "yearly".
    count_phrase : bool, default False
        If True, counts the co-occurrences of each phrase containing both
        keywords. If False, returns the number of times both keywords co-occur
        in each resolution period.
    cooccur_level : str, default "grams"
        Either "grams" or "articles". The level at which to look for co-occurrences of the two keywords: in
        3-grams for "livres" and "presse" and in 4-grams or articles for
        "lemonde".

    Returns
    -------
    pandas.DataFrame
        With the `date` at the beginning of the period of a given observation,
        `keyword_1`, `keyword_2`, the phrase (`gram`, only if `count_phrase` is
        True), the number of co-occurrences (`n_cooccur`), the total number of
        ngrams or articles over the period (`n_total`), the proportion of
        co-occurrences over the period of a given observation (`prop_cooccur`),
        the `year` and potentially the `month` of the observation, the `corpus`,
        the `resolution` and the syntagma at which the co-occurrences are
        computed (`cooccur_level`).

    Examples
    --------
    >>> gallicagram_cooccur("président", "mauvais", corpus="press")
    """
    param_clean = prepare_param(
        keyword_1, corpus, from_, to, resolution, cooccur_level, func_type="cooccur"
    )
    param_clean_2 = prepare_param(
        keyword_2, corpus, from_, to, resolution, cooccur_level, func_type="cooccur"
    )

    route = (
        "cooccur"
        if cooccur_level == "articles" and param_clean["corpus"] == "lemonde"
        else "contain"
    )
    url = (
        f"{BASE_URL}{route}"
        f"?corpus={param_clean['corpus']}"
        f"&mot1={param_clean['keyword']}"
        f"&mot2={param_clean_2['keyword']}"
        f"&from={param_clean['from']}"
        f"&to={param_clean['to']}"
        f"&resolution={param_clean['resolution_fr']}"
        f"&count={'False' if count_phrase else 'True'}"  # opposite to API
    )

    output = tidy_gallicagram(
        url, param_clean["corpus"], param_clean["resolution_en"]
    ).rename(
        columns={
            "keyword": "gram",
            "n": "n_cooccur",
            "total": "n_total",
            "prop": "prop_cooccur",
        }
    )
    output["keyword_1"] = keyword_1
    output["keyword_2"] = keyword_2
    if cooccur_level == "articles":
        output["cooccur_level"] = "articles"
    elif param_clean["corpus"] == "lemonde":
        output["cooccur_level"] = "4-grams"
    else:
        output["cooccur_level"] = "3-grams"
    output["gram"] = output["gram"].where(output["gram"] != "")

    first = ["date", "keyword_1", "keyword_2"]
    output = output[first + [name for name in output.columns if name not in first]]

    # gram = keyword_1&keyword_2 when count_phrase = False so redundant
    if not count_phrase:
        output = output.drop(columns="gram")

    return output


def gallicagram_cooccur_lexicon(
    lexicon_1: Union[str, Iterable[str]],
    lexicon_2: Union[str, Iterable[str]],
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    resolution: str = "monthly",
    cooccur_level: str = "grams",
) -> pd.DataFrame:
    """Close co-occurrences of two lexicons in a Gallicagram corpus.

    Retrieves the proportion of close co-occurrences of two lexicons in a corpus
    by year or month.

    Close co-occurrences correspond to the number of 3-grams (4-grams in the
    Le Monde corpus) that contain each pair of keywords in the two lexicons.

    This function simply loops the function `gallicagram_cooccur` over each word
    of each lexicon and sums the results. It can thus take some time to run.

    It is only available for the corpora for which the `available_func` column
    of the `list_corpora` dataset contains "cooccurr".

    Parameters
    ----------
    lexicon_1 : list of str
        One of the two lexicons to search.
    lexicon_2 : list of str
        The other lexicon to search.
    corpus : str, default "lemonde"
        The corpus to search. See `gallicagram`.
    from_ : int or "earliest", default "earliest"
        The starting year. See `gallicagram`.
    to : int or "latest", default "latest"
        The end year. See `gallicagram`.
    resolution : str, default "monthly"
        Can be either "yearly" or "monthly". See `gallicagram_cooccur`.
    cooccur_level : str, default "grams"
        Either "grams" or "articles". See `gallicagram_cooccur`.

    Returns
    -------
    pandas.DataFrame
        With the `date` at the beginning of the period of a given observation,
        the number of co-occurrences (`n_cooccur`), the total number of ngrams or
        articles over the period (`n_total`), the proportion of co-occurrences
        (`prop_cooccur`), the `year` and potentially the `month` of the
        observation, the `corpus`, the `resolution`, `cooccur_level`, the first
        keyword of each lexicon (`keyword_1`, `keyword_2`) and the entire
        lexicons (`lexicon_1`, `lexicon_2`).

    Examples
    --------
    >>> gallicagram_cooccur_lexicon(["président", "présidente"], ["mauvais", "nul"], corpus="press")
    """
    keywords_1 = _as_lexicon(lexicon_1)
    keywords_2 = _as_lexicon(lexicon_2)

    output = _bind(
        [
            gallicagram_cooccur(
                keyword_1,
                keyword_2,
                corpus,
                from_,
                to,
                resolution,
                count_phrase=False,
                cooccur_level=cooccur_level,
            )
            for keyword_1 in keywords_1
            for keyword_2 in keywords_2
        ]
    )
    output["n_cooccur"] = _sum_by(output, "date", "n_cooccur")
    output["prop_cooccur"] = output["n_cooccur"] / output["n_total"]
    output = (
        output.drop(columns=["keyword_1", "keyword_2"])
        .drop_duplicates()
        .reset_index(drop=True)
    )
    output["keyword_1"] = keywords_1[0]
    output["keyword_2"] = keywords_2[0]
    output["lexicon_1"] = "+".join(keywords_1)
    output["lexicon_2"] = "+".join(keywords_2)

    return output


def gallicagram_associated(
    keyword: str,
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    n_results: Union[int, str] = 20,
    distance: Union[int, str] = "max",
    stopwords: Union[str, Iterable[str], None] = "default",
    remove_numbers: bool = True,
) -> pd.DataFrame:
    """Words the most often associated with a keyword in a Gallicagram corpus.

    Returns the words the most frequently at a given number of words (`distance`)
    from the keyword.

    This function calls the `associated_ngram` route of the API or, for
    `distance="articles"`, the `associated_article` route.

    This function is only available for the corpora for which the
    `available_func` column of the `list_corpora` dataset contains "associated".
    Searching the "press" corpus can take a long time and return an error. If it
    does, run the same function again, it will start off where it stopped.

    Note that the API route does not allow to search for associated words after a
    punctuation mark. For instance, in "son camarade, le chasseur, a", the
    function will not count "chasseur" as a word associated with "camarade". The
    ngram "son camarade le chasseur" is not in the database. Thus, there might be
    less associated words at a longer distance as it increases the probability of
    ngrams to be excluded from the database.

    Apostrophes and letters preceding them are withdrawn from the dataset (except
    for n' since they carry meaning).

    Parameters
    ----------
    keyword : str
        Keyword to search. Cannot contain an apostrophe. See `gallicagram`.
    corpus : str, default "lemonde"
        The corpus to search. See `gallicagram`.
    from_ : int or "earliest", default "earliest"
        The starting year. See `gallicagram`.
    to : int or "latest", default "latest"
        The end year. See `gallicagram`.
    n_results : int or "all", default 20
        The number of most frequently associated words to return. Can also be set
        to "all" to return all the available results.
    distance : int or str, default "max"
        An integer, "max" or "articles". The maximum distance, in number of words, at which to look for words
        associated with the keyword. The max length for each corpus (distance +
        number of words in the keyword) is described in the `max_length` column of
        the `list_corpora` dataset.

        When set to "max", automatically considers the longest ngram possible for
        this corpus.

        When set to "articles", looks for associated words within the whole
        article. Only available for the "lemonde" corpus and for unigrams (ie
        keywords only made of one word).
    stopwords : list of str, "default" or None, default "default"
        The stopwords to remove. "default" is the list of the 500 most frequent
        words in the Gallica books dataset, ie `stopwords_gallica[:500]`. This
        number can be changed by passing for instance `stopwords_gallica[:300]`
        for the 300 most frequent words. If None, does not remove any stopwords.
    remove_numbers : bool, default True
        If True, removes numbers from the list of associated words.

    Returns
    -------
    pandas.DataFrame
        Containing the words the most frequently associated with the `keyword`
        mentioned (`associated_word`), the number of co-occurrences between the
        keyword and the associated word over the period (`n_cooccur`), the input
        parameters `keyword`, `corpus`, `from` and `to`, and the level at which
        the co-occurrences are computed (n-grams or articles, `cooccur_level`).

    Examples
    --------
    >>> gallicagram_associated("camarade", from_=1960, to=1970)
    """
    param_clean = prepare_param(
        keyword, corpus, from_, to, resolution="yearly", func_type="associated"
    )
    # param resolution not used

    # errors handling 1
    is_keyword_distance = isinstance(distance, str) and distance in ("max", "articles")
    if not (_is_number(distance) or is_keyword_distance):
        raise ValueError(
            "'distance' should be numeric, 'max' or 'articles' (for lemonde only)"
        )

    if distance == "articles" and param_clean["corpus"] != "lemonde":
        raise ValueError(
            "'distance' can only be set to 'articles' for the lemonde corpus"
        )

    if not is_keyword_distance and distance <= 0:
        raise ValueError("'distance' has to be larger than 0")

    if not is_keyword_distance and not _is_whole(distance):
        raise ValueError("'distance' should be a whole number")

    _check_n_results(n_results)

    # compute length
    max_length_corpus = int(_corpus_info(param_clean["corpus"])["max_length"])
    nb_words = _nb_words(keyword)
    asked_length = (
        max_length_corpus if is_keyword_distance else nb_words + _plain_number(distance)
    )
    length = min(max_length_corpus, asked_length)

    stopwords_list = _stopwords_list(stopwords)
    if stopwords_list is not None:
        n_joker: Union[int, str] = "all"
    elif n_results == "all":
        n_joker = "all"
    else:
        n_joker = _plain_number(n_results) + nb_words

    # errors handling 2
    if asked_length > max_length_corpus:
        warnings.warn(
            "Distance set to 'max'. The sum of the number of words in 'keyword' "
            f"and 'distance' cannot be more than {max_length_corpus} for this "
            "corpus.",
            stacklevel=2,
        )

    if "'" in keyword:
        raise ValueError(_APOSTROPHE_MESSAGE)

    if distance == "articles" and nb_words > 1:
        warnings.warn(_ONE_WORD_MESSAGE.format("distance = 'articles'"), stacklevel=2)

    route = "associated_article" if distance == "articles" else "associated_ngram"
    url = (
        f"{BASE_URL}{route}"
        f"?corpus={param_clean['corpus']}"
        f"&mot={param_clean['keyword']}"
        f"&from={param_clean['from']}"
        f"&to={param_clean['to']}"
        f"&n_joker={n_joker}"
        f"&length={length}"
        f"{_elias(param_clean['corpus'])}"
    )

    raw = read_data_gallicagram(url)
    # remove apostrophes (except for n' since they carry meaning)
    raw["associated_word"] = [
        re.sub(r"^[a-mo-z]'", "", gram, count=1) for gram in raw["gram"]
    ]
    keyword_words = re.split(r"[\s+]", param_clean["keyword_plain"])
    raw = raw.loc[~raw["associated_word"].isin(keyword_words)]

    # groupby sorts the words so that the ties are in alphabetical order
    output = (
        raw.groupby("associated_word", as_index=False)
        .agg(n_cooccur=("tot", "sum"))
        .sort_values("n_cooccur", ascending=False, kind="stable")
    )

    # add param
    output["keyword"] = param_clean["keyword_plain"]
    output["corpus"] = param_clean["corpus"]
    output["from"] = param_clean["from"]
    output["to"] = param_clean["to"]
    output["cooccur_level"] = (
        "articles" if distance == "articles" else f"{length}-grams"
    )

    if remove_numbers:
        has_number = [
            re.search("[0-9]", word) is not None for word in output["associated_word"]
        ]
        output = output.loc[~pd.Series(has_number, index=output.index, dtype=bool)]

    # remove stopwords
    if stopwords_list is not None:
        output = output.loc[~output["associated_word"].isin(stopwords_list)]

    # these "" were created because some associated_word
    # returned are in the format \w'
    output = output.loc[output["associated_word"] != ""]

    if n_results != "all":
        output = output.head(int(n_results))

    return output.reset_index(drop=True)


def _stopwords_list(stopwords: Union[str, Iterable[str], None]) -> Optional[List[str]]:
    if stopwords is None:
        return None
    if isinstance(stopwords, str) and stopwords == "default":
        return list(_stopwords()[:500])
    return _as_strings(stopwords, "'stopwords' must be a character vector.")


def gallicagram_associated_lexicon(
    lexicon: Union[str, Iterable[str]],
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    n_results: Union[int, str] = 20,
    distance: Union[int, str] = "max",
    stopwords: Union[str, Iterable[str], None] = "default",
) -> pd.DataFrame:
    """Words the most often associated with a list of keywords in a Gallicagram corpus.

    Returns the words the most frequently at a given number of words (`distance`)
    from any of the keywords in the list.

    This function sums the outputs of calls of `gallicagram_associated` obtained
    for each keyword in the list. A keyword present several times in the list,
    whatever its case, is counted once. Each word appears once in the output: if
    the keywords do not have the same number of words, `cooccur_level` lists all
    the levels searched.

    Can typically be used with the function `get_same_stem`.

    This function is only available for the corpora for which the
    `available_func` column of the `list_corpora` dataset contains "associated".

    Parameters
    ----------
    lexicon : list of str
        Keywords to search.
    corpus : str, default "lemonde"
        The corpus to search. See `gallicagram`.
    from_ : int or "earliest", default "earliest"
        The starting year. See `gallicagram`.
    to : int or "latest", default "latest"
        The end year. See `gallicagram`.
    n_results : int or "all", default 20
        The number of most frequently associated words to return. See
        `gallicagram_associated`.
    distance : int or str, default "max"
        An integer, "max" or "articles". See `gallicagram_associated`.
    stopwords : list of str, "default" or None, default "default"
        The stopwords to remove. See `gallicagram_associated`.

    Returns
    -------
    pandas.DataFrame
        With the words the most frequently associated with any of the keywords in
        the `lexicon` mentioned (`associated_word`), the number of co-occurrences
        between the keywords and the associated word over the period
        (`n_cooccur`), the first `keyword` in this lexicon, typically the main
        one, the input parameters `corpus`, `from` and `to`, the level at which
        the co-occurrences are computed (`cooccur_level`) and the entire
        `lexicon`.

    Examples
    --------
    >>> gallicagram_associated_lexicon(["président", "présidentiel"])
    """
    # to check for errors
    prepare_param("a", corpus, from_, to, "yearly", func_type="associated")
    keywords = _as_lexicon(lexicon)
    _check_n_results(n_results)

    output = _bind(
        [
            gallicagram_associated(
                keyword,
                corpus,
                from_,
                to,
                n_results=_ALL_RESULTS,
                distance=distance,
                stopwords=stopwords,
            )
            for keyword in keywords
        ]
    )
    output["keyword"] = keywords[0]
    output["n_cooccur"] = _sum_by(output, "associated_word", "n_cooccur")
    # Otherwise, a word found at two levels would remain on two rows
    output["cooccur_level"] = ", ".join(output["cooccur_level"].unique())
    output = output.drop_duplicates().sort_values(
        "n_cooccur", ascending=False, kind="stable"
    )
    output["lexicon"] = "+".join(keywords)

    if n_results != "all":
        output = output.head(int(n_results))

    return output.reset_index(drop=True)


def gallicagram_with(
    keyword: str,
    corpus: str = "lemonde",
    from_: Year = "earliest",
    to: Year = "latest",
    n_results: Union[int, str] = 20,
    length: int = 2,
) -> pd.DataFrame:
    """ngrams that most frequently contain a keyword in a Gallicagram corpus over a period.

    Returns the most frequent ngrams containing a keyword over a given period.

    This function is only available for the corpora for which the
    `available_func` column of the `list_corpora` dataset contains "with".

    This function corresponds to the `joker_ngram` route of the API, accessed
    through the 'Joker' function on the Gallicagram app. When length = 1, it is
    analogous to the 'Joker' function on Ngram Viewer.

    It is analogous to `gallicagram_with_month` but for a period instead of a
    given month.

    For instance "camarade" is often followed by "staline" or "khrouchtchev" in
    Le Monde. The function returns the most frequent ngrams of the form
    "camarade _" where "_" is a placeholder for any ngram of length up to
    `length`. When no placeholder is specified, it is assumed that one is located
    after keyword. The placeholder can be located within phrases. For example,
    "le _ staline".

    The running time for the "presse" corpus can be long.

    Parameters
    ----------
    keyword : str
        Keyword to search. Cannot contain an apostrophe. See `gallicagram`.
    corpus : str, default "lemonde"
        The corpus to search. See `gallicagram`.
    from_ : int or "earliest", default "earliest"
        The starting year. See `gallicagram`.
    to : int or "latest", default "latest"
        The end year. See `gallicagram`.
    n_results : int or "all", default 20
        The number of most frequent ngrams to return. Can also be set to "all" to
        return all the available results.
    length : int, default 2
        The length of the ngrams considered. Its maximum for each corpus is
        described in the `max_length` column of the `list_corpora` dataset.

    Returns
    -------
    pandas.DataFrame
        With the number of occurrences over the period (`n_occur`) and the
        `n_results` most frequent ngrams containing the `keyword` searched
        (`ngram`). It also returns the input parameters `keyword`, `corpus`,
        `from` and `to`.

    Examples
    --------
    >>> gallicagram_with("camarade", from_=1960, to=1970)
    """
    param_clean = prepare_param(
        keyword, corpus, from_, to, resolution="yearly", func_type="with"
    )
    # param resolution not used

    # errors handling
    _check_length(keyword, param_clean["corpus"], length)
    _check_n_results(n_results)
    if "'" in keyword:
        raise ValueError(_APOSTROPHE_MESSAGE)

    url = (
        f"{BASE_URL}joker_ngram"
        f"?corpus={param_clean['corpus']}"
        f"&mot={param_clean['keyword']}"
        f"&from={param_clean['from']}"
        f"&to={param_clean['to']}"
        f"&n_joker={_plain_number(n_results)}"
        f"&length={_plain_number(length)}"
        f"{_elias(param_clean['corpus'])}"
    )

    output = read_data_gallicagram(url).rename(
        columns={"tot": "n_occur", "gram": "ngram"}
    )
    output["keyword"] = param_clean["keyword_plain"]
    output["corpus"] = param_clean["corpus"]
    output["from"] = param_clean["from"]
    output["to"] = param_clean["to"]

    return output


def gallicagram_with_month(
    keyword: str,
    corpus: str = "lemonde",
    year: int = 2022,
    month: int = 1,
    n_results: Union[int, str] = 20,
    length: int = 2,
) -> pd.DataFrame:
    """ngrams that most frequently contain a keyword in a Gallicagram corpus for a specific month.

    Returns the most frequent ngrams containing a keyword for a given month.

    This function is only available for the corpora for which the
    `available_func` column of the `list_corpora` dataset contains "with".

    This function corresponds to the `joker_mois` route of the API. At the time of
    writing, the API only answers this route for the lemonde and presse corpora,
    and returns an HTTP error for the other ones that were tried.

    It is analogous to `gallicagram_with` but for a precise month instead of a
    given period.

    For instance "camarade" is often followed by "staline" or "khrouchtchev" in
    Le Monde. The function returns the most frequent ngrams of the form
    "camarade _".

    Searching the "press" corpus can require a long running time.

    Parameters
    ----------
    keyword : str
        Keyword to search. Cannot contain an apostrophe. See `gallicagram`.
    corpus : str, default "lemonde"
        See `gallicagram`.
    year : int, default 2022
        The year of interest.
    month : int, default 1
        The month of the `year` of interest.
    n_results : int or "all", default 20
        The number of most frequent ngrams to return. See `gallicagram_with`.
    length : int, default 2
        The length of the ngrams considered. See `gallicagram_with`.

    Returns
    -------
    pandas.DataFrame
        With the number of occurrences over the period (`n_occur`) and the
        `n_results` most frequent ngrams containing the `keyword` searched
        (`ngram`). It also returns the input parameters `keyword`, `corpus`,
        `year` and `month`.

    Examples
    --------
    >>> gallicagram_with_month("camarade")
    """
    param_clean = prepare_param(
        keyword, corpus, year, year, resolution="yearly", func_type="with"
    )
    # param resolution not used

    # errors handling
    _check_length(keyword, param_clean["corpus"], length)
    _check_n_results(n_results)

    if not _is_number(month):
        raise ValueError("'year' and 'month' should be numeric")

    if not _is_whole(month) or not 1 <= month <= 12:
        raise ValueError("'month' should be a whole number between 1 and 12")

    if "'" in keyword:
        raise ValueError(_APOSTROPHE_MESSAGE)

    url = (
        f"{BASE_URL}joker_mois"
        f"?corpus={param_clean['corpus']}"
        f"&mot={param_clean['keyword']}"
        f"&year={_plain_number(year)}"
        f"&month={_plain_number(month)}"
        f"&n_joker={_plain_number(n_results)}"
        f"&length={_plain_number(length)}"
        f"{_elias(param_clean['corpus'])}"
    )

    output = read_data_gallicagram(url).rename(
        columns={"tot": "n_occur", "gram": "ngram"}
    )
    output["keyword"] = param_clean["keyword_plain"]
    output["corpus"] = param_clean["corpus"]
    output["year"] = _plain_number(year)
    output["month"] = _plain_number(month)

    return output


def get_same_stem(keyword: str) -> List[str]:
    """Finds words with the same stem as a keyword.

    Searches such words in the `word_lemma_stem` data frame.

    A word appears only once in the output, even if it has several entries in
    `word_lemma_stem`. Otherwise, passing the output to one of the `_lexicon`
    functions would count its occurrences several times.

    Parameters
    ----------
    keyword : str
        The keyword.

    Returns
    -------
    list of str
        Words with the same stem as the `keyword`.

    Raises
    ------
    ValueError
        If the keyword is not in the dataset.

    Examples
    --------
    >>> get_same_stem("président")
    """
    wls = _word_lemma_stem()
    matches = wls.loc[wls["word"] == keyword, "stem"]
    if matches.empty:
        raise ValueError("Keyword not in the dataset")

    stem = matches.iloc[0]
    return list(dict.fromkeys(wls.loc[wls["stem"] == stem, "word"]))
