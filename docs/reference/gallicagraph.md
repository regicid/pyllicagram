# gallicagraph

::: pyllicagram.gallicagraph

## Examples, with their outputs

``` python
gallicagraph(gallicagram("président"))
```

![Graph](figures/gallicagraph-1.png)

``` python
gallicagraph(gallicagram_cooccur("président", "ancien", cooccur_level="articles"))
```

![Graph](figures/gallicagraph-2.png)

``` python
gallicagraph(gallicagram_associated("patate", from_=2020))
```

![Graph](figures/gallicagraph-3.png)

