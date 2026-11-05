# gallicagraph_cooccur

::: pyllicagram.gallicagraph_cooccur

## Examples, with their outputs

``` python
import pandas as pd
```

``` python
import plotnine
```

``` python
ancien = gallicagram_cooccur("président", "ancien", cooccur_level="articles")
```

``` python
gallicagraph_cooccur(ancien)
```

![Graph](figures/gallicagraph_cooccur-4.png)

``` python
both = pd.concat([ancien, gallicagram_cooccur("président", "république", cooccur_level="articles")])
```

``` python
gallicagraph_cooccur(both, color="keyword")
```

![Graph](figures/gallicagraph_cooccur-6.png)

``` python
gallicagraph_cooccur(both) + plotnine.facet_wrap("keyword")
```

![Graph](figures/gallicagraph_cooccur-7.png)

