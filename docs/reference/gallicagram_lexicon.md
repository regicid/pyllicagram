# gallicagram_lexicon

::: pyllicagram.gallicagram_lexicon

## Examples, with their outputs

``` python
gallicagram_lexicon(["président", "présidentiel"])
#>           date    keyword  n_occur  n_total  prop_occur  year  month   corpus  \
#> 0   1945-01-01  président      310   262131    0.001183  1945      1  lemonde   
#> 1   1945-02-01  président      248   256110    0.000968  1945      2  lemonde   
#> 2   1945-03-01  président      329   313806    0.001048  1945      3  lemonde   
#> 3   1945-04-01  président      566   299972    0.001887  1945      4  lemonde   
#> 4   1945-05-01  président      408   327917    0.001244  1945      5  lemonde   
#> ..         ...        ...      ...      ...         ...   ...    ...      ...   
#> 931 2022-08-01  président     2351  2338286    0.001005  2022      8  lemonde   
#> 932 2022-09-01  président     3273  3358982    0.000974  2022      9  lemonde   
#> 933 2022-10-01  président     3177  3189107    0.000996  2022     10  lemonde   
#> 934 2022-11-01  président     3283  3336090    0.000984  2022     11  lemonde   
#> 935 2022-12-01  président     3249  3242511    0.001002  2022     12  lemonde   
#> 
#>     resolution     n_of                 lexicon  
#> 0      monthly  1-grams  président+présidentiel  
#> 1      monthly  1-grams  président+présidentiel  
#> 2      monthly  1-grams  président+présidentiel  
#> 3      monthly  1-grams  président+présidentiel  
#> 4      monthly  1-grams  président+présidentiel  
#> ..         ...      ...                     ...  
#> 931    monthly  1-grams  président+présidentiel  
#> 932    monthly  1-grams  président+présidentiel  
#> 933    monthly  1-grams  président+présidentiel  
#> 934    monthly  1-grams  président+présidentiel  
#> 935    monthly  1-grams  président+présidentiel  
#> 
#> [936 rows x 11 columns]
```

