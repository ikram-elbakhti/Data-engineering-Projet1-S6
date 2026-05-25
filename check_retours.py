import pandas as pd
from sqlalchemy import create_engine
from mexora_etl.config.settings import DB_CONFIG
import urllib.parse

password = urllib.parse.quote_plus(DB_CONFIG['password'])
url = f"postgresql://{DB_CONFIG['user']}:{password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(url)

print("--- Distribution des statuts ---")
print(pd.read_sql("SELECT statut_commande, COUNT(*) FROM dwh_mexora.fait_ventes GROUP BY 1", engine))

print("\n--- Taux de retour calculé ---")
print(pd.read_sql("""
    SELECT p.categorie, 
           COUNT(*) FILTER (WHERE f.statut_commande = 'retourne') as nb_retours,
           COUNT(*) as total
    FROM dwh_mexora.fait_ventes f
    JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
    GROUP BY 1
""", engine))
