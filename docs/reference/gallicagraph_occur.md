# gallicagraph_occur

::: pyllicagram.gallicagraph_occur

## Examples, with their outputs

``` python
import pandas as pd
```

``` python
import plotnine
```

``` python
gallicagraph_occur(gallicagram("président"))
```

![Graph](figures/gallicagraph_occur-3.png)

``` python
both = pd.concat([gallicagram("président"), gallicagram("république")])
```

``` python
gallicagraph_occur(both, color="keyword")
```

![Graph](figures/gallicagraph_occur-5.png)

``` python
gallicagraph_occur(both) + plotnine.facet_wrap("keyword")
```

![Graph](figures/gallicagraph_occur-6.png)

``` python
corpora = pd.concat([gallicagram("président"), gallicagram("président", corpus="huma")])
```

``` python
gallicagraph_occur(corpora, color="corpus")
```

![Graph](figures/gallicagraph_occur-8.png)

