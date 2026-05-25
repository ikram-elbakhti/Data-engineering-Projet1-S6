# ============================================================
# extractor.py — Extraction des données brutes par source
# ============================================================
# Ce module contient les fonctions responsables de la lecture
# des données depuis les différentes sources :
#   - Fichiers CSV / Excel
#   - Base de données source (si applicable)
#   - API REST (si applicable)
# Chaque fonction retourne un pandas DataFrame brut, sans
# aucune transformation.
# ============================================================

import pandas as pd
from mexora_etl.utils.logger import get_logger
from mexora_etl.config.settings import COMMANDES_FILE, CLIENTS_FILE, PRODUITS_FILE

logger = get_logger(__name__)


# ------------------------------------------------------------
# Extraction des commandes
# ------------------------------------------------------------
def extract_commandes() -> pd.DataFrame:
    """
    Lit le fichier source des commandes et retourne un DataFrame brut.

    Returns:
        pd.DataFrame: Données brutes des commandes.

    Raises:
        FileNotFoundError: Si le fichier source est introuvable.
    """
    logger.info(f"Extraction des commandes depuis : {COMMANDES_FILE}")
    try:
        df = pd.read_csv(COMMANDES_FILE, encoding="utf-8", sep=",")
        logger.info(f"  -> {len(df)} lignes extraites.")
        return df
    except FileNotFoundError:
        logger.error(f"Fichier introuvable : {COMMANDES_FILE}")
        raise


# ------------------------------------------------------------
# Extraction des clients
# ------------------------------------------------------------
def extract_clients() -> pd.DataFrame:
    """
    Lit le fichier source des clients et retourne un DataFrame brut.

    Returns:
        pd.DataFrame: Données brutes des clients.
    """
    logger.info(f"Extraction des clients depuis : {CLIENTS_FILE}")
    try:
        df = pd.read_csv(CLIENTS_FILE, encoding="utf-8", sep=",")
        logger.info(f"  -> {len(df)} lignes extraites.")
        return df
    except FileNotFoundError:
        logger.error(f"Fichier introuvable : {CLIENTS_FILE}")
        raise


# ------------------------------------------------------------
# Extraction des produits
# ------------------------------------------------------------
def extract_produits() -> pd.DataFrame:
    """
    Lit le fichier source des produits et retourne un DataFrame brut.

    Returns:
        pd.DataFrame: Données brutes des produits.
    """
    import json
    logger.info(f"Extraction des produits depuis : {PRODUITS_FILE}")
    try:
        with open(PRODUITS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data['produits'])
        logger.info(f"  -> {len(df)} lignes extraites.")
        return df
    except FileNotFoundError:
        logger.error(f"Fichier introuvable : {PRODUITS_FILE}")
        raise


# ------------------------------------------------------------
# Point d'entrée (test rapide)
# ------------------------------------------------------------
if __name__ == "__main__":
    commandes = extract_commandes()
    clients   = extract_clients()
    produits  = extract_produits()
    print(commandes.head())
    print(clients.head())
    print(produits.head())
