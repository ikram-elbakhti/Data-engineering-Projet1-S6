import pandas as pd
from datetime import date
import re
from mexora_etl.utils.logger import get_logger

logger = get_logger(__name__)

def clean_clients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et transforme les données de clients.
    """
    logger.info("Début du nettoyage des clients")
    initial = len(df)

    # R1 — Déduplication
    df['email_norm'] = df['email'].str.lower().str.strip()
    df = df.sort_values('date_inscription').drop_duplicates(subset=['email_norm'], keep='last')
    logger.info(f"[TRANSFORM] R1 doublons email : {initial - len(df)} lignes supprimées")

    # R2 — Standardisation du sexe
    mapping_sexe = {
        'm': 'm', 'f': 'f', '1': 'm', '0': 'f',
        'homme': 'm', 'femme': 'f', 'male': 'm', 'female': 'f',
        'h': 'm'
    }
    df['sexe'] = df['sexe'].str.lower().str.strip().map(mapping_sexe).fillna('inconnu')

    # R3 — Validation des dates de naissance
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    today = pd.Timestamp(date.today())
    df['age'] = (today - df['date_naissance']).dt.days // 365
    df.loc[(df['age'] < 16) | (df['age'] > 100), 'date_naissance'] = pd.NaT
    df['tranche_age'] = pd.cut(
        df['age'].fillna(0),
        bins=[0, 18, 25, 35, 45, 55, 65, 200],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    )

    # R4 — Validation email
    pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    df.loc[~df['email'].str.match(pattern_email, na=False), 'email'] = None

    logger.info(f"[TRANSFORM] Clients terminés : {len(df)} lignes valides.")
    return df
