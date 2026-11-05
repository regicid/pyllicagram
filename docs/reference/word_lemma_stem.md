# word_lemma_stem

A data frame containing words, their lemmas and stem of the lemmas.

The lemmas come from the [Lexique](http://www.lexique.org/) data base. The stems are obtained by stemming these lemmas using the `SnowballC` R package.

This data frame can be used to get a list of words that are closely related to a keyword of interest.

**Format**: a data frame with 3 columns (`word`, `lemma`, `stem`) and 142,694 rows.

## Usage

``` python
from pyllicagram import word_lemma_stem
```
