"""Builds the documentation, as knitr and pkgdown do for rallicagram.

Usage: python tools/render_docs.py

Every example is executed against the real API, so that the outputs shown are
real and that an example that does not work stops the build. It generates:

- README.md and docs/index.md from docs_src/README.md
- docs/articles/pyllicagram.md from docs_src/articles/pyllicagram.md
- docs/reference/*.md from the docstrings

Blocks of the form ```{python options} are executed. The options are:
echo=False, figure=<name>, height=<inches>, table=<variable or "corpora">,
rows=<number of rows of the table>.
"""

import ast
import contextlib
import inspect
import io
import re
import shutil
import warnings
from pathlib import Path

import pandas as pd
import plotnine

import pyllicagram
from pyllicagram import _params, _read

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RAW = "https://raw.githubusercontent.com/regicid/pyllicagram/main/"
BLOB = "https://github.com/regicid/pyllicagram/blob/main/"

PAGES = {
    "Main functions": (None, [
        "gallicagram", "gallicagram_associated", "gallicagram_cooccur", "gallicagram_with",
    ]),
    "Lexicon version of main functions": ("Running the main functions for more than one keyword.", [
        "gallicagram_lexicon", "gallicagram_associated_lexicon",
        "gallicagram_cooccur_lexicon", "get_same_stem",
    ]),
    "Graph functions": (None, [
        "gallicagraph", "gallicagraph_occur", "gallicagraph_cooccur", "gallicagraph_associated",
    ]),
    "Other functions": (None, ["gallicagram_with_month", "gallicagram_all"]),
    "Data": (None, ["list_corpora", "list_subcorpora", "stopwords_gallica", "word_lemma_stem"]),
    "Internal functions": (None, [
        "error_param", "prepare_param", "read_data_gallicagram", "tidy_gallicagram",
    ]),
}
OBJECTS = {
    "prepare_param": (_params.prepare_param, "pyllicagram._params.prepare_param"),
    "read_data_gallicagram": (_read.read_data_gallicagram, "pyllicagram._read.read_data_gallicagram"),
    "tidy_gallicagram": (_read.tidy_gallicagram, "pyllicagram._read.tidy_gallicagram"),
}
DATA_PAGES = {
    "list_corpora": """A data frame containing information about the available corpora.

It includes the code name of the corpus, its plain language name, the years for which the data is reliable, the number of words in each corpus, the maximum length of the ngrams, and the resolution.

**Format**: a data frame with 71 rows and 9 variables:

| Variable | Description |
|:---|:---|
| `corpus` | Code name of the corpus. |
| `corpus_name` | Plain language name of the corpus. |
| `reliable_from` | The year at which the corpus starts being reliable. |
| `reliable_to` | The year at which the corpus stops being reliable. |
| `nb_words` | The number of words in the corpus. |
| `max_length` | The maximum length of ngrams available. |
| `resolution` | The finest available resolution (daily, monthly, yearly). |
| `available_func` | The set of available functions for this corpus, in addition to `gallicagram()`. |
| `alt_base` | An internal variable that indicates in which database the corpus is stored. |
""",
    "list_subcorpora": """A data frame containing information about the available subcorpora.

It includes the code name of the corpus and subcorpus, its plain language name, the years for which the data is reliable, and the academic disciplines it relates to. It contains the 368 reviews of Persée and the 672 reviews of Cairn. The codes are specific to each corpus and, for Cairn, are in upper case.

**Format**: a data frame with 1040 rows and 6 variables:

| Variable | Description |
|:---|:---|
| `subcorpus_name` | Plain language name of the subcorpus. |
| `subcorpus` | Code name of the subcorpus. |
| `reliable_from` | The year at which the subcorpus starts being reliable. Missing for Cairn, as the API does not give it. |
| `reliable_to` | The year at which the subcorpus stops being reliable. Missing for Cairn, as the API does not give it. |
| `disciplines` | The academic disciplines associated with this subcorpus, as a list. Empty for the 4 reviews of Persée without a discipline. |
| `corpus` | Code name of the corpus. |
""",
    "stopwords_gallica": """A list containing the most frequent words in the Gallica books corpus.

Sorted from most to less frequent word.

**Format**: a list of length 1000.
""",
    "word_lemma_stem": """A data frame containing words, their lemmas and stem of the lemmas.

The lemmas come from the [Lexique](http://www.lexique.org/) data base. The stems are obtained by stemming these lemmas using the `SnowballC` R package.

This data frame can be used to get a list of words that are closely related to a keyword of interest.

**Format**: a data frame with 3 columns (`word`, `lemma`, `stem`) and 142,694 rows.
""",
}


class Session:
    def __init__(self, figures: Path, prefix: str = ""):
        self.namespace = {}
        exec("from pyllicagram import *", self.namespace)
        self.figures = figures
        self.prefix = prefix

    def run(self, code, figure=None, height=5):
        """Runs code. Returns the printed output and the path of the figure."""
        tree = ast.parse(code)
        last = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = ast.Expression(tree.body.pop().value)
        output = io.StringIO()
        with warnings.catch_warnings(record=True) as caught, contextlib.redirect_stdout(output):
            warnings.simplefilter("always")
            exec(compile(tree, "<docs>", "exec"), self.namespace)
            value = eval(compile(last, "<docs>", "eval"), self.namespace) if last else None
        text = "".join(
            f"UserWarning: {w.message}\n" for w in caught if w.category is UserWarning
        ) + output.getvalue()
        path = None
        if isinstance(value, plotnine.ggplot):
            if figure is None:
                raise ValueError(f"Graph without a figure name: {code}")
            self.figures.mkdir(parents=True, exist_ok=True)
            path = self.figures / f"{figure}.png"
            value.save(path, width=7, height=height, dpi=200, verbose=False)
        elif value is not None:
            with pd.option_context(
                "display.width", 88, "display.max_rows", 10, "display.max_columns", None,
                "display.min_rows", 10,
            ):
                text += repr(value) + "\n"
        return text, path


def comment(text):
    return "".join(f"#> {line}\n" for line in text.splitlines())


def markdown_table(data):
    def cell(value):
        if isinstance(value, pd.Timestamp):
            return str(value.date())
        if isinstance(value, float):
            return f"{value:.7g}"
        return str(value).replace("|", "\\|").replace("#", "\\#")

    lines = ["| " + " | ".join(str(c) for c in data.columns) + " |"]
    lines.append("|" + "|".join(":---" for _ in data.columns) + "|")
    for row in data.itertuples(index=False):
        lines.append("| " + " | ".join(cell(v) for v in row) + " |")
    return "\n".join(lines) + "\n"


def corpora_table():
    corpora = pyllicagram.list_corpora
    corpora["Number Of Words"] = [
        "-" if pd.isna(value) else f"{value:g}" for value in corpora["nb_words"]
    ]
    corpora["Available Functions"] = corpora["available_func"].fillna("-")
    corpora = corpora[[
        "corpus_name", "corpus", "reliable_from", "reliable_to", "max_length",
        "resolution", "Number Of Words", "Available Functions",
    ]].rename(columns=lambda name: name.replace("_", " ").title())
    return markdown_table(corpora)


OPTIONS = re.compile(r"(\w+)=([^\s}]+)")
BLOCK = re.compile(r"```\{python([^}]*)\}\n(.*?)```\n", re.S)


def render(source, session, figure_link):
    def replace(match):
        options = dict(OPTIONS.findall(match.group(1)))
        code = match.group(2)
        if options.get("table") == "corpora":
            return corpora_table()
        if "table" in options:
            data = session.namespace[options["table"]]
            return markdown_table(data.head(int(options.get("rows", 6))))
        text, path = session.run(
            code, options.get("figure"), float(options.get("height", 5))
        )
        out = ""
        if options.get("echo") != "False":
            out += f"``` python\n{code}"
            out += comment(text)
            out += "```\n"
        if path is not None:
            out += f"\n![Graph]({figure_link(path)})\n"
        return out

    return BLOCK.sub(replace, source)


def _documented(name):
    if name in OBJECTS:
        return OBJECTS[name]
    return getattr(pyllicagram, name), f"pyllicagram.{name}"


def reference_page(name):
    if name in DATA_PAGES:
        return (
            f"# {name}\n\n{DATA_PAGES[name]}\n## Usage\n\n"
            f"``` python\nfrom pyllicagram import {name}\n```\n"
        )
    function, identifier = _documented(name)
    page = f"# {name}\n\n::: {identifier}\n"
    examples = [
        line[4:] for line in inspect.getdoc(function).splitlines() if line.startswith(">>> ")
    ]
    if examples:
        session = Session(DOCS / "reference" / "figures")
        page += "\n## Examples, with their outputs\n\n"
        count = 0
        for code in examples:
            count += 1
            text, path = session.run(code + "\n", f"{name}-{count}")
            page += f"``` python\n{code}\n{comment(text)}```\n\n"
            if path is not None:
                page += f"![Graph](figures/{path.name})\n\n"
    return page


def reference_index():
    page = "# Reference\n"
    for title, (description, names) in PAGES.items():
        page += f"\n## {title}\n\n"
        if description:
            page += f"{description}\n\n"
        for name in names:
            if name in DATA_PAGES:
                summary = DATA_PAGES[name].split("\n")[0]
            else:
                summary = inspect.getdoc(_documented(name)[0]).split("\n")[0]
            page += f"- [`{name}`]({name}.md): {summary}\n"
    return page


def main():
    for folder in (DOCS / "reference", DOCS / "figures"):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)

    readme = (ROOT / "docs_src" / "README.md").read_text(encoding="utf-8")
    session = Session(DOCS / "figures")
    body = render(readme, session, lambda path: f"FIGURES/{path.name}")

    header = (
        "<!-- README.md is generated from docs_src/README.md "
        "by tools/render_docs.py. Please edit that file -->\n\n"
    )
    github = (
        body.replace("FIGURES/", RAW + "docs/figures/")
        .replace("DOCS/", BLOB + "docs/")
        .replace("(LICENSE)", f"({BLOB}LICENSE)")
    )
    (ROOT / "README.md").write_text(header + github, encoding="utf-8")

    site = (
        body.replace("FIGURES/", "figures/")
        .replace("DOCS/", "")
        .replace("(LICENSE)", "(license.md)")
    )
    (DOCS / "index.md").write_text(site, encoding="utf-8")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    (DOCS / "license.md").write_text(
        f"# License\n\n```\n{license_text}```\n", encoding="utf-8"
    )

    article = (ROOT / "docs_src" / "articles" / "pyllicagram.md").read_text(encoding="utf-8")
    session = Session(DOCS / "figures")
    (DOCS / "articles" / "pyllicagram.md").write_text(
        render(article, session, lambda path: f"../figures/{path.name}"), encoding="utf-8"
    )

    (DOCS / "reference" / "index.md").write_text(reference_index(), encoding="utf-8")
    for _, names in PAGES.values():
        for name in names:
            print(name, flush=True)
            (DOCS / "reference" / f"{name}.md").write_text(
                reference_page(name), encoding="utf-8"
            )


if __name__ == "__main__":
    main()
