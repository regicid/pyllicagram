# Differences with rallicagram

`pyllicagram` is a port of [`rallicagram`](https://github.com/vincentbagilet/rallicagram) 0.2.0, the R package by [Vincent Bagilet](https://vincentbagilet.github.io/). Each function has the same name, parameters, order of parameters and output columns as its R counterpart, and sends the same requests to the API, with the exceptions below.

This was checked by running 121 calls in both packages on the real API and comparing the URLs, warnings, errors, column names and values (`tools/r_parity`). The differences below are the only ones found.

## Addition: Cairn

`rallicagram` cannot query Cairn, as the code of this corpus in its `list_corpora` is "route à part (query_cairn)", which the API refuses. In `pyllicagram`:

- `gallicagram(corpus="cairn")` uses the route `query_cairn`, and `gallicagram_with` and `gallicagram_associated` work on this corpus.
- `subcorpora` also selects reviews of Cairn: `gallicagram("république", corpus="cairn", subcorpora=["ARSS", "ACO"], resolution="yearly")`.
- `list_corpora` has the code `cairn` in this row, and `list_subcorpora` also contains the 672 reviews of Cairn given by the API, with `tools/update_cairn_subcorpora.py`. Their `reliable_from` and `reliable_to` are missing, and these two columns therefore have the nullable `Int64` type.
- As `available_func` indicates for this corpus, `gallicagram_cooccur` is not available.

## Adaptations to Python

| R | Python |
|:---|:---|
| `from = 1960` | `from_=1960`, as `from` is a reserved word. The output column is still called `from` |
| `c("a", "b")` | `["a", "b"]` |
| `NULL`, `NA` (`stopwords`, `subcorpora`, `labels_color`) | `None` |
| `stopwords = stopwords_gallica[1:500]` | `stopwords="default"`, equal to `stopwords_gallica[:500]` |
| `color = keyword` | `color="keyword"` |
| `x |> gallicagraph()` | `gallicagraph(x)` or `x.pipe(gallicagraph)` |
| `+ facet_wrap(~ keyword)` | `+ plotnine.facet_wrap("keyword")` |
| `ggplot2` | `plotnine`, an optional dependency: `pip install "pyllicagram[graph]"` |
| `rbind(x, y)` | `pandas.concat([x, y])` |
| tibble | `pandas.DataFrame` |
| `Date` column | `datetime64[s]` column, as the default nanoseconds cannot represent the years before 1677 found in the `livres` corpus |
| `error_param` finds the function being called from the text of the call | `error_param` has an additional `func_type` parameter |
| error, warning | `ValueError` or `requests.HTTPError`, `UserWarning` |

## Problems of rallicagram fixed in this port

Each of these was reproduced with `rallicagram` 0.2.0 on the API as of November 2026.

### Results that differ

| Call | `rallicagram` | `pyllicagram` |
|:---|:---|:---|
| `get_same_stem("écologie")` passed to `gallicagram_lexicon` | `get_same_stem` returns "écologiste" and "écologistes" twice, so that they are counted twice in the sum: 1746 occurrences in 1990 in Le Monde | Each word appears once: 1185 occurrences |
| `gallicagram_associated("camarade", distance=2)`, column `cooccur_level` | "2-grams", while 3-grams are searched. "1-grams" for `distance=1` | "3-grams", "2-grams" |
| `gallicagram_with("le camarade", length=3)`, column `keyword` | "le%20camarade" | "le camarade" |
| `gallicagram_associated("le président de", corpus="livres")`, column `keyword` | "le président%20de" | "le président de" |
| `gallicagram_all("le président")`, column `n_of` | "1-grams" | "2-grams" |
| `gallicagram_lexicon(["Camarade", "camarade"])`, and the other lexicon functions | The API ignores the case but the word is searched twice, so counted twice: 386 occurrences in 2000 in Le Monde | Searched and counted once: 193 occurrences. The first form typed is kept |
| `gallicagram_associated_lexicon(["camarade", "le camarade"], distance=1)` | A word found for both keywords remains on two rows, one per level, each with the total, and takes two of the `n_results`. Its bar is twice too long in the graph | One row per word. `cooccur_level` is "2-grams, 3-grams" |
| `gallicagram("velo+auto")`, column `n_of` | "1-grams", while the API reads "+" as a space and uses the total of the 2-grams | "2-grams". Applies to all the checks on the number of words |
| `gallicagram("président ")`, column `n_of` | "2-grams", while the API ignores the space | "1-grams" |
| `gallicagram_with_month("Camarade")`, column `keyword` | "Camarade", while `gallicagram_with` gives "camarade" | "camarade" |
| `list_subcorpora`, column `disciplines` | Lists that end with an empty string, or `NA` for 4 reviews | No empty string. An empty list for these 4 reviews |
| `gallicagram("nan")`, `gallicagram("1945")`, column `keyword` | `NaN`, `1945` (numbers guessed by `read.csv`) | "nan", "1945" (text) |
| Subtitle of `gallicagraph_cooccur` | Lists all the corpora of `list_corpora` | Lists the corpora of the data |

### Calls that fail

| Call | `rallicagram` | `pyllicagram` |
|:---|:---|:---|
| `gallicagram("président", n_of="articles")` | HTTP error 404: the route `query_ngram_article` does not exist | Uses the route `query_article` |
| `gallicagram("république", corpus="persee")` | HTTP error 404: the route `query_ngram_persee` does not exist | Uses the route `query_persee` |
| `gallicagram(..., corpus="persee", subcorpora="arss")` | Always "Invalid subcorpus name" | Validated against `list_subcorpora`, then sent to the API |
| `gallicagram_associated("camarade", n_results="all")`, which is documented | Error | Returns all the results |
| `gallicagram("with", corpus="ouest")`, or any call whose text contains "with", "cooccur" or "associated" | "This function is not suported for this corpus", because the text of the call is searched | The function called is what is checked |

### Smaller changes

- A keyword containing `&`, `#` or `%` is encoded so that it does not break the URL.
- In `gallicagram_associated`, the keyword is removed from the associated words regardless of the case in which it was typed.
- `gallicagram(n_of="articles")` and `gallicagram_associated(distance="articles")` warn for a keyword of several words: the API does not fail but returns no results.
- Invalid numbers raise an error rather than giving unexpected results: `month` outside of 1-12, `n_results` that is not a positive whole number, and `from`, `to`, `distance` or `length` that are not whole numbers.
- An empty lexicon raises the error about `lexicon`, in all the lexicon functions.
- Axis labels of the graphs show `2005` and not `2005-01-01`.
- Typos in the messages and titles are fixed ("suported", "co-occurences").
- The HTTP errors include the answer of the API, for instance `corpus inconnu : tv_bfmtv`.
- Parts of the documentation that no longer match the data are updated: the functions are not limited to three corpora, `max_length` for Le Monde is 3, and `list_corpora` has 71 rows.

## What was kept on purpose

- `gallicagram_all` searches the same periods as in R, 1944-2023, 1789-1949 and 1000-1939, which go beyond the reliable periods of `lemonde` and `livres` and hence raise the same warnings.
- `gallicagram_cooccur` labels the Le Monde results "4-grams", which matches the phrases returned by the API (`président _ _ république`), even though `max_length` is 3 for this corpus.
- `gallicagram_lexicon` with keywords of different lengths returns one row per date and number of words, as in R.
- Apart from what is described above, the datasets are identical to those of `rallicagram`, including the reliable period of 1985-1991 given for all the reviews of Persée.
- `gallicagram_cooccur` reports `keyword_1` and `keyword_2` as typed, and the lexicon functions report the first keyword as typed.
- `gallicagram_with_month` is allowed on every corpus with "with" in `available_func`, even though the API only answers this route for `lemonde` and `presse` at the time of writing.
