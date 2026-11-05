"""Adds the reviews of Cairn, given by the API, to the list_subcorpora dataset.

Usage: python tools/update_cairn_subcorpora.py

rallicagram only lists the reviews of Persée. A review can belong to several
disciplines. The API does not give the period covered by each review, hence the
missing reliable_from and reliable_to.
"""

import csv
from pathlib import Path

import requests

URL = "https://shiny.ens-paris-saclay.fr/guni/v2/revues?corpus=cairn"
PATH = Path(__file__).parents[1] / "src" / "pyllicagram" / "data" / "list_subcorpora.csv"


def main():
    response = requests.get(URL, timeout=600)
    response.raise_for_status()

    names, disciplines = {}, {}
    for discipline in response.json()["disciplines"]:
        for review in discipline["revues"]:
            names[review["code"]] = review["name"]
            disciplines.setdefault(review["code"], []).append(discipline["discipline"])

    def quoted(value):
        return '"' + value.replace('"', '""') + '"'

    lines = [
        line
        for line in PATH.read_text(encoding="utf-8").splitlines()
        if not line.endswith(',"cairn"')
    ]
    for code, name in names.items():
        fields = [quoted(name), quoted(code), "NA", "NA",
                  quoted(";".join(disciplines[code])), quoted("cairn")]
        lines.append(",".join(fields))
    PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    print(len(rows), "rows, of which", sum(r["corpus"] == "cairn" for r in rows), "for Cairn")


if __name__ == "__main__":
    main()
