import psycopg2
from mexora_etl.config.settings import DB_CONFIG

def verify_etl():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cur = conn.cursor()
        
        tables = [
            'dwh_mexora.dim_temps',
            'dwh_mexora.dim_client',
            'dwh_mexora.dim_produit',
            'dwh_mexora.dim_region',
            'dwh_mexora.dim_livreur',
            'dwh_mexora.fait_ventes'
        ]
        
        print("-" * 40)
        print("RÉSULTATS DU CHARGEMENT ETL")
        print("-" * 40)
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"Table {table:25} : {count:6} lignes")
            
        # Vérification des vues matérialisées
        print("\nRafraîchissement des vues matérialisées...")
        views = [
            'reporting_mexora.mv_ca_mensuel',
            'reporting_mexora.mv_top_produits',
            'reporting_mexora.mv_performance_livreurs'
        ]
        for view in views:
            cur.execute(f"REFRESH MATERIALIZED VIEW {view}")
            cur.execute(f"SELECT COUNT(*) FROM {view}")
            count = cur.fetchone()[0]
            print(f"Vue {view:25} : {count:6} lignes")
            
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Erreur lors de la vérification : {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_etl()
