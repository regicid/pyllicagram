# list_subcorpora

A data frame containing information about the available subcorpora.

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

## Usage

``` python
from pyllicagram import list_subcorpora
```
