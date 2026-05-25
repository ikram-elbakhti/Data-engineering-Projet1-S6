import pandas as pd
from mexora_etl.utils.logger import get_logger

logger = get_logger(__name__)

def clean_produits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et transforme les données de produits.
    """
    logger.info("Début du nettoyage des produits")
    initial = len(df)

    # Casse incohérente sur les catégories
    if 'categorie' in df.columns:
        df['categorie'] = df['categorie'].str.strip().str.title()
    
    # Casse incohérente sur les sous-catégories
    if 'sous_categorie' in df.columns:
        df['sous_categorie'] = df['sous_categorie'].str.strip().str.title()

    # Prix catalogue nuls -> on met une valeur par défaut ou on garde pour traitement
    if 'prix_catalogue' in df.columns:
        df['prix_catalogue'] = df['prix_catalogue'].fillna(0)

    logger.info(f"[TRANSFORM] Produits terminés : {len(df)} lignes valides.")
    return df
