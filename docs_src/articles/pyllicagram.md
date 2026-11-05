# pyllicagram

This vignette introduces the main functions in the package and provides examples of simple analyses that can be carried out with these functions. It is adapted from the [vignette of `rallicagram`](https://vincentbagilet.github.io/rallicagram/articles/rallicagram.html), the R package by Vincent Bagilet of which `pyllicagram` is a port.

More information is available in the documentation of each function, accessible by typing `help(gallicagram)` in the console for instance, for the `gallicagram` function.

```{python echo=False}
from pyllicagram import *
```

## Main functions

### Occurrences

The main function in this package, `gallicagram`, builds a data frame with the yearly, monthly or daily proportion of mentions of a term in one of the corpora.

For the *Le Monde* corpus, this function allows to compute the number of newspaper articles that mention the keywords (parameter `n_of="articles"`).

```{python}
ex_occur = gallicagram(
    keyword="président",
    corpus="lemonde",
    from_=1960,
    to=1970,
    resolution="monthly",
)
```

Here is an example of the first rows of the output:

```{python table=ex_occur}
```

### Co-occurrences

`gallicagram_cooccur` builds a data frame with the yearly or monthly proportion of mentions of close co-occurrences of two keywords in one of the corpora for which this function is available (see the `available_func` column of `list_corpora`) between two specified dates.

Close co-occurrences correspond to words that are less than 3 (4 in the *Le Monde* corpus) words away in the initial text. For the *Le Monde* corpus, this function allows to compute the number of co-occurrences within an entire article (parameter `cooccur_level="articles"`).

```{python}
ex_cooccur = gallicagram_cooccur(
    keyword_1="président",
    keyword_2="république",
    corpus="lemonde",
    from_=1960,
    to=1970,
    resolution="monthly",
    cooccur_level="articles",
)
```

Here is an example of part of the output:

```{python table=ex_cooccur}
```

### Associations

`gallicagram_associated` builds a data frame with the words most frequently used close to a given keyword over the period. For the *Le Monde* corpus, this function allows to compute the number of co-occurrences within an entire article (parameter `distance="articles"`).

```{python}
ex_associated = gallicagram_associated(
    keyword="camarade",
    corpus="lemonde",
    from_=1960,
    to=1970,
    n_results=10,
    distance=2,
)
```

The terms most often associated with "camarade" are:

```{python table=ex_associated rows=10}
```

## Graphs

One of the main usage of `Gallicagram` is to plot time series of occurrences in a corpus. The function `gallicagraph` enables to do that in only one additional line of code. It takes as input a data frame produced by one of the functions from the package and automatically produces the corresponding graph:

```{python figure=graph_line}
gallicagraph(gallicagram(keyword="obama", corpus="lemonde", from_=2005))
```

The graphs are [`plotnine`](https://plotnine.org/) objects, the Python port of `ggplot2`: they display automatically in a notebook, can be saved with their `.save()` method and can be modified by adding elements, as in `ggplot2`. The documentation of `rallicagram` uses the `ggplot2` theme [`mediocrethemes`](https://vincentbagilet.github.io/mediocrethemes/) of its author. It has no Python version, so that the graphs below use the default theme. Another theme can be set with `plotnine.theme_set()`.

One can also use the same function to plot words associated with a given keyword:

```{python figure=graph_associated height=6}
gallicagraph(gallicagram_associated(keyword="obama", corpus="lemonde", from_=2005))
```

## More than one keyword

### Occurrences of a lexicon

Each of the main functions described above has a `lexicon` counterpart, adding a suffix `_lexicon` (`gallicagram_lexicon`, `gallicagram_cooccur_lexicon` and `gallicagram_associated_lexicon`). Each function simply loops the initial function over each word of the lexicon(s) and sums the results. It thus computes the sum of (co-)occurrences of each word in the lexicon:

```{python}
ex_lexicon = gallicagram_lexicon(
    lexicon=["président", "présidente"],
    corpus="lemonde",
    from_=1960,
    to=1970,
    resolution="monthly",
)

ex_cooccur_lexicon = gallicagram_cooccur_lexicon(
    lexicon_1=["président", "présidente"],
    lexicon_2=["mauvais", "nul"],
    corpus="lemonde",
    from_=1960,
    to=1970,
    resolution="monthly",
    cooccur_level="articles",
)
```

Here is an example of part of the output of `gallicagram_lexicon`:

```{python table=ex_lexicon}
```

These functions are particularly helpful to compute the number of occurrences of words from a whole lexical field (or the plural or feminine form of a keyword, etc).

### Words with the same stem

The function `get_same_stem()` enables to retrieve part of these forms: those that share the same stem as the keyword of interest. For instance, for "écologie":

```{python}
get_same_stem("écologie")
```

This function is particularly useful when its output is passed to one of the `_lexicon` functions:

```{python}
ex_stem_lexicon = gallicagram_lexicon(
    get_same_stem("écologie"),
    corpus="lemonde",
    from_=1960,
    to=1970,
    resolution="yearly",
)
```

Note that due to the number of requests sent to the API, it may take some time to run.

```{python table=ex_stem_lexicon}
```

### Searching several keywords

One can also run the functions for several keywords but separately, without summing the result. To do so, one can call the function for each keyword in a list comprehension and bind the results with `pandas.concat`. It returns a unique data frame with the results for searches corresponding to each keyword.

```{python}
import pandas as pd

keywords = ["république", "france"]

ex_keywords = pd.concat(
    [gallicagram(keyword, corpus="lemonde", from_=1960, to=1970) for keyword in keywords],
    ignore_index=True,
)
```

Based on that same principle, we can run several searches at once, varying all parameters, not only the keyword searched. To do that, we can specify the series of parameters in a data frame, each row corresponding to a set of parameters to run the `gallicagram` function for.

To specify the set of parameters, we can either build the parameters data frame by hand or use `merge(how="cross")` to create all combinations of possible searches.

```{python}
params = (
    pd.DataFrame({"from_": [1850], "to": [1870], "resolution": ["yearly"]})
    .merge(pd.DataFrame({"corpus": ["press", "books"]}), how="cross")
    .merge(pd.DataFrame({"keyword": ["république", "france"]}), how="cross")
)
```

The corresponding set of parameters to search looks like this:

```{python table=params}
```

We can then call the function `gallicagram` for each of the 4 sets of parameters defined in the rows of `params`:

```{python}
ex_params = pd.concat(
    [gallicagram(**row) for row in params.to_dict("records")],
    ignore_index=True,
)
```

This method also applies to the other functions in the `pyllicagram` package.
