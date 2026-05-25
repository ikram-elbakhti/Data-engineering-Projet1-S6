# Rapport Global du Projet Mexora ETL & BI

## 1. Contexte et Objectifs
L'entreprise e-commerce **Mexora**, opérant principalement au Maroc, nécessitait une solution robuste pour analyser et piloter ses performances. L'objectif de ce projet était de concevoir et de développer un système complet d'aide à la décision (Data to Insight), couvrant tout le cycle de vie de la donnée, de l'extraction au reporting interactif.

## 2. Architecture Globale
Le projet s'appuie sur une architecture moderne, scindée en 3 couches distinctes :
*   **Extraction et Nettoyage (ETL)** : Développé en Python (via Pandas), ce pipeline récupère les données hétérogènes (fichiers CSV, JSON) et les nettoie selon des règles métiers strictes.
*   **Stockage et Modélisation (Data Warehouse)** : Bâti sur PostgreSQL, avec une modélisation dimensionnelle (Star Schema) optimisée pour les requêtes d'analyse (OLAP).
*   **Visualisation (Dashboard & BI)** : Une application web développée avec Streamlit et un Dashboard analytique puissant sous Microsoft Power BI, permettant de naviguer visuellement à travers les KPIs et l'analyse spatio-temporelle de l'entreprise.

## 3. Réalisation de la Couche ETL (Python)
L'ETL est le cœur de la fiabilité de ce projet. Plus de 60 000 lignes de données brutes ont été traitées :
*   **Commandes** : Filtrage des prix et quantités négatifs (commandes de test), imputation des livreurs manquants par une valeur neutre "-1", et standardisation des statuts (livré, annulé, retourné, en_cours). Sur 50 000 commandes brutes, environ 2 450 ont été écartées car invalides.
*   **Clients** : Dédoublonnage strict basé sur les adresses emails.
*   **Produits** : Nettoyage via format JSON et gestion transparente des valeurs nulles.

## 4. Réalisation du Data Warehouse (PostgreSQL)
Le DWH a été modelé en étoile pour maximiser la vitesse des requêtes analytiques :
*   **Table de Faits** : `fait_ventes`, centralisant les montants, quantités, et délais de livraison avec les clés étrangères appropriées.
*   **Dimensions** : `dim_temps`, `dim_client`, `dim_produit`, `dim_region`, et `dim_livreur`.
*   **Optimisation** : Création de **Vues Matérialisées** (Materialized Views) agrégeant le CA mensuel et les performances des livreurs, garantissant un affichage quasi-instantané des graphiques complexes dans les outils de restitution.

## 5. Visualisation et Restitution des Données
Le rendu final est composé de deux solutions complémentaires et puissantes :

### A. Dashboard Interactif Power BI
Une solution de Business Intelligence complète a été développée sur Power BI pour offrir une vue macro et granulaire de l'activité, structurée en 3 onglets stratégiques :
*   **Dashboard Global** : Présentation des KPIs majeurs (CA Total : >363M DH, >142K unités vendues), une cartographie interactive des ventes (Casablanca, Rabat, Tanger), une comparaison annuelle de l'évolution mensuelle du CA (Year-over-Year), et la répartition équilibrée du CA par catégorie (Mode 34.3%, Électronique 33.8%, Alimentation 31.8%).
*   **Filtre et Analyse** : Exploration détaillée avec filtres croisés par année, trimestre et ville. Inclut un focus sur le Top 10 des produits et des livreurs (identifiant le fameux "Inconnu" comme gérant de gros volumes), ainsi qu'une analyse de l'impact du Ramadan sur les ventes.
*   **Analyse de la ville de Tanger** : Vue filtrée démontrant le comportement spécifique des clients tangérois. On y observe le poids immense du segment "Gold" (57.74% du CA régional avec un panier moyen de 8932 DH), et des taux de retour stables autour de 1.35%.

### B. Application Web Streamlit (Premium)
Un dashboard web sur-mesure au design sombre interactif et fluide, découpé en modules clés :
*   Évolution et Géographie
*   Focus Ville (Top Produits)
*   Segments Clients
*   Analyse des Retours
*   Effet Ramadan
*   Performance Logistique (Mettant en lumière les taux de retards inacceptables chez certains prestataires).

## 6. Conclusion et Perspectives
Le projet est un succès technique et métier. Mexora dispose désormais d'un outil End-to-End complet, alliant la souplesse applicative de Streamlit et la profondeur analytique de Power BI.
*   **Perspectives** : La prochaine étape consisterait à orchestrer ce pipeline Python via un outil comme **Apache Airflow** pour une exécution quotidienne automatisée, ainsi qu'à intégrer des APIs externes (données météo ou coûts de campagnes publicitaires) pour enrichir le modèle de données.
