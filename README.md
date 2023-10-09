# pyllicagram
Un micro package python pour importer des données de [Gallicagram](https://shiny.ens-paris-saclay.fr/app/gallicagram).

## Installation
Tout simplement :
```console
$ pip install pyllicagram
```

Ou, si vous préférez la subtilité, vous pouvez cloner ce github et vous diriger dans le dossier créé :
```console
$ git clone https://github.com/regicid/pyllicagram
$ cd pyllicagram
```
Vous pouvez maintenant lancer python (dans ce directory!)

## Usage dans python
Le package contient trois fonctions, qui correspondent aux trois routes de l'API décrites [ici]](https://regicid.github.io/api) : pyllicagram (correspondant à la route query), contain et joker (correspondant aux routes éponymes). 

Importez les fonctions avec :
```python
from pyllicagram import pyllicagram
from pyllicagram import contain
from pyllicagram import joker
```

Vous pouvez utiliser la fonction de base comme ceci, pour obtenir les fréquences des mots recherchés dans le corpus voulu, sur la période vulue, à la résolution voulue :
```python
pyllicagram(recherche="francis",corpus="presse",debut=1789,fin=1950,resolution="annee")
```
Le seul argument nécessaire est `recherche`. Par défaut, les fonction cherche dans le corpus de presse de Gallica, de 1789 à 1950, en résolution mensuelle. Si vous ne spéficiez pas la résolution, la résolution la plus fine disponible est utilisée.

La fonction vous retourne un tableau pandas, avec pour colonnes le nombre d'occurrences (`n`), le nombre total de mots sur la période (`total`), la fréquence du mot calculée comme le rapport des deux (`ratio`), le syntagme recherché (`gram`), l'année (`annee`) et selon la résolution le `mois` et le `jour`.

Pour rechercher plusieurs syntagmes, vous pouvez passer une liste dans l'argument `recherche`. 
```python
pyllicagram(["francis","roger"])

```
En spécifiant `somme = True` dans la fonction, elle retournera la somme des fréquences des mots recherchés, ce qui correspond à la recherche "francis+roger" dans l'interface graphique de Gallicagram.

La fonction `contain` dénombre les 3gram (ou 4gram sur le corpus "lemonde") contenant à la fois `mot1` et `mot2`. Elle ne dispose pas encore de paramètre de résolution, mais vous pouvez faire le .groubpy vous-mêmes, bande de feignasses. Seuls les deux premiers arguments sont nécessaires, les défauts sont les mêmes que la première fonction (et le résultat est structuré de la même façon).

```python
contain(mot1="francis",mot2="grand",corpus="presse",debut=1789,fin=1950)
```

La fonction `joker` vous donne ce qui suit le plus souvent le mot (ou groupe de mots) donné, avec le nombre total d'occurrences (colonne `tot`). De même, seul l'argument `gram` est nécessaire.

```python
joker(gram="francis",corpus="presse",debut=1789,fin=1950,after=True,n_joker=20)
```

## Corpus
Ce package permet seulement de chercher dans les corpus qui ont été tokénisés pour le projet Gallicagram, que voici :

|Titre                         |Période (conseillée)      |Volume (en mots)|Code API          |Longueur max|Résolution                    |Seuils                 |
|------------------------------|--------------------------|----------------|------------------|------------|------------------------------|-----------------------|
|Le Monde                      |1944-2023                 |1,5 milliards   |lemonde           |4gram       |Journalière                   |Aucun                  |
|Presse de Gallica             |1789-1950                 |57 milliards    |presse            |3gram       |Mensuelle                     |2gram>1,3gram>1        |
|Livres de Gallica             |1600-1940                 |16 milliards    |livres            |5gram       |Annuelle                      |2gram>1, etc           |
|Deutsches Zeitungsportal (DDB)|1780-1950                 |39 milliards    |ddb               |2gram       |Mensuelle                     |1gram > 1, 2gram>2     |
|American Stories              |1798-1963                 |20 milliards    |american_stories  |3gram       |Annuelle (mensuelle à venir ?)|1gram>1,2gram>2,3gram>3|
|Journal de Paris              |1777-1827                 |86 millions     |paris             |2gram       |Journalière                   |2gram>1                |
|Moniteur Universel            |1789-1869                 |511 millions    |moniteur          |2gram       |Journalière                   |2gram>1                |
|Journal des Débats            |1789-1944                 |1,2 milliards   |journal_des_debats|1gram       |Journalière                   |Aucun                  |
|La Presse                     |1836-1869                 |253 millions    |la_presse         |2gram       |Journalière                   |2gram>1                |
|Le Constitutionnel            |1821-1913 (très lacunaire)|64 millions     |constitutionnel   |2gram       |Journalière                   |2gram>1                |
|Le Figaro                     |1854-1952                 |870 millions    |figaro            |2gram       |Journalière                   |2gram>1                |
|Le Temps                      |1861-1942                 |1 milliard      |temps             |2gram       |Journalière                   |2gram>1                |
|Le Petit Journal              |1863-1942                 |745 millions    |petit_journal     |2gram       |Journalière                   |2gram>1                |
|Le Petit Parisien             |1876-1944                 |631 millions    |petit_parisien    |2gram       |Journalière                   |2gram>1                |
|L’Humanité                    |1904-1952                 |318 millions    |huma              |2gram       |Journalière                   |2gram>1                |
|Opensubtitles (français)      |1935-2020                 |17 millions     |substitles        |3gram       |Annuelle                      |Aucun                  |
|Opensubtitles (anglais)       |1930-2020                 |102 millions    |subtitles_en      |3gram       |Annuelle                      |Aucun                  |



## Pour les passionnés
Plus d'informations dans notre [preprint](https://osf.io/preprints/socarxiv/84bf3/) consacré au projet et dans la notice du [site](https://shiny.ens-paris-saclay.fr/app/gallicagram).

## Usage en ligne de commande
Grâce à [Laurent Vanni](https://github.com/lvanni/), vous pouvez utiliser le programme directement en ligne de commande et génère un fichier "results.csv" où les valeurs sont séparées par des tablulations. Pour ce faire, clonez (ou si vous êtes un barbare, téléchargez) ce Github, et allez dans le directory pyllicagram (ou, cela revient au même, bougez le fichier pyllicagram.py dans le directory où vous souhaitez l'utiliser). Puis, pour la recherche d'un mot :
```console
$ python3 pyllicagram.py france
```

Pour la recherche de plusieurs mots (séparés par des virgules) :
```console
$ python3 pyllicagram.py france,nation
```

Pour la recherche de la somme de plusieurs mots (séparés par des +):
```console
$ python3 pyllicagram.py france+nation
```

Pour la recherche d’une expression (entre guillemets) : 
```console
$ python3 pyllicagram.py "la france"
```

Pour passer les options :

Choix du corpus parmi [lemonde, livres, presse] (presse par défaut) :
```console
$ python3 pyllicagram.py france -c livres
```

Choix de la date de début (1789 par défaut) :
```console
$ python3 pyllicagram.py france -d 1800
```

Choix de la date de fin (1950 par défaut) :
```console
$ python3 pyllicagram.py france -d 1900
```

Choix de la resolution parmi [default, annee, mois] :
```console
$ python3 pyllicagram.py france -r annee
```

Vous pouvez mélanger les options :
```console
$ python3 pyllicagram.py france -d 1800 -f 1900 -r annee 
```
