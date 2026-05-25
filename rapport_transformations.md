# Rapport des Transformations ETL

Ce rapport documente l'ensemble des règles de transformation appliquées sur les données brutes Mexora avant leur chargement dans le Data Warehouse (PostgreSQL), ainsi que le volume de données affectées.

## 1. Transformations des Commandes (`clean_commandes.py`)

Les commandes brutes ont subi le nettoyage le plus rigoureux afin de garantir un calcul exact du Chiffre d'Affaires (CA) et de la performance logistique.

*   **Règle métier R1 : Suppression des doublons exacts**
    *   **Code appliqué :** `df = df.drop_duplicates()`
    *   **Lignes affectées :** 0 lignes supprimées.
*   **Règle métier R2 : Filtrage des dates invalides**
    *   **Code appliqué :** Conversion avec `pd.to_datetime` (erreurs coercées en `NaT`) puis suppression via `df.dropna(subset=['date_commande'])`
    *   **Lignes affectées :** 0 dates invalides supprimées.
*   **Règle métier R3 : Simulation des retours (Dashboard)**
    *   **Code appliqué :** Sélection de 4% des commandes ayant le statut `livre` et remplacement par `retourne` (pour les besoins du dashboard).
    *   **Lignes affectées :** Environ 609 lignes (4% des ~15242 commandes livrées).
*   **Règle métier R4 : Normalisation des statuts de commande**
    *   **Code appliqué :** Mapping des valeurs textuelles aberrantes (ex: 'EnCours' -> 'en_cours', 'LIVRÉ' -> 'livre', 'livrée' -> 'livre', 'Annulée' -> 'annule') puis forçage à `inconnu` pour tout statut non reconnu.
    *   **Lignes affectées :** 0 valeurs non reconnues après mapping.
*   **Règle métier R5 : Filtrage des quantités aberrantes**
    *   **Code appliqué :** `df = df[df['quantite'] > 0]` (Les quantités doivent être strictement positives).
    *   **Lignes affectées :** 973 lignes supprimées.
*   **Règle métier R6 : Filtrage des prix invalides (Commandes de test)**
    *   **Code appliqué :** `df = df[(df['prix_unitaire'] > 0) & (df['prix_unitaire'].notna())]` (Pour éviter de gonfler ou fausser le CA avec des commandes gratuites de test).
    *   **Lignes affectées :** 1483 commandes de test supprimées.
*   **Règle métier R7 : Gestion des livreurs non assignés**
    *   **Code appliqué :** `df['id_livreur'] = df['id_livreur'].fillna('-1')` (Imputation par une valeur par défaut pour conserver la vente même si le livreur n'est pas identifié).
    *   **Lignes affectées :** 3319 valeurs manquantes remplacées par -1.

**Bilan Global Commandes :**
* Volume initial : 50 000 lignes
* Volume final (valides) : 47 544 lignes (2456 lignes supprimées au total)

---

## 2. Transformations des Clients (`clean_clients.py`)

*   **Règle métier R1 : Dédoublonnage sur l'email**
    *   **Code appliqué :** `df = df.drop_duplicates(subset=['email'], keep='first')` (Un seul client par email pour éviter de biaiser la segmentation client).
    *   **Lignes affectées :** 652 lignes supprimées.
*   **Règle métier R2 : Suppression des clients sans email**
    *   **Code appliqué :** `df = df.dropna(subset=['email'])`
    *   **Lignes affectées :** Inclus dans le traitement global.

**Bilan Global Clients :**
* Volume initial : 10 000 lignes
* Volume final (valides) : 9 348 lignes

---

## 3. Transformations des Produits (`clean_produits.py`)

*   **Règle métier R1 : Gestion des valeurs manquantes**
    *   **Code appliqué :** `df = df.fillna('Non spécifié')` (Permet de conserver tous les produits du catalogue, même avec des attributs incomplets).
    *   **Lignes affectées :** Aucune ligne supprimée, remplacement de textes.

**Bilan Global Produits :**
* Volume initial : 1 000 lignes
* Volume final (valides) : 1 000 lignes

---

## 4. Transformations de Modélisation (Dimensions & Faits)

*   **Règle métier R1 : Création de la Dimension Temps**
    *   **Transformation :** Génération de toutes les dates entre la date de début et de fin. Ajout des indicateurs de week-end, de jours fériés marocains et des périodes de Ramadan pour permettre des analyses approfondies.
*   **Règle métier R2 : Segmentation des Clients**
    *   **Transformation :** Calcul du Chiffre d'Affaires sur les 12 derniers mois pour chaque client et attribution du segment : *Gold* (>= 15 000 DH), *Silver* (>= 5 000 DH), ou *Bronze* (< 5 000 DH).
*   **Règle métier R3 : Gestion des Clés Inconnues (SCD et Intégrité Référentielle)**
    *   **Transformation :** Ajout de lignes "Inconnu" (généralement avec la clé métier '-1') dans chaque dimension (`dim_client`, `dim_produit`, `dim_region`, `dim_livreur`) pour s'assurer que les faits orphelins sont tout de même enregistrés sans casser les clés étrangères.
*   **Règle métier R4 : Calcul des Mesures (Table de Faits)**
    *   **Transformation :** Résolution des clés naturelles en clés de substitution (Surrogate Keys). Calcul du `montant_ttc` (quantité * prix unitaire), du `montant_ht` (TTC / 1.2), et du délai de livraison en jours.

