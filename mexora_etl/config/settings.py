# =========================
# CONFIGURATION POSTGRESQL
# =========================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mexora_db",
    "user": "postgres",
    "password": "ikram.elb@20"
}
print("DB_CONFIG =", DB_CONFIG)
# =========================
# CHEMINS DES DONNÉES
# =========================

DATA_PATH = "mexora_etl/data/raw/"

CLIENTS_FILE = DATA_PATH + "clients_mexora.csv"
COMMANDES_FILE = DATA_PATH + "commandes_mexora.csv"
PRODUITS_FILE = DATA_PATH + "produits_mexora.json"
REGIONS_FILE = DATA_PATH + "regions_maroc.csv"