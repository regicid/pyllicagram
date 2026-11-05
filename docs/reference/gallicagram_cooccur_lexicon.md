# gallicagram_cooccur_lexicon

::: pyllicagram.gallicagram_cooccur_lexicon

## Examples, with their outputs

``` python
gallicagram_cooccur_lexicon(["président", "présidente"], ["mauvais", "nul"], corpus="press")
#>            date  n_cooccur   n_total  prop_cooccur  year  month  corpus resolution  \
#> 0    1789-01-01          0   1071494           0.0  1789      1  presse    monthly   
#> 1    1789-02-01          0    250634           0.0  1789      2  presse    monthly   
#> 2    1789-03-01          0    256735           0.0  1789      3  presse    monthly   
#> 3    1789-04-01          0    302266           0.0  1789      4  presse    monthly   
#> 4    1789-05-01          0    459722           0.0  1789      5  presse    monthly   
#> ...         ...        ...       ...           ...   ...    ...     ...        ...   
#> 1939 1950-08-01          0   9529732           0.0  1950      8  presse    monthly   
#> 1940 1950-09-01          0  10101409           0.0  1950      9  presse    monthly   
#> 1941 1950-10-01          0  11242624           0.0  1950     10  presse    monthly   
#> 1942 1950-11-01          0  11194426           0.0  1950     11  presse    monthly   
#> 1943 1950-12-01          0  11783823           0.0  1950     12  presse    monthly   
#> 
#>      cooccur_level  keyword_1 keyword_2             lexicon_1    lexicon_2  
#> 0          3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 1          3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 2          3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 3          3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 4          3-grams  président   mauvais  président+présidente  mauvais+nul  
#> ...            ...        ...       ...                   ...          ...  
#> 1939       3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 1940       3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 1941       3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 1942       3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 1943       3-grams  président   mauvais  président+présidente  mauvais+nul  
#> 
#> [1944 rows x 13 columns]
```

