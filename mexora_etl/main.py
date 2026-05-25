import logging
from datetime import datetime
import os

from mexora_etl.utils.logger import get_logger
from mexora_etl.extract.extractor import extract_commandes, extract_produits, extract_clients
from mexora_etl.transform.clean_commandes import clean_commandes as transform_commandes
from mexora_etl.transform.clean_clients import clean_clients as transform_clients
from mexora_etl.transform.clean_produits import clean_produits as transform_produits
from mexora_etl.transform.build_dimensions import (
    build_dim_temps, build_dim_client, build_dim_produit, 
    build_dim_region, build_dim_livreur, build_fait_ventes
)
from mexora_etl.load.loader import get_engine, charger_dimension, charger_faits
from mexora_etl.config.settings import REGIONS_FILE
import pandas as pd

logger = get_logger(__name__)

def extract_regions(filepath: str) -> pd.DataFrame:
    """Extraction additionnelle pour les régions non gérée dans extractor.py"""
    logger.info(f"Extraction des régions depuis : {filepath}")
    return pd.read_csv(filepath, encoding="utf-8", sep=",")

def run_pipeline():
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("DÉMARRAGE PIPELINE ETL MEXORA")
    logger.info("=" * 60)

    try:
        # 1. EXTRACT
        logger.info("--- PHASE EXTRACT ---")
        df_commandes_raw = extract_commandes()
        df_produits_raw  = extract_produits()
        df_clients_raw   = extract_clients()
        df_regions       = extract_regions(REGIONS_FILE)

        # 2. TRANSFORM
        logger.info("--- PHASE TRANSFORM ---")
        df_commandes = transform_commandes(df_commandes_raw)
        df_clients   = transform_clients(df_clients_raw)
        df_produits  = transform_produits(df_produits_raw)

        dim_temps    = build_dim_temps('2020-01-01', '2026-12-31')
        dim_client   = build_dim_client(df_clients, df_commandes)
        dim_produit  = build_dim_produit(df_produits)
        dim_region   = build_dim_region(df_regions)
        dim_livreur  = build_dim_livreur(df_commandes)

        # 3. LOAD
        logger.info("--- PHASE LOAD ---")
        engine = get_engine()

        # A. Charger les dimensions d'abord
        charger_dimension(dim_temps,   'dim_temps',   engine)
        charger_dimension(dim_client,  'dim_client',  engine)
        charger_dimension(dim_produit, 'dim_produit', engine)
        charger_dimension(dim_region,  'dim_region',  engine)
        charger_dimension(dim_livreur, 'dim_livreur', engine)

        # B. Récupérer les mappings NK -> SK depuis la DB
        from mexora_etl.load.loader import get_sk_mapping
        map_client  = get_sk_mapping(engine, 'dim_client',  'id_client_nk',  'id_client_sk')
        map_produit = get_sk_mapping(engine, 'dim_produit', 'id_produit_nk', 'id_produit_sk')
        map_region  = get_sk_mapping(engine, 'dim_region',  'ville',         'id_region')
        map_livreur = get_sk_mapping(engine, 'dim_livreur', 'id_livreur_nk', 'id_livreur')

        # C. Construire la table de faits avec les SK
        logger.info("--- PHASE TRANSFORM (FAITS) ---")
        fait_ventes = build_fait_ventes(df_commandes, map_client, map_produit, map_region, map_livreur)

        # D. Charger les faits
        charger_faits(fait_ventes, engine)

        # E. Rafraîchir les vues de reporting
        logger.info("--- PHASE FINAL (VUES) ---")
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("REFRESH MATERIALIZED VIEW reporting_mexora.mv_ca_mensuel"))
            conn.execute(text("REFRESH MATERIALIZED VIEW reporting_mexora.mv_top_produits"))
            conn.execute(text("REFRESH MATERIALIZED VIEW reporting_mexora.mv_performance_livreurs"))
            conn.commit()
        logger.info("Vues de reporting rafraîchies.")

        duree = (datetime.now() - start).seconds
        logger.info(f"PIPELINE TERMINÉ EN {duree} secondes")

    except Exception as e:
        logger.error(f"ERREUR PIPELINE : {e}", exc_info=True)
        raise

if __name__ == '__main__':
    run_pipeline()
