import pandas as pd
import collections
def pyllicagram(recherche,corpus="presse",debut=1789,fin=1950,resolution="default",somme=False):
	if not isinstance(recherche, str) and not isinstance(recherche, list):
            raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
	if not isinstance(recherche, list): recherche = [recherche]
	assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
	assert resolution in ["default","annee","mois"], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
	for gram in recherche:
		gram = gram.replace(" ","%20")
		df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{gram}_from={debut}_to={fin}")
		if resolution=="mois" and corpus != "livres":
			df = df.groupby(["annee","mois", "gram"]).agg({'n':'sum','total':'sum'}).reset_index()
		if resolution=="annee":
			df = df.groupby(["annee","gram"]).agg({'n':'sum','total':'sum'}).reset_index()
		if 'result' in locals():
			result = pd.concat([result, df])
		else:
			result = df
	if somme:
		result = result.groupby(["annee",*(("mois",) if "mois" in result.columns else()),*(("jour",) if 'jour' in result.columns else())]).agg({'n':'sum','total':'mean'}).reset_index()
		result["gram"] = "+".join(recherche)
	result["ratio"] = result.n.values/result.total.values
	return result
