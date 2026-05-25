import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from mexora_etl.config.settings import DB_CONFIG
import os

def init_database():
    # Connexion à la base par défaut 'postgres' pour créer la base cible
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Vérifier si la base de données existe
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_CONFIG['database']}';")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Création de la base de données {DB_CONFIG['database']}...")
            cur.execute(f"CREATE DATABASE {DB_CONFIG['database']};")
        else:
            print(f"La base de données {DB_CONFIG['database']} existe déjà.")
            
        cur.close()
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base : {e}")
        return
    finally:
        if conn:
            conn.close()

    # Connexion à la base cible pour exécuter le script SQL
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cur = conn.cursor()
        
        sql_file_path = os.path.join('mexora_etl', 'scripts', 'create_dwh.sql')
        print(f"Exécution du script SQL : {sql_file_path}")
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        cur.execute(sql_script)
        conn.commit()
        print("Initialisation du Data Warehouse réussie !")
        
        cur.close()
    except Exception as e:
        print(f"Erreur lors de l'exécution du script SQL : {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database()
