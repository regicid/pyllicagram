# gallicagram

::: pyllicagram.gallicagram

## Examples, with their outputs

``` python
gallicagram("président")
#>           date    keyword  n_occur  n_total  prop_occur  year  month   corpus  \
#> 0   1945-01-01  président      306   262131    0.001167  1945      1  lemonde   
#> 1   1945-02-01  président      248   256110    0.000968  1945      2  lemonde   
#> 2   1945-03-01  président      327   313806    0.001042  1945      3  lemonde   
#> 3   1945-04-01  président      565   299972    0.001884  1945      4  lemonde   
#> 4   1945-05-01  président      406   327917    0.001238  1945      5  lemonde   
#> ..         ...        ...      ...      ...         ...   ...    ...      ...   
#> 931 2022-08-01  président     2256  2338286    0.000965  2022      8  lemonde   
#> 932 2022-09-01  président     3152  3358982    0.000938  2022      9  lemonde   
#> 933 2022-10-01  président     3061  3189107    0.000960  2022     10  lemonde   
#> 934 2022-11-01  président     3175  3336090    0.000952  2022     11  lemonde   
#> 935 2022-12-01  président     3152  3242511    0.000972  2022     12  lemonde   
#> 
#>     resolution     n_of  
#> 0      monthly  1-grams  
#> 1      monthly  1-grams  
#> 2      monthly  1-grams  
#> 3      monthly  1-grams  
#> 4      monthly  1-grams  
#> ..         ...      ...  
#> 931    monthly  1-grams  
#> 932    monthly  1-grams  
#> 933    monthly  1-grams  
#> 934    monthly  1-grams  
#> 935    monthly  1-grams  
#> 
#> [936 rows x 10 columns]
```

``` python
gallicagram("république", corpus="cairn", from_=2010, to=2020, resolution="yearly", subcorpora=["ARSS", "ACO"])
#>          date     keyword  n_occur  n_total  prop_occur  year corpus resolution  \
#> 0  2010-01-01  république       23   363249    0.000063  2010  cairn     yearly   
#> 1  2011-01-01  république       70   390962    0.000179  2011  cairn     yearly   
#> 2  2012-01-01  république       41   360705    0.000114  2012  cairn     yearly   
#> 3  2013-01-01  république       21   306986    0.000068  2013  cairn     yearly   
#> 4  2014-01-01  république       89   255840    0.000348  2014  cairn     yearly   
#> ..        ...         ...      ...      ...         ...   ...    ...        ...   
#> 6  2016-01-01  république       29   292680    0.000099  2016  cairn     yearly   
#> 7  2017-01-01  république        3   256062    0.000012  2017  cairn     yearly   
#> 8  2018-01-01  république       23   364148    0.000063  2018  cairn     yearly   
#> 9  2019-01-01  république       35   191809    0.000182  2019  cairn     yearly   
#> 10 2020-01-01  république        4   356677    0.000011  2020  cairn     yearly   
#> 
#>        n_of  
#> 0   1-grams  
#> 1   1-grams  
#> 2   1-grams  
#> 3   1-grams  
#> 4   1-grams  
#> ..      ...  
#> 6   1-grams  
#> 7   1-grams  
#> 8   1-grams  
#> 9   1-grams  
#> 10  1-grams  
#> 
#> [11 rows x 9 columns]
```

