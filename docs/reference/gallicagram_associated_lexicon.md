# gallicagram_associated_lexicon

::: pyllicagram.gallicagram_associated_lexicon

## Examples, with their outputs

``` python
gallicagram_associated_lexicon(["président", "présidentiel"])
#>    associated_word  n_cooccur    keyword   corpus  from    to cooccur_level  \
#> 0           groupe      35889  président  lemonde  1945  2024       3-grams   
#> 1        américain      24850  président  lemonde  1945  2024       3-grams   
#> 2        assemblée      24328  président  lemonde  1945  2024       3-grams   
#> 3      association      19188  président  lemonde  1945  2024       3-grams   
#> 4           comité      17625  président  lemonde  1945  2024       3-grams   
#> ..             ...        ...        ...      ...   ...   ...           ...   
#> 15      eisenhower       8140  président  lemonde  1945  2024       3-grams   
#> 16           sénat       7858  président  lemonde  1945  2024       3-grams   
#> 17           nixon       7105  président  lemonde  1945  2024       3-grams   
#> 18           russe       6913  président  lemonde  1945  2024       3-grams   
#> 19             élu       6908  président  lemonde  1945  2024       3-grams   
#> 
#>                    lexicon  
#> 0   président+présidentiel  
#> 1   président+présidentiel  
#> 2   président+présidentiel  
#> 3   président+présidentiel  
#> 4   président+présidentiel  
#> ..                     ...  
#> 15  président+présidentiel  
#> 16  président+présidentiel  
#> 17  président+présidentiel  
#> 18  président+présidentiel  
#> 19  président+présidentiel  
#> 
#> [20 rows x 8 columns]
```

