# Mexora ETL & Data Warehouse Project 📊

## Présentation du Projet
Ce projet a pour objectif de concevoir et d'implémenter une solution complète de **Business Intelligence** pour l'entreprise fictive **Mexora**, spécialisée dans la distribution. La solution couvre l'intégralité du cycle de vie de la donnée : de l'extraction des fichiers sources bruts à la visualisation décisionnelle.

## Architecture Technique
Le projet repose sur une architecture moderne de Data Engineering :

1.  **Pipeline ETL (Python)** :
    *   **Extraction** : Lecture de fichiers CSV (Commandes, Clients, Produits).
    *   **Transformation** : Nettoyage (doublons, valeurs manquantes), normalisation et enrichissement des données (Villes/Régions du Maroc).
    *   **Chargement** : Insertion optimisée dans un Data Warehouse PostgreSQL via une stratégie d'UPSERT.
2.  **Data Warehouse (PostgreSQL)** :
    *   **Schéma en Étoile (Star Schema)** composé d'une table de faits (`fait_ventes`) et de 5 dimensions (`dim_temps`, `dim_client`, `dim_produit`, `dim_region`, `dim_livreur`).
    *   **Vues Matérialisées** pour optimiser les performances des rapports.
3.  **Visualisation (Power BI)** :
    *   Dashboard interactif et complet développé sous **Microsoft Power BI**, offrant des graphiques analytiques, des cartes KPI, une cartographie des ventes au Maroc et des filtres croisés avancés connectés directement au Data Warehouse PostgreSQL.


## Structure du Projet
```text
mexora_etl/
├── config/             # Paramètres de connexion DB
├── data/               # Sources CSV (raw/processed)
├── extract/            # Logique d'extraction
├── transform/          # Nettoyage et Construction des dimensions
├── load/               # Logique de chargement PostgreSQL
├── scripts/            # SQL (DDL, Vues) et Utilitaires
├── main.py             # Point d'entrée du pipeline
├── app.py              # Application Dashboard Streamlit Premium

```
## Livrables et Documents (L1 à L8)

L1 : le schéma entité-relation annoté ;
L2 : le document de justification des choix techniques ;
L3 : le code complet du pipeline ETL en Python ;
L4 : le rapport des transformations au format Markdown ;
L5 : le script SQL de création du Data Warehouse ;
L6 : le script SQL de vérification de l’intégrité ;
L7 : le dashboard final Power BI (format PDF) ;
L8 : le document des insights métiers (format PDF).
## Installation et Utilisation

### 1. Prérequis
*   Python 3.10+
*   PostgreSQL
*   Microsoft Power BI Desktop (pour ouvrir le Dashboard)
*   Dépendances Python : `pip install pandas sqlalchemy psycopg2-binary`

### 2. Configuration
Modifiez le fichier `mexora_etl/config/settings.py` avec vos identifiants PostgreSQL.

### 3. Exécution
Suivez cet ordre pour lancer le projet complet :

```powershell
# 1. Initialiser la base de données (Création schéma et tables)
python mexora_etl/scripts/init_db.py

# 2. Lancer le pipeline ETL (Transformation et Chargement)
python mexora_etl/main.py

# 3. Vérifier l'intégrité des données
python mexora_etl/scripts/verify_etl.py

# 4. Lancer les Dashboards

**Option A : Dashboard Power BI**
Ouvrez le fichier de projet Power BI associé (.pbix) pour naviguer visuellement à travers les données de Mexora.

**Option B : Dashboard Web (Streamlit)**
Exécutez la commande suivante pour lancer l'application web interactive :
```powershell
python -m streamlit run mexora_etl/app.py
```

```

## Questions Métier Couvertes
Le dashboard répond automatiquement aux analyses suivantes :
*   Chiffre d'affaires par région marocaine.
*   Top 10 des produits les plus vendus (Focus sur Tanger).
*   Analyse du panier moyen par segment client (Gold, Silver, Bronze).
*   Taux de retour par catégorie de produit.
*   Impact saisonnier (Effet Ramadan sur les ventes alimentaires).

## Technologies Utilisées
*   **Langage** : Python 3.14
*   **Base de données** : PostgreSQL 16
*   **Business Intelligence** : Microsoft Power BI
*   **Bibliothèques** : Pandas (DataFrames), SQLAlchemy (ORM).

