#!/usr/bin/python
# -*-coding:Utf-8 -*
#
# pyllicagram.py:
#    Un micro package python pour importer des données de [Gallicagram]
#
import urllib
import sys
from tqdm import tqdm
import os
import collections
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# import pandas
try:
        import pandas as pd
        pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/query?corpus=presse&mot=test&from=1789&to=1950")
        print(sys.executable)
except:
        print("install pandas...")
        # install pandas as a subprocess if needed
        os.system(sys.executable + " -m pip install pandas")
        os.system(sys.executable + " " + " ".join(sys.argv))
        exit()

# ------------------------
# API CALL
def pyllicagram(recherche,corpus="presse",debut=1789,fin=1950,resolution="default",somme=False):
        if not isinstance(recherche, str) and not isinstance(recherche, list):
            raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
        if not isinstance(recherche, list): recherche = [recherche]
        assert corpus in ["lemonde","livres","presse","huma","paris"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
        assert resolution in ["default","annee","mois"], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
        result = []
        for gram in tqdm(recherche):
                gram = urllib.parse.quote_plus(gram.lower()).replace("-"," ").replace("+"," ")
                gram = gram.replace(" ","%20")
                df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/query?corpus={corpus}&mot={gram}&from={debut}&to={fin}&resolution={resolution:}")
                #if resolution=="mois" and corpus != "livres":
                #        df = df.groupby(["annee","mois", "gram"]).agg({'n':'sum','total':'sum'}).reset_index()
                #if resolution=="annee":
                #        df = df.groupby(["annee","gram"]).agg({'n':'sum','total':'sum'}).reset_index()
                #if 'result' in locals():
                #        result = pd.concat([result, df])
                #else:
                #        result = df
                result.append(df)
        result = pd.concat(result)
        if somme:
                result = result.groupby(["annee",*(("mois",) if "mois" in result.columns else()),*(("jour",) if 'jour' in result.columns else())]).agg({'n':'sum','total':'mean'}).reset_index()
                result["gram"] = "+".join(recherche)
        result["ratio"] = result.n.values/result.total.values
        if 'jour' in result.columns:
            jour = result.jour.astype("str")
        else:
            jour = "01"
        if 'mois' in result.columns:
            mois = result.mois.astype("str")
        else:
            mois = "01"

        result["date"] = result.annee.astype("str") + "-" + mois + "-" + jour
        result.date = pd.to_datetime(result.date)
        return result


def joker(gram,corpus="presse",debut=1789,fin=1950,after=True,n_joker=20,length=None):
    if not isinstance(gram, str) and not isinstance(gram, list):
            raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    gram = urllib.parse.quote_plus(gram.lower()).replace("-"," ").replace(" ","%20")
    url=f"https://shiny.ens-paris-saclay.fr/guni/joker?corpus={corpus}&mot={gram}&from={debut}&to={fin}&after={after}"
    if length is not None: url=url+f"length={length}"
    df = pd.read_csv(url)
    return df 


def contain(mot1,mot2,corpus="presse",debut=1789,fin=1950,count=True):
    if not isinstance(mot1,str) or not isinstance(mot2,str):
        raise ValueError("La recherche doit être une chaîne de caractères")
    assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    mot1 = urllib.parse.quote_plus(mot1.lower()).replace("-"," ").replace(" ","%20")
    mot2 = urllib.parse.quote_plus(mot2.lower()).replace("-"," ").replace(" ","%20")
    df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/contain?corpus={corpus}&mot1={mot1}&mot2={mot2}&from={debut}&to={fin}&count={count}")
    return df

def cooccur_doc(mot1,mot2,debut=1945,fin=2022,resolution="mois"):
    if not isinstance(mot1,str) or not isinstance(mot2,str):
        raise ValueError("La recherche doit être une chaîne de caractères")
    assert resolution in ["annee","mois"], 'Vous devez choisir la résolution parmi "annee" et "mois"'
    mot1 = urllib.parse.quote_plus(mot1.lower()).replace("-"," ").replace(" ","%20")
    mot2 = urllib.parse.quote_plus(mot2.lower()).replace("-"," ").replace(" ","%20")
    df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/cooccur?mot1={mot1}&mot2={mot2}&from={debut}&to={fin}&resolution={resolution}")
    return df

def associated_article(mot,debut=1945,fin=2022,n_joker=100,stopwords=0):
    #if not isinstance(mot):
    #    raise ValueError("La recherche doit être une chaîne de caractères")
    mot = urllib.parse.quote_plus(mot.lower()).replace("-"," ").replace(" ","%20")
    url=f"https://shiny.ens-paris-saclay.fr/guni/associated_article?mot={mot}&from={debut}&to={fin}&n_joker={n_joker}&stopwords={stopwords}"
    df = pd.read_csv(url)
    return df




def associated(gram,corpus="presse",debut=1789,fin=1950,n_joker=20,length=None,stopwords=0):
    if not isinstance(gram, str) and not isinstance(gram, list):
            raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    gram = urllib.parse.quote_plus(gram.lower()).replace("-"," ").replace(" ","%20")
    url=f"https://shiny.ens-paris-saclay.fr/guni/associated?corpus={corpus}&mot={gram}&from={debut}&to={fin}&stopwords={stopwords}"
    if length is not None: url=url+f"&length={length}"
    df = pd.read_csv(url)
    return df

