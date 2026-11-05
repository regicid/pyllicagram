"""The graph functions, that have no test in rallicagram."""

import datetime

import pandas as pd
import pytest

plotnine = pytest.importorskip("plotnine")

from pyllicagram import (  # noqa: E402
    gallicagram,
    gallicagram_associated,
    gallicagram_associated_lexicon,
    gallicagram_cooccur,
    gallicagram_cooccur_lexicon,
    gallicagram_lexicon,
    gallicagram_with,
    gallicagraph,
    gallicagraph_associated,
    gallicagraph_cooccur,
    gallicagraph_occur,
)
from pyllicagram._graphs import _date_labels  # noqa: E402


def labels(graph):
    return graph.labels


def draw(graph, tmp_path):
    path = tmp_path / "graph.png"
    graph.save(path, width=5, height=4, dpi=72, verbose=False)
    assert path.stat().st_size > 0


def test_occur(tmp_path):
    data = gallicagram("obama", from_=2005, to=2005)
    graph = gallicagraph(data)
    assert labels(graph).title == 'Evolution of the monthly coverage of "obama"'
    assert labels(graph).subtitle == "In the Le Monde (rubriques) corpus"
    assert labels(graph).y == "Proportion (of 1-grams in the corpus)"
    draw(graph, tmp_path)


def test_occur_several(tmp_path):
    data = pd.concat(
        [gallicagram("a", from_=2005, to=2005), gallicagram("b", corpus="figaro", from_=1900, to=1900)]
    )
    graph = gallicagraph_occur(data, color="corpus")
    assert labels(graph).title == 'Evolution of the monthly coverage of "a", "b"'
    assert labels(graph).subtitle == "In the Le Monde (rubriques), Le Figaro corpora"
    draw(graph, tmp_path)
    draw(gallicagraph(data) + plotnine.facet_wrap("keyword"), tmp_path)


def test_occur_lexicon():
    graph = gallicagraph(gallicagram_lexicon(["a", "b"], from_=2005, to=2005))
    assert labels(graph).title == 'Evolution of the monthly coverage of the "a" lexicon'


def test_cooccur(tmp_path):
    data = gallicagram_cooccur("a", "b", from_=1960, to=1960, cooccur_level="articles")
    graph = gallicagraph(data)
    assert labels(graph).title == 'Evolution of co-occurrences of "a" and "b"'
    # rallicagram lists all the corpora of list_corpora here
    assert labels(graph).subtitle == "In articles in the Le Monde (rubriques) corpus"
    assert labels(graph).y == "Proportion (of articles in the corpus)"
    draw(graph, tmp_path)
    draw(gallicagraph_cooccur(data, color="keyword") + plotnine.facet_wrap("keyword"), tmp_path)


def test_cooccur_lexicon():
    graph = gallicagraph(gallicagram_cooccur_lexicon(["a", "b"], ["c"], from_=1960, to=1960))
    assert labels(graph).title == 'Evolution of co-occurrences of the "a" and "c" lexicons'


def test_associated(tmp_path):
    data = gallicagram_associated("ami", from_=1960, to=1970, stopwords=None)
    graph = gallicagraph(data, labels_color="white")
    assert labels(graph).title == 'Words most often co-occurring with "ami"'
    assert labels(graph).subtitle == (
        "In 3-grams in the Le Monde (rubriques) corpus, from 1960 to 1970"
    )
    assert labels(graph).y == "Number of co-occurrences"
    assert len(graph.layers) == 2
    categories = graph.data["associated_word"].cat.categories
    assert categories[-1] == "de"  # most frequent word at the top
    assert data["associated_word"].dtype != "category"  # input not modified
    draw(graph, tmp_path)


def test_associated_no_label():
    data = gallicagram_associated("ami", from_=1960, to=1970)
    assert len(gallicagraph_associated(data).layers) == 1


def test_associated_lexicon():
    data = gallicagram_associated_lexicon(["a", "b"], from_=1960, to=1970)
    assert labels(gallicagraph(data)).title == (
        'Words most often co-occurring with the "a" lexicon'
    )


@pytest.mark.parametrize(
    "data", [pd.DataFrame({"a": [1]}), "not a data frame"]
)
def test_only_pyllicagram_data(data):
    with pytest.raises(ValueError, match="Only works for data produced by pyllicagram"):
        gallicagraph(data)


def test_with_data_has_no_graph():
    with pytest.raises(ValueError, match="Only works for data produced by pyllicagram"):
        gallicagraph(gallicagram_with("camarade", from_=1960, to=1970))


def test_date_labels():
    d = datetime.datetime
    assert _date_labels([d(1500, 1, 1), d(2005, 1, 1)]) == ["1500", "2005"]
    assert _date_labels([d(2005, 1, 1), d(2005, 7, 1)]) == ["2005-01", "2005-07"]
    assert _date_labels([d(2005, 1, 1), d(2005, 1, 15)]) == ["2005-01-01", "2005-01-15"]
