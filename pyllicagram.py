import pandas as pd
import collections
def pyllicagram(gram,corpus="presse",debut=1789,fin=1950,resolution="default"):
	if not isinstance(gram, str) and not isinstance(gram, list):
            raise ValueError("Le gram doit être une chaîne de caractères ou une liste")
	if not isinstance(gram, list): gram = [gram]
	assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
	assert resolution in ["default","annee","mois"], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
	for gram in gram:
		df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{gram}_from={debut}_to={fin}")
		if resolution=="mois" and corpus != "livres":
			df = df.groupby(["annee","mois","gram"]).agg({'n':'sum','total':'sum'}).reset_index()
		if resolution=="annee":
			df = df.groupby(["annee","gram"]).agg({'n':'sum','total':'sum'}).reset_index()
		df["ratio"] = df.n.values/df.total.values
		if 'result' in locals():
			result = pd.concat([result, df])
		else:
			result = df
	return result
