# pyllicagram

## Overview

`pyllicagram` is a Python wrapper for the [Gallicagram](https://www.gallicagram.com/) API.

> **This package is a port to Python of [`rallicagram`](https://github.com/vincentbagilet/rallicagram), the R package by [Vincent Bagilet](https://vincentbagilet.github.io/).** The design of the functions and most of this documentation are his work, adapted to Python. The [differences between the two packages](DOCS/differences.md) are listed in the documentation. Please report problems with this port on the [`pyllicagram` repository](https://github.com/regicid/pyllicagram/issues), not to the author of `rallicagram`.

[Gallicagram](https://www.gallicagram.com/) is a super nice tool and set of databases that enables to easily run simple Natural Language Processing (**NLP**) analyses on a wide set of corpora. In particular, it enables to build historical **time series of occurrences of keywords** in various media in one line of code.

## Installation

You can install `pyllicagram` from PyPI, with the optional dependency used to draw graphs ([`plotnine`](https://plotnine.org/), the Python port of `ggplot2`), with:

``` console
pip install "pyllicagram[graph]"
```

You can install the development version from [GitHub](https://github.com/regicid/pyllicagram) with:

``` console
pip install "pyllicagram[graph] @ git+https://github.com/regicid/pyllicagram"
```

## Usage

The main function, `gallicagram`, builds a data frame with the yearly, monthly or daily proportion of mentions of a term.

```{python}
from pyllicagram import gallicagram

gallicagram(keyword="président", corpus="lemonde", from_=1960)
```

Note that the parameter called `from` in `rallicagram` is called `from_` here, as `from` is a reserved word in Python.

It enables to draw nice graphs representing the evolution of the use of a term in time, in two lines of code.

```{python figure=README-graph-1}
from pyllicagram import gallicagraph

gallicagraph(gallicagram(keyword="obama", from_=2005))
```

The package also allows to describe co-occurrences or words associated with a keyword. The corresponding functions are described in the [vignette](DOCS/articles/pyllicagram.md).

## Corpora

The corpora available via Gallicagram are the following. Note, for now, there are two "Le Monde" corpora, with different functions associated with each (this is a feature of the data base and will evolve shortly).

```{python table=corpora}
```

These are the data of the `list_corpora` dataset. It is the one of `rallicagram`, except that Cairn, which `rallicagram` cannot query, has its actual code, `cairn`, and can be searched by review with the parameter `subcorpora`, like Persée. The codes of the reviews of both corpora are in the `list_subcorpora` dataset.

At the time of writing, the route of the API used by `gallicagram` refuses the codes `presse_livres`, `tv_bfmtv`, `tv_cnews`, `tv_franceinfo` and `presse_moderne`: calling `gallicagram` on these raises an error containing the answer of the API, as with `rallicagram`. The "route à part (persee+cairn)" row is not an actual corpus code and is refused by `pyllicagram`.

Additional information on Gallicagram can be found on a [preprint](https://osf.io/preprints/socarxiv/84bf3/) by Gallicagram developers [Benoît de Courson](https://regicid.github.io/) and Benjamin Azoulay and on the "Notice" tab of the [Gallicagram website](https://www.gallicagram.com/).

## Functions of pyllicagram 1.x

The functions of the previous versions of this package (`pyllicagram`, `joker`, `contain`, `cooccur_doc`, `associated` and `associated_article`) are still available and work as before, so existing code keeps working. New code should use the functions described above.

Importing the package no longer sends a request to the API, no longer tries to install pandas and no longer disables the verification of SSL certificates for the whole Python session.

## Credits

`pyllicagram` is distributed under the MIT license. The port is based on `rallicagram`, Copyright (c) 2023 rallicagram authors: see the [license](LICENSE).
