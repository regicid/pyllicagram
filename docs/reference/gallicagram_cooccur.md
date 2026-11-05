# gallicagram_cooccur

::: pyllicagram.gallicagram_cooccur

## Examples, with their outputs

``` python
gallicagram_cooccur("président", "mauvais", corpus="press")
#>            date  keyword_1 keyword_2  n_cooccur   n_total  prop_cooccur  year  month  \
#> 0    1789-01-01  président   mauvais          0   1071494           0.0  1789      1   
#> 1    1789-02-01  président   mauvais          0    250634           0.0  1789      2   
#> 2    1789-03-01  président   mauvais          0    256735           0.0  1789      3   
#> 3    1789-04-01  président   mauvais          0    302266           0.0  1789      4   
#> 4    1789-05-01  président   mauvais          0    459722           0.0  1789      5   
#> ...         ...        ...       ...        ...       ...           ...   ...    ...   
#> 1939 1950-08-01  président   mauvais          0   9529732           0.0  1950      8   
#> 1940 1950-09-01  président   mauvais          0  10101409           0.0  1950      9   
#> 1941 1950-10-01  président   mauvais          0  11242624           0.0  1950     10   
#> 1942 1950-11-01  président   mauvais          0  11194426           0.0  1950     11   
#> 1943 1950-12-01  président   mauvais          0  11783823           0.0  1950     12   
#> 
#>       corpus resolution cooccur_level  
#> 0     presse    monthly       3-grams  
#> 1     presse    monthly       3-grams  
#> 2     presse    monthly       3-grams  
#> 3     presse    monthly       3-grams  
#> 4     presse    monthly       3-grams  
#> ...      ...        ...           ...  
#> 1939  presse    monthly       3-grams  
#> 1940  presse    monthly       3-grams  
#> 1941  presse    monthly       3-grams  
#> 1942  presse    monthly       3-grams  
#> 1943  presse    monthly       3-grams  
#> 
#> [1944 rows x 11 columns]
```

