"""The functions drawing graphs, based on plotnine, the Python port of ggplot2."""

from __future__ import annotations

from typing import Any, Iterable, List, Optional

import pandas as pd

from ._data import _corpora


def _plotnine():
    try:
        import plotnine
    except ImportError as error:
        raise ImportError(
            "The graph functions require plotnine. Install it with: "
            "pip install 'pyllicagram[graph]'"
        ) from error
    return plotnine


def _corpus_names(data: pd.DataFrame) -> List[str]:
    corpora = _corpora()
    return list(corpora.loc[corpora["corpus"].isin(data["corpus"]), "corpus_name"])


def _unique(column: pd.Series) -> str:
    return ", ".join(str(value) for value in column.unique())


def _keywords(data: pd.DataFrame) -> str:
    return '", "'.join(str(value) for value in data["keyword"].unique())


def _date_labels(breaks: Iterable[Any]) -> List[str]:
    """Shows 2005 rather than 2005-01-01, as ggplot2 does for yearly breaks."""
    dates = [pd.Timestamp(value).to_pydatetime() for value in breaks]
    if all((date.month, date.day) == (1, 1) for date in dates):
        return [str(date.year) for date in dates]
    if all(date.day == 1 for date in dates):
        return [f"{date.year}-{date.month:02d}" for date in dates]
    return [f"{date.year}-{date.month:02d}-{date.day:02d}" for date in dates]


def _mapping(p9: Any, y: str, color: Optional[str]) -> Any:
    if color is None:
        return p9.aes(x="date", y=y)
    return p9.aes(x="date", y=y, color=color)


def gallicagraph_occur(data: pd.DataFrame, color: Optional[str] = None) -> Any:
    """Graph describing the evolution of the proportion of occurrences.

    Takes as input data produced by `gallicagram` or `gallicagram_lexicon` and
    produces a graph describing the evolution of the proportion of occurrences in
    this data set.

    This function can also be combined with faceting by adding for instance
    `+ facet_wrap("keyword")` after calling the function.

    Parameters
    ----------
    data : pandas.DataFrame
        A data frame produced by the `gallicagram` or `gallicagram_lexicon`
        functions (or several of such data frames bound by rows).
    color : str, default None
        The name of a column of `data` to set colors for the graph.

    Returns
    -------
    plotnine.ggplot
        A graph describing the evolution of the proportion of occurrences of one
        or several keywords in one or several corpora.

    Examples
    --------
    >>> import pandas as pd
    >>> import plotnine
    >>> gallicagraph_occur(gallicagram("président"))
    >>> both = pd.concat([gallicagram("président"), gallicagram("république")])
    >>> gallicagraph_occur(both, color="keyword")
    >>> gallicagraph_occur(both) + plotnine.facet_wrap("keyword")
    >>> corpora = pd.concat([gallicagram("président"), gallicagram("président", corpus="huma")])
    >>> gallicagraph_occur(corpora, color="corpus")
    """
    p9 = _plotnine()
    corpus_names = _corpus_names(data)
    is_lexicon = "lexicon" in data.columns

    title = (
        f"Evolution of the {_unique(data['resolution'])} coverage of"
        + (' the "' if is_lexicon else ' "')
        + _keywords(data)
        + ('" lexicon' if is_lexicon else '"')
    )
    subtitle = (
        f"In the {', '.join(corpus_names)} "
        + ("corpus" if len(corpus_names) == 1 else "corpora")
    )

    return (
        p9.ggplot(data, _mapping(p9, "prop_occur", color))
        + p9.geom_line()
        + p9.scale_x_datetime(labels=_date_labels)
        + p9.labs(
            x="",
            y=f"Proportion (of {_unique(data['n_of'])} in the corpus)",
            title=title,
            subtitle=subtitle,
        )
        + p9.theme(panel_background=p9.element_blank())
    )


def gallicagraph_cooccur(data: pd.DataFrame, color: Optional[str] = None) -> Any:
    """Graph describing the evolution of the proportion of co-occurrences.

    Takes as input data produced by `gallicagram_cooccur` or
    `gallicagram_cooccur_lexicon` and produces a graph describing the evolution of
    the proportion of co-occurrences in this data set.

    This function can also be combined with faceting by adding for instance
    `+ facet_wrap("keyword")` after calling the function. The `keyword` column,
    made of the two keywords, is created by this function.

    Parameters
    ----------
    data : pandas.DataFrame
        A data frame produced by the `gallicagram_cooccur` or
        `gallicagram_cooccur_lexicon` functions (or several of such data frames
        bound by rows).
    color : str, default None
        The name of a column of `data`, or "keyword", to set colors for the graph.

    Returns
    -------
    plotnine.ggplot
        A graph describing the evolution of the proportion of co-occurrences of
        two keywords in one or several corpora.

    Examples
    --------
    >>> import pandas as pd
    >>> import plotnine
    >>> ancien = gallicagram_cooccur("président", "ancien", cooccur_level="articles")
    >>> gallicagraph_cooccur(ancien)
    >>> both = pd.concat([ancien, gallicagram_cooccur("président", "république", cooccur_level="articles")])
    >>> gallicagraph_cooccur(both, color="keyword")
    >>> gallicagraph_cooccur(both) + plotnine.facet_wrap("keyword")
    """
    p9 = _plotnine()
    corpus_names = _corpus_names(data)
    is_lexicon = "lexicon_1" in data.columns

    data_clean = data.copy()
    data_clean["keyword"] = (
        '"' + data_clean["keyword_1"] + '" and "' + data_clean["keyword_2"] + '"'
    )

    title = (
        "Evolution of co-occurrences of "
        + ("the " if is_lexicon else "")
        + _unique(data_clean["keyword"])
        + (" lexicons" if is_lexicon else "")
    )
    subtitle = (
        f"In {_unique(data_clean['cooccur_level'])} in the "
        f"{', '.join(corpus_names)} "
        + ("corpus" if len(corpus_names) == 1 else "corpora")
    )

    return (
        p9.ggplot(data_clean, _mapping(p9, "prop_cooccur", color))
        + p9.geom_line()
        + p9.scale_x_datetime(labels=_date_labels)
        + p9.labs(
            x="",
            y=f"Proportion (of {_unique(data['cooccur_level'])} in the corpus)",
            title=title,
            subtitle=subtitle,
        )
        + p9.theme(panel_background=p9.element_blank())
    )


def gallicagraph_associated(
    data: pd.DataFrame, labels_color: Optional[str] = None
) -> Any:
    """Graph describing the most common co-occurrences with a keyword or lexicon.

    Takes as input data produced by `gallicagram_associated` or
    `gallicagram_associated_lexicon` and produces a graph describing the words the
    most commonly co-occurring with the keyword or lexicon of interest.

    Parameters
    ----------
    data : pandas.DataFrame
        A data frame produced by the `gallicagram_associated` or
        `gallicagram_associated_lexicon` functions.
    labels_color : str, default None
        The color in which to print the labels. Set to None for no label.

    Returns
    -------
    plotnine.ggplot
        A graph describing the most common co-occurrences with a keyword or
        lexicon.

    Examples
    --------
    >>> gallicagraph_associated(gallicagram_associated("président", from_=2020), labels_color="white")
    """
    p9 = _plotnine()
    corpus_names = _corpus_names(data)
    is_lexicon = "lexicon" in data.columns

    # Equivalent of stats::reorder(associated_word, n_cooccur)
    levels = (
        data.groupby("associated_word")["n_cooccur"]
        .mean()
        .sort_values(kind="stable")
        .index
    )
    data_clean = data.copy()
    data_clean["associated_word"] = pd.Categorical(
        data_clean["associated_word"], categories=list(levels), ordered=True
    )

    title = (
        "Words most often co-occurring with"
        + (' the "' if is_lexicon else ' "')
        + _keywords(data)
        + ('" lexicon' if is_lexicon else '"')
    )
    subtitle = (
        f"In {_unique(data['cooccur_level'])} in the {', '.join(corpus_names)} "
        f"corpus, from {_unique(data['from'])} to {_unique(data['to'])}"
    )

    graph = (
        p9.ggplot(data_clean, p9.aes(x="associated_word", y="n_cooccur"))
        + p9.geom_col()
    )
    if labels_color is not None and not pd.isna(labels_color):
        graph = graph + p9.geom_text(
            p9.aes(label="n_cooccur"),
            color=labels_color,
            size=8,
            ha="right",
            nudge_y=-0.01 * data["n_cooccur"].max(),
        )

    return (
        graph
        + p9.labs(x="", y="Number of co-occurrences", title=title, subtitle=subtitle)
        + p9.coord_flip()
        + p9.theme(
            panel_background=p9.element_blank(),
            axis_ticks_major_y=p9.element_blank(),
            axis_ticks_minor_y=p9.element_blank(),
            panel_grid_major_y=p9.element_blank(),
        )
    )


def gallicagraph(
    data: pd.DataFrame,
    color: Optional[str] = None,
    labels_color: Optional[str] = None,
) -> Any:
    """Automatically produces the relevant graph.

    Takes as input data produced by one of the `gallicagram`,
    `gallicagram_cooccur` or `gallicagram_associated` functions or their lexicon
    counterparts and produces the corresponding base graph.

    This function can also be combined with faceting by adding for instance
    `+ facet_wrap("keyword")` after calling the function.

    Parameters
    ----------
    data : pandas.DataFrame
        A data frame produced by one of the `gallicagram`, `gallicagram_cooccur`
        or `gallicagram_associated` functions or their lexicon counterparts (or
        several of such data frames bound by rows).
    color : str, default None
        The name of a column of `data` to set colors for the graph. Only used for
        evolutions of (co-)occurrences.
    labels_color : str, default None
        The color in which to print the labels. Set to None for no label. Only
        used for associated words.

    Returns
    -------
    plotnine.ggplot
        A graph describing the evolution of the proportion of (co-)occurrences of
        one or several keywords in one or several corpora, or the words the most
        commonly associated with a keyword.

    Raises
    ------
    ValueError
        If the data has not been produced by pyllicagram.

    Examples
    --------
    >>> gallicagraph(gallicagram("président"))
    >>> gallicagraph(gallicagram_cooccur("président", "ancien", cooccur_level="articles"))
    >>> gallicagraph(gallicagram_associated("patate", from_=2020))
    """
    columns = getattr(data, "columns", ())
    if "n_occur" in columns and "prop_occur" in columns:
        return gallicagraph_occur(data, color)
    if "associated_word" in columns:
        return gallicagraph_associated(data, labels_color)
    if "n_cooccur" in columns:
        return gallicagraph_cooccur(data, color)
    raise ValueError("Only works for data produced by pyllicagram")
