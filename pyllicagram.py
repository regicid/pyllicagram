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
        assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
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
        return result


def joker(gram,corpus="presse",debut=1789,fin=1950,after=True,n_joker=20):
    if not isinstance(gram, str) and not isinstance(gram, list):
            raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    gram = urllib.parse.quote_plus(gram.lower()).replace("-"," ").replace(" ","%20")
    df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/joker?corpus={corpus}&mot={gram}&from={debut}&to={fin}&after={after}&n_joker={n_joker}")
    return df 


def contain(mot1,mot2,corpus="presse",debut=1789,fin=1950):
    if not isinstance(mot1,str) or not isinstance(mot2,str):
        raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    mot1 = urllib.parse.quote_plus(mot1.lower()).replace("-"," ").replace(" ","%20")
    mot2 = urllib.parse.quote_plus(mot2.lower()).replace("-"," ").replace(" ","%20")
    df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/contain?corpus={corpus}&mot1={mot1}&mot2={mot2}&from={debut}&to={fin}")
    return df
