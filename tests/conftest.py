"""Tests run offline: the requests to the API are replaced by canned answers."""

from urllib.parse import parse_qs, urlparse

import pytest

from pyllicagram import _read


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.content = text.encode("utf-8")
        self.text = text
        self.status_code = status_code
        self.ok = status_code < 400


def _occurrences(query):
    mot = query.get("mot", ["motif"])[0]
    year = query.get("from", ["1960"])[0]
    resolution = query.get("resolution", ["annee"])[0]
    if resolution == "jour":
        return f"n,annee,mois,jour,gram,total\n2,{year},1,1,{mot},10\n3,{year},1,2,{mot},20\n"
    if resolution == "mois":
        return f"n,annee,mois,gram,total\n2,{year},1,{mot},10\n3,{year},2,{mot},20\n"
    return f"n,annee,gram,total\n2,{year},{mot},10\n"


def fake_answer(url):
    parsed = urlparse(url)
    route = parsed.path.rsplit("/", 1)[-1]
    query = parse_qs(parsed.query)
    if route.startswith("query"):
        return _occurrences(query)
    if route in ("contain", "cooccur"):
        gram = f"{query['mot1'][0]}&{query['mot2'][0]}"
        year = query["from"][0]
        if query["resolution"][0] == "jour":
            return f"n,annee,mois,jour,total,gram\n2,{year},1,1,10,{gram}\n"
        if query["resolution"][0] == "mois":
            return f"n,annee,mois,total,gram\n2,{year},1,10,{gram}\n"
        return f"n,annee,total,gram\n2,{year},10,{gram}\n"
    if route.startswith("associated"):
        return "gram,tot\nkhrouchtchev,14\nl'ami,3\nami,4\nn'est,2\nde,49\n1960,8\na2,7\nd',5\nnull,1\n"
    if route.startswith("joker"):
        return "tot,gram\n256,camarade de\n124,camarade null\n"
    raise AssertionError(f"Unexpected route: {url}")


@pytest.fixture(autouse=True)
def api(request, monkeypatch):
    """Records the URLs requested and answers with canned data."""
    urls = []
    if request.node.get_closest_marker("live"):
        yield urls
        return

    def get(url, **kwargs):
        urls.append(url)
        assert kwargs.get("timeout") == 5000
        return FakeResponse(fake_answer(url))

    monkeypatch.setattr(_read.requests, "get", get)
    yield urls
