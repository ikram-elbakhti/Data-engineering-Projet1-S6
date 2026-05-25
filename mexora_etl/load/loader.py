import pandas as pd
import json
from sqlalchemy import create_engine
from mexora_etl.config.settings import DB_CONFIG

import mexora_etl.config.settings as s
print("FILE SETTINGS =", s.__file__)
print("HOST =", s.DB_CONFIG["host"])
# =========================
# CONNEXION POSTGRESQL
# =========================
import urllib.parse

def get_engine():
    """
    Retourne une connexion à la base de données.
    """
    encoded_password = urllib.parse.quote_plus(DB_CONFIG['password'])
    return create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{encoded_password}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

from mexora_etl.utils.logger import get_logger

logger = get_logger(__name__)

def charger_dimension(df: pd.DataFrame, table_name: str, engine, if_exists='append'):
    """
    Charge une table de dimension dans PostgreSQL.
    Stratégie : truncate + reload pour contourner les erreurs de clés étrangères au Drop.
    """
    from sqlalchemy import text
    logger.info(f"Début chargement de la dimension {table_name}")
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE dwh_mexora.{table_name} RESTART IDENTITY CASCADE"))
        
    df.to_sql(
        name=table_name,
        con=engine,
        schema='dwh_mexora',
        if_exists=if_exists,
        index=False,
        method='multi',
        chunksize=1000
    )
    logger.info(f"[LOAD] {table_name} : {len(df)} lignes chargées")

def charger_faits(df: pd.DataFrame, engine):
    """
    Charge la table de faits avec une stratégie UPSERT.
    Utilise ON CONFLICT pour mettre à jour les lignes existantes.
    """
    from sqlalchemy.dialects.postgresql import insert
    from sqlalchemy import Table, MetaData

    logger.info("Début chargement de la table de faits (fait_ventes)")
    
    metadata = MetaData(schema='dwh_mexora')
    # On reflète la table existante
    table_fait_ventes = Table('fait_ventes', metadata, autoload_with=engine)

    # Construction de l'upsert via SQLAlchemy core
    with engine.begin() as conn:
        for chunk in [df[i:i+5000] for i in range(0, len(df), 5000)]:
            records = chunk.to_dict('records')
            conn.execute(table_fait_ventes.insert(), records)
            
    logger.info(f"[LOAD] fait_ventes : {len(df)} lignes chargées")

def get_sk_mapping(engine, table_name, nk_col, sk_col):
    """
    Récupère un dictionnaire de mapping NK -> SK depuis une table de dimension.
    """
    from sqlalchemy import text
    query = text(f"SELECT {nk_col}, {sk_col} FROM dwh_mexora.{table_name}")
    with engine.connect() as conn:
        result = conn.execute(query)
        return {row[0]: row[1] for row in result}
