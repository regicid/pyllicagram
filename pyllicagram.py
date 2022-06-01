import pandas as pd

def pyllicagram(gram,corpus="presse",debut=1789,fin=1950,resolution="default"):
	assert corpus in ["lemonde","livres","presse"], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
	assert resolution in ["default","annee","mois"], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
	df = pd.read_csv(f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{gram}_from={debut}_to={fin}")
	df["ratio"] = df.n.values/df.total.values
	return df
