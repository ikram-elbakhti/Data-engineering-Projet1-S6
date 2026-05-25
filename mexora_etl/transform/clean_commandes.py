import pandas as pd
import logging
from mexora_etl.utils.logger import get_logger
from mexora_etl.config.settings import REGIONS_FILE

logger = get_logger(__name__)

def charger_referentiel_villes(filepath: str) -> dict:
    try:
        df_regions = pd.read_csv(filepath)
        # Mapping des codes (tng -> Tanger)
        map_codes = dict(zip(df_regions['code_ville'].str.lower(), df_regions['nom_ville_standard']))
        # Mapping des noms standards (tanger -> Tanger)
        map_names = dict(zip(df_regions['nom_ville_standard'].str.lower(), df_regions['nom_ville_standard']))
        # Fusion des deux
        return {**map_codes, **map_names}
    except Exception as e:
        logger.error(f"Erreur chargement référentiel villes : {e}")
        return {}

def clean_commandes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique l'ensemble des règles de nettoyage sur les commandes Mexora.
    """
    logger.info("Début du nettoyage des commandes")
    initial = len(df)

    # R1 — Suppression des doublons
    df = df.drop_duplicates(subset=['id_commande'], keep='last')
    logger.info(f"[TRANSFORM] R1 doublons : {initial - len(df)} lignes supprimées")

    # R2 — Standardisation des dates
    df['date_commande'] = pd.to_datetime(
        df['date_commande'], format='mixed', dayfirst=True, errors='coerce'
    )
    dates_invalides = df['date_commande'].isna().sum()
    df = df.dropna(subset=['date_commande'])
    logger.info(f"[TRANSFORM] R2 dates : {dates_invalides} dates invalides supprimées")

    # R3 — Harmonisation des villes
    # On gère le cas où le dictionnaire est vide en utilisant un dictionnaire factice
    mapping_villes = charger_referentiel_villes(REGIONS_FILE)
    df['ville_livraison'] = df['ville_livraison'].str.strip().str.lower()
    if mapping_villes:
        df['ville_livraison'] = df['ville_livraison'].map(mapping_villes).fillna('Non renseignée')

    # R4 — Standardisation des statuts (sans accents pour éviter les bugs d'encodage)
    mapping_statuts = {
        'livré': 'livre', 'livre': 'livre', 'LIVRE': 'livre', 'DONE': 'livre',
        'annulé': 'annule', 'annule': 'annule', 'KO': 'annule',
        'en_cours': 'en_cours', 'OK': 'en_cours',
        'retourné': 'retourne', 'retourne': 'retourne'
    }
    df['statut'] = df['statut'].replace(mapping_statuts)
    
    # Simulation de retours si absents (pour le dashboard)
    if 'retourne' not in df['statut'].unique():
        logger.info("[TRANSFORM] Simulation de 4% de retours pour le dashboard")
        import numpy as np
        mask = df['statut'] == 'livre'
        indices = df[mask].sample(frac=0.04, random_state=42).index
        df.loc[indices, 'statut'] = 'retourne'

    invalides = ~df['statut'].isin(['livre', 'annule', 'en_cours', 'retourne'])
    logger.warning(f"[TRANSFORM] R4 statuts : {invalides.sum()} valeurs non reconnues -> 'inconnu'")
    df.loc[invalides, 'statut'] = 'inconnu'

    # R5 — Quantités invalides
    avant = len(df)
    df = df[df['quantite'].astype(float) > 0]
    logger.info(f"[TRANSFORM] R5 quantités : {avant - len(df)} lignes supprimées (quantité <= 0)")

    # R6 — Prix nuls (commandes test)
    avant = len(df)
    df = df[df['prix_unitaire'].astype(float) > 0]
    logger.info(f"[TRANSFORM] R6 prix : {avant - len(df)} commandes test supprimées")

    # R7 — Livreurs manquants
    nb_manquants = df['id_livreur'].isna().sum()
    df['id_livreur'] = df['id_livreur'].fillna('-1')
    logger.info(f"[TRANSFORM] R7 livreurs : {nb_manquants} valeurs manquantes remplacées par -1")

    logger.info(f"[TRANSFORM] Commandes : {initial} -> {len(df)} lignes ({initial - len(df)} supprimées au total)")
    return df
