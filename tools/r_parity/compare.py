"""Compares pyllicagram with rallicagram, on the real API.

Usage: python compare.py <path to rallicagram> [--write-urls <fixture.json>]

Each case of cases.json is run in both packages. The URLs sent to the API, the
warnings, the errors, the column names and the values have to be identical,
except for the deliberate differences described by the "expect" field of the
case, which are the ones listed in docs/differences.md.
"""

import json
import math
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path
from unittest import mock
from urllib.parse import unquote

import pandas as pd

import pyllicagram
from pyllicagram import _read

HERE = Path(__file__).parent
MESSAGE_FIXES = [
    ("route à part (query_cairn), route à part (persee+cairn), ", "cairn, "),
    ("suported", "supported"),
    ("Should be NULL or one of the one specified in rallicagram::list_subcorpora",
     "Should be None or one of the ones specified in pyllicagram.list_subcorpora"),
]


def run_python(case):
    args = {("from_" if k == "from" else k): v for k, v in case["args"].items()}
    urls = []
    real_get = _read.requests.get

    def get(url, **kwargs):
        urls.append(url)
        return real_get(url, **kwargs)

    out = {"urls": urls, "warnings": [], "error": None, "columns": None, "value": None}
    with warnings.catch_warnings(record=True) as caught, mock.patch.object(
        _read.requests, "get", get
    ):
        warnings.simplefilter("always")
        try:
            value = getattr(pyllicagram, case["fn"])(**args)
        except Exception as error:  # noqa: BLE001
            out["error"] = str(error)
        else:
            if isinstance(value, pd.DataFrame):
                out["columns"] = list(value.columns)
                out["dtypes"] = value.dtypes.astype(str).to_dict()
                if "date" in value:
                    value = value.assign(date=value["date"].astype(str))
                out["value"] = {
                    c: [None if pd.isna(x) else x for x in value[c].tolist()]
                    for c in value.columns
                }
            else:
                out["value"] = value
    out["warnings"] = list(dict.fromkeys(str(w.message) for w in caught))
    return out


def same_values(left, right):
    if left is None or right is None:
        # NaN and missing are one in JSON (R gives "NaN" as a string)
        return (left is None and right is None) or left == "NaN" or right == "NaN"
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(left, right, rel_tol=1e-13, abs_tol=0)
    return left == right


def fix(r, case):
    """Applies to the R results the deliberate differences."""
    expect = case.get("expect")
    if isinstance(r["error"], list):
        r["error"] = r["error"][0]
    if r["error"]:
        for old, new in MESSAGE_FIXES:
            r["error"] = r["error"].replace(old, new)
    columns = r["value"] if isinstance(r["value"], dict) else {}
    if expect == "assoc_label" and "cooccur_level" in columns:
        columns["cooccur_level"] = [
            f"{int(x.split('-')[0]) + 1}-grams" if x != "articles" else x
            for x in columns["cooccur_level"]
        ]
    if expect == "with_keyword":
        columns["keyword"] = [x.replace("%20", " ") for x in columns["keyword"]]
    if expect == "n_of_label":
        columns["n_of"] = [x.replace("1-grams", "2-grams") for x in columns["n_of"]]
    if expect == "word_type":
        # read.csv guesses that "nan" and "1945" are numbers
        columns["keyword"] = [case["args"]["keyword"]]
    if expect == "keyword_lower":
        columns["keyword"] = [x.lower() for x in columns["keyword"]]
    if expect == "n_of_trailing_space":
        columns["n_of"] = ["1-grams" for _ in columns["n_of"]]
    if expect == "stem_dedup":
        r["value"] = list(dict.fromkeys(r["value"]))
    return r


def compare(case, r, py):
    problems = []
    expect = case.get("expect")
    if expect == "r_broken":
        if not r["error"]:
            problems.append("R is expected to fail")
        if py["error"] or not py["columns"]:
            problems.append(f"Python should work: {py['error']}")
        return problems
    if expect == "fixed":
        # deliberately different results, checked in tests/test_live.py
        if py["error"] or not py["columns"]:
            problems.append(f"Python should work: {py['error']}")
        return problems
    if expect == "message":
        if bool(r["error"]) != bool(py["error"]):
            problems.append(f"errors differ: {r['error']!r} / {py['error']!r}")
        return problems

    r = fix(r, case)
    r_urls = [unquote(u) for u in r["urls"] or []]
    py_urls = [unquote(u) for u in py["urls"]]
    if r_urls != py_urls:
        problems.append(f"URLs differ:\n  R  {r_urls}\n  Py {py_urls}")
    if r["error"]:
        normal = " ".join(r["error"].split())
        if normal != " ".join((py["error"] or "").split()):
            problems.append(f"errors differ:\n  R  {normal}\n  Py {py['error']}")
        return problems
    if py["error"]:
        problems.append(f"only Python fails: {py['error']}")
        return problems
    r_warnings = sorted(" ".join(w.split()) for w in r["warnings"] or [])
    if r_warnings != sorted(" ".join(w.split()) for w in py["warnings"]):
        problems.append(f"warnings differ:\n  R  {r_warnings}\n  Py {py['warnings']}")
    if r["columns"] is None:
        if r["value"] != py["value"]:
            problems.append(f"values differ:\n  R  {r['value']}\n  Py {py['value']}")
        return problems
    if r["columns"] != py["columns"]:
        problems.append(f"columns differ:\n  R  {r['columns']}\n  Py {py['columns']}")
        return problems
    for column in r["columns"]:
        left, right = r["value"].get(column, []), py["value"][column]
        if len(left) != len(right):
            problems.append(f"{column}: {len(left)} rows in R, {len(right)} in Python")
            break
        bad = [
            i for i, (a, b) in enumerate(zip(left, right)) if not same_values(a, b)
        ]
        if bad:
            i = bad[0]
            problems.append(
                f"{column}: {len(bad)} values differ, first at row {i}: "
                f"R {left[i]!r} Py {right[i]!r}"
            )
    return problems


def main():
    rallicagram = sys.argv[1]
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as folder:
        output = Path(folder) / "r.json"
        subprocess.run(
            ["Rscript", str(HERE / "run_r.R"), rallicagram,
             str(HERE / "cases.json"), str(output)],
            check=True,
        )
        results = json.loads(output.read_text(encoding="utf-8"))

    failures = 0
    golden = []
    for case, r in zip(cases, results):
        py = run_python(case)
        golden.append({"fn": case["fn"], "args": case["args"], "urls": py["urls"]})
        problems = compare(case, r, py)
        status = "FAIL" if problems else "ok  "
        failures += bool(problems)
        print(status, case["fn"], json.dumps(case["args"], ensure_ascii=False))
        for problem in problems:
            print("    ", problem)
    print(f"\n{len(cases) - failures}/{len(cases)} cases identical")
    if "--write-urls" in sys.argv:
        path = sys.argv[sys.argv.index("--write-urls") + 1]
        Path(path).write_text(
            json.dumps(golden, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
