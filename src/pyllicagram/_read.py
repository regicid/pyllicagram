"""Reading and tidying of the outputs of the API."""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

import numpy as np
import pandas as pd
import requests

BASE_URL = "https://shiny.ens-paris-saclay.fr/guni/"

# Long enough to handle queries that take Gallicagram a long time to process.
TIMEOUT = 5000

# Columns of the API that contain text. Everything else is numeric.
_TEXT_COLUMNS = {"gram"}


def _to_numeric(column: pd.Series) -> pd.Series:
    return pd.to_numeric(column.where(~column.isin(["", "NA"])))


def read_data_gallicagram(url: str) -> pd.DataFrame:
    """Internal function to read the output of the API call.

    Turns the output into a data frame.

    The timeout is set to 5000s to handle queries that take Gallicagram a long
    time to process.

    Unlike `pandas.read_csv` with its default arguments, the words returned by
    the API are always kept as text: the words "null", "nan" or "none" are not
    turned into missing values and "1945" remains a string.

    Parameters
    ----------
    url : str
        The URL to pass to the Gallicagram API.

    Returns
    -------
    pandas.DataFrame
        The raw data from the Gallicagram API.

    Raises
    ------
    requests.HTTPError
        If the API returns an error.
    """
    response = requests.get(url, timeout=TIMEOUT)
    if not response.ok:
        raise requests.HTTPError(
            f"The Gallicagram API returned the error {response.status_code} "
            f"({response.text.strip()[:200]}) for {url}",
            response=response,
        )

    output = pd.read_csv(
        BytesIO(response.content), encoding="utf-8", dtype=str, na_filter=False
    )
    for name in output.columns:
        if name not in _TEXT_COLUMNS:
            output[name] = _to_numeric(output[name])
    return output


def _dates(years: Iterable, months: Iterable, days: Iterable) -> pd.Series:
    """Builds dates in seconds, as nanoseconds cannot represent years before 1677."""
    dates = []
    for year, month, day in zip(years, months, days):
        try:
            dates.append(
                np.datetime64(f"{int(year):04d}-{int(month):02d}-{int(day):02d}", "s")
            )
        except ValueError:  # impossible date or missing value
            dates.append(np.datetime64("NaT", "s"))
    return pd.Series(np.array(dates, dtype="datetime64[s]"))


def tidy_gallicagram(url: str, corpus: str, resolution_en: str) -> pd.DataFrame:
    """Internal function to tidy the output of the API call.

    Turns the Gallicagram API data into a data frame, renames the variables and
    adds the input parameters to the output data frame.

    Parameters
    ----------
    url : str
        A URL to pass to the Gallicagram API.
    corpus : str
        The code of the corpus.
    resolution_en : str
        The resolution of the data: "daily", "monthly" or "yearly".

    Returns
    -------
    pandas.DataFrame
        Its columns are the `date` at the beginning of the period of a given
        observation, the `keyword`, the number of occurrences or co-occurrences
        (`n`), the total number of ngrams or articles over the period (`total`),
        their ratio (`prop`), the `year` and potentially the `month` and `day`
        of the observation, the `corpus` and the `resolution`. The functions
        calling this one then rename `n`, `total` and `prop`.
    """
    output = read_data_gallicagram(url).rename(
        columns={
            "gram": "keyword",
            "annee": "year",
            "mois": "month",
            "jour": "day",
            "nb_articles_occur": "n",
            "nb_total_article": "total",
            "nb_articles_cooccur": "n",
        }
    )

    output["prop"] = output["n"] / output["total"]
    output["corpus"] = corpus
    output["resolution"] = resolution_en
    months = output["month"] if resolution_en != "yearly" else [1] * len(output)
    days = output["day"] if resolution_en == "daily" else [1] * len(output)
    output["date"] = _dates(output["year"], months, days)

    first = ["date", "keyword", "n", "total", "prop"]
    return output[first + [name for name in output.columns if name not in first]]
