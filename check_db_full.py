import pandas as pd
from sqlalchemy import create_engine, text
from mexora_etl.config.settings import DB_CONFIG
import urllib.parse

password = urllib.parse.quote_plus(DB_CONFIG['password'])
url = f"postgresql://{DB_CONFIG['user']}:{password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(url)

with engine.connect() as conn:
    print("--- Vérification des Vues ---")
    res = conn.execute(text("SELECT COUNT(*) FROM reporting_mexora.mv_ca_mensuel")).fetchone()
    print(f"Lignes dans mv_ca_mensuel : {res[0]}")
    
    print("\n--- Segments dans dim_client ---")
    print(pd.read_sql("SELECT segment_client, COUNT(*) FROM dwh_mexora.dim_client GROUP BY 1", engine))

    print("\n--- Statuts dans fait_ventes ---")
    print(pd.read_sql("SELECT statut_commande, COUNT(*) FROM dwh_mexora.fait_ventes GROUP BY 1", engine))
    
    print("\n--- Jointure Fait <-> Client ---")
    print(pd.read_sql("""
        SELECT c.segment_client, COUNT(*) 
        FROM dwh_mexora.fait_ventes f 
        JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client_sk 
        WHERE f.statut_commande = 'livre'
        GROUP BY 1
    """, engine))
