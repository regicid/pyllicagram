# pyllicagram
Un micro package python pour importer des données de [Gallicagram](https://shiny.ens-paris-saclay.fr/app/gallicagram).

## Installation
Assurez-vous que `pandas` est installé (sinon...sérieusement ?). Allez dans votre Terminal, clonez ce github et dirigez vous dans le dossier créé :
```console
git clone https://github.com/regicid/pyllicagram
cd pyllicagram
```
Vous pouvez maintenant lancer python (dans ce directory!)

## Usage
Importez la fonction avec :
```python
from pyllicagram import pyllicagram
```

Vous pouvez l'utiliser comme ceci:
```python
pyllicagram(recherche="francis",corpus="presse",debut=1789,fin=1950,resolution="annee")
```
Le seul argument nécessaire est `recherche`. Par défaut, la fonction cherche dans le corpus de presse de Gallica, de 1789 à 1950, en résolution mensuelle. Si vous ne spéficiez pas la résolution, la fonction vous retourne la résolution la plus fine disponible.

Pour rechercher plusieurs syntagmes, vous pouvez passer une liste dans l'argument `recherche`. 
```python
pyllicagram(["francis","roger"])

```
En spécifiant `somme = True` dans la fonction, elle retournera la somme des fréquences des mots recherchés, ce qui correspond à la recherche "francis+roger" dans l'interface graphique de Gallicagram.

## Corpus
Ce package permet seulement de chercher dans les corpus qui ont été tokénisés pour le projet Gallicagram, c'est-à-dire :
* La presse de Gallica (corpus="presse"). 3 millions de numéros, fiable à partir de 1789 et jusqu'en 1950 (la faute aux droits d'auteur). Résolution mensuelle.
![gallica_presse](man/figures/gallica_presse.png)
* Les livres de Gallica (corpus="livres"). 300 000 "monographies", de plus en plus fiable au fil des XVIIe et XVIIIe siècle, et ce jusqu'en 1950 (même raison). Résolution annuelle.
![gallica_livres](man/figures/gallica_livres.png)
* Les archives du Monde de décembre 1944 au 22 février 2022 (corpus="lemonde"). Fiable tout au long de la période, résolution journalière. Impeccablement océrisé, contrairement à Gallica.
![lemonde](man/figures/lemonde.png)
## Pour les passionnés
Plus d'informations dans notre [preprint](https://osf.io/preprints/socarxiv/84bf3/) consacré au projet et dans la notice sur le [site](https://shiny.ens-paris-saclay.fr/app/gallicagram).
