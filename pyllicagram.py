import pandas as pd

def pyllicagram(gram,corpus="presse",debut=1789,fin=1950,resolution="default"):
	assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
	assert resolution in ["default","annee","mois"], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
	df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{gram}_from={debut}_to={fin}")
	if resolution=="mois" and corpus != "livres":
		df = df.groupby(["annee","mois","gram"]).agg({'n':'sum','total':'sum'}).reset_index()
	if resolution=="annee":
		df = df.groupby(["annee","gram"]).agg({'n':'sum','total':'sum'}).reset_index()
	df["ratio"] = df.n.values/df.total.values
	return df
