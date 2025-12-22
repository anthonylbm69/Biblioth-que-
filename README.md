# Système de gestion de Bibliothèque API (FastAPI)

Une API REST robuste pour la gestion d'une bibliothèque, permettant de gérer les auteurs, les livres et les emprunts. Développée avec **Python**, **FastAPI** et **SQLModel**.

## Fonctionnalités

* **Gestion des Auteurs** : Création, recherche et consultation des profils d'auteurs.
* **Gestion des Livres** : CRUD complet (Création, Lecture, Mise à jour, Suppression).

* **Système d'Emprunts** : Suivi des livres empruntés et gestion des statuts (en cours, rendu, en retard).
* **Validation de données** : Utilisation de Pydantic pour garantir l'intégrité des données (codes langues ISO, années de publication, etc.).

## Stack Technique

* **Framework** : [FastAPI](https://fastapi.tiangolo.com/)
* **ORM** : [SQLModel](https://sqlmodel.tiangolo.com/) (basé sur SQLAlchemy et Pydantic)
* **Serveur** : Uvicorn
* **Base de données** : SQLite

## Prérequis

* Python 3.10 ou supérieur
* Un gestionnaire de paquets (`pip`)

## ⚙️ Installation

1. **Cloner le projet** :
```bash
git clone https://github.com/anthonylbm69/Biblioth-que-.git

```


2. **Créer un environnement virtuel** :

## Environnement virtuel
```bash
python -m venv mon_venv

```
## Activation
```bash
source venv/bin/activate

```

3. **Installer les dépendances** :
```bash
pip freeze > requirements.txt

```

4. **Git Ignore** : 
```bash
git init
echo "tpBibli/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore    

```


## Lancement de l'application

Pour démarrer le serveur de développement :

```bash
uvicorn app.main:app --reload

```

L'API sera disponible sur : `http://127.0.0.1:8000`

## Documentation de l'API

Une fois le serveur lancé, vous pouvez accéder à la documentation interactive :

* **Swagger UI** : `http://127.0.0.1:8000/docs` (pour tester les endpoints)
* **ReDoc** : `http://127.0.0.1:8000/redoc`

## Structure du Projet

```text
app/
├── core/           # Configuration (Base de données, sécurité)
├── models/         # Modèles SQLModel (Tables de la DB)
├── routers/        # Endpoints de l'API (Livres, Auteurs, Emprunts)
├── schemas/        # Schémas Pydantic (Validation Entrée/Sortie)
└── main.py         # Point d'entrée de l'application

```
