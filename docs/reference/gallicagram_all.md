# gallicagram_all

::: pyllicagram.gallicagram_all

## Examples, with their outputs

``` python
gallicagram_all("président")
#> UserWarning: The lemonde corpus is only reliable after 1945
#> UserWarning: The livres corpus is only reliable after 1700
#>           date    keyword  n_occur   n_total  prop_occur  year   corpus resolution  \
#> 0   1944-01-01  président      102    125782    0.000811  1944  lemonde     yearly   
#> 1   1945-01-01  président     5710   4248522    0.001344  1945  lemonde     yearly   
#> 2   1946-01-01  président     7329   5910189    0.001240  1946  lemonde     yearly   
#> 3   1947-01-01  président     6758   5299085    0.001275  1947  lemonde     yearly   
#> 4   1948-01-01  président     7005   6210111    0.001128  1948  lemonde     yearly   
#> ..         ...        ...      ...       ...         ...   ...      ...        ...   
#> 622 1935-01-01  président    17359  51241370    0.000339  1935   livres     yearly   
#> 623 1936-01-01  président    17631  41648149    0.000423  1936   livres     yearly   
#> 624 1937-01-01  président    10340  27685105    0.000373  1937   livres     yearly   
#> 625 1938-01-01  président     8999  29991419    0.000300  1938   livres     yearly   
#> 626 1939-01-01  président     3958  17400800    0.000227  1939   livres     yearly   
#> 
#>         n_of  
#> 0    1-grams  
#> 1    1-grams  
#> 2    1-grams  
#> 3    1-grams  
#> 4    1-grams  
#> ..       ...  
#> 622  1-grams  
#> 623  1-grams  
#> 624  1-grams  
#> 625  1-grams  
#> 626  1-grams  
#> 
#> [627 rows x 9 columns]
```

