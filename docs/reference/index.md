# Reference

## Main functions

- [`gallicagram`](gallicagram.md): Occurrences of a keyword in a Gallicagram corpus.
- [`gallicagram_associated`](gallicagram_associated.md): Words the most often associated with a keyword in a Gallicagram corpus.
- [`gallicagram_cooccur`](gallicagram_cooccur.md): Close co-occurrences of two keywords in a Gallicagram corpus.
- [`gallicagram_with`](gallicagram_with.md): ngrams that most frequently contain a keyword in a Gallicagram corpus over a period.

## Lexicon version of main functions

Running the main functions for more than one keyword.

- [`gallicagram_lexicon`](gallicagram_lexicon.md): Occurrences of a list of keywords in a Gallicagram corpus.
- [`gallicagram_associated_lexicon`](gallicagram_associated_lexicon.md): Words the most often associated with a list of keywords in a Gallicagram corpus.
- [`gallicagram_cooccur_lexicon`](gallicagram_cooccur_lexicon.md): Close co-occurrences of two lexicons in a Gallicagram corpus.
- [`get_same_stem`](get_same_stem.md): Finds words with the same stem as a keyword.

## Graph functions

- [`gallicagraph`](gallicagraph.md): Automatically produces the relevant graph.
- [`gallicagraph_occur`](gallicagraph_occur.md): Graph describing the evolution of the proportion of occurrences.
- [`gallicagraph_cooccur`](gallicagraph_cooccur.md): Graph describing the evolution of the proportion of co-occurrences.
- [`gallicagraph_associated`](gallicagraph_associated.md): Graph describing the most common co-occurrences with a keyword or lexicon.

## Other functions

- [`gallicagram_with_month`](gallicagram_with_month.md): ngrams that most frequently contain a keyword in a Gallicagram corpus for a specific month.
- [`gallicagram_all`](gallicagram_all.md): Occurrences of a keyword in all Gallicagram corpora.

## Data

- [`list_corpora`](list_corpora.md): A data frame containing information about the available corpora.
- [`list_subcorpora`](list_subcorpora.md): A data frame containing information about the available subcorpora.
- [`stopwords_gallica`](stopwords_gallica.md): A list containing the most frequent words in the Gallica books corpus.
- [`word_lemma_stem`](word_lemma_stem.md): A data frame containing words, their lemmas and stem of the lemmas.

## Internal functions

- [`error_param`](error_param.md): Internal function to check for errors in the parameters.
- [`prepare_param`](prepare_param.md): Internal function to prepare the parameters to use them in the API call.
- [`read_data_gallicagram`](read_data_gallicagram.md): Internal function to read the output of the API call.
- [`tidy_gallicagram`](tidy_gallicagram.md): Internal function to tidy the output of the API call.
