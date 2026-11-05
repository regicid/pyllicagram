# list_corpora

A data frame containing information about the available corpora.

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

## Usage

``` python
from pyllicagram import list_corpora
```
