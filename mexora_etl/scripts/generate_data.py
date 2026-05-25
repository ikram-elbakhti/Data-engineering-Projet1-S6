import pandas as pd
import numpy as np
import random
from faker import Faker
import json
from datetime import datetime, timedelta

#initialisation(faker)
fake = Faker("fr_FR")
random.seed(42)
np.random.seed(42)

#------------------------------------------------------------------------------------------------------------
# Creation dataset régions (csv) avec 5 villes
#------------------------------------------------------------------------------------------------------------
regions = [
    ["TNG", "Tanger", "Tanger-Assilah", "Tanger-Tetouan-Al Hoceima", "Nord", 1200000, 90000],
    ["CAS", "Casablanca", "Casablanca-Settat", "Centre", 3500000, 20000],
    ["RAB", "Rabat", "Rabat-Sale-Kenitra", "Centre", 580000, 10000],
    ["MRK", "Marrakech", "Marrakech-Safi", "Sud", 950000, 40000],
    ["AGD", "Agadir", "Souss-Massa", "Sud", 600000, 80000],
]

df_regions = pd.DataFrame(regions, columns=[
    "code_ville","nom_ville_standard","province",
    "region_admin","zone_geo","population","code_postal"
])

df_regions.to_csv("data/raw/regions_maroc.csv", index=False)


#------------------------------------------------------------------------------------------------------------
# Creation dataset clients
#------------------------------------------------------------------------------------------------------------

def generate_clients(n=10000):
    clients = []

    villes = ["Tanger", "CAS", "tanger", "TNG", "Rabat", "RAB"]

    for i in range(n):
        nom = fake.last_name()
        prenom = fake.first_name()

        email = fake.email()

        # ❌ erreurs volontaires
        if random.random() < 0.05:
            email = "invalid_email"

        sexe_options = ["m", "f", "Homme", "Femme", "1", "0"]
        sexe = random.choice(sexe_options)

        ville = random.choice(villes)

        # âge invalide parfois
        birth = fake.date_of_birth(minimum_age=10, maximum_age=90)
        if random.random() < 0.01:
            birth = fake.date_of_birth(minimum_age=150, maximum_age=200)

        clients.append([
            f"C{i:05}",
            nom,
            prenom,
            email,
            birth,
            sexe,
            ville,
            fake.phone_number(),
            fake.date_between("-3y", "today"),
            random.choice(["Facebook","Instagram","Google","TikTok"])
        ])

    return pd.DataFrame(clients, columns=[
        "id_client","nom","prenom","email","date_naissance",
        "sexe","ville","telephone","date_inscription","canal_acquisition"
    ])

df_clients = generate_clients()
df_clients.to_csv("data/raw/clients_mexora.csv", index=False)


#------------------------------------------------------------------------------------------------------------
# Creation dataset produits
#------------------------------------------------------------------------------------------------------------
def generate_produits(n=1000):
    categories = ["Electronique","Mode","Alimentation"]
    data = []

    for i in range(n):
        cat = random.choice(categories)

        # erreurs volontaires
        if random.random() < 0.1:
            cat = cat.lower()  # casse incohérente

        prix = round(random.uniform(50, 20000), 2)

        if random.random() < 0.05:
            prix = None  # erreur

        data.append({
            "id_produit": f"P{i:05}",
            "nom": fake.word() + " " + fake.word(),
            "categorie": cat,
            "sous_categorie": random.choice(["A","B","C"]),
            "marque": fake.company(),
            "fournisseur": fake.company(),
            "prix_catalogue": prix,
            "origine_pays": random.choice(["USA","France","China","Germany"]),
            "date_creation": str(fake.date_between("-2y","today")),
            "actif": random.choice([True, False])
        })

    return {"produits": data}

produits = generate_produits()

with open("data/raw/produits_mexora.json","w",encoding="utf-8") as f:
    json.dump(produits, f, indent=4, ensure_ascii=False)

#------------------------------------------------------------------------------------------------------------
# Creation dataset commandes
#------------------------------------------------------------------------------------------------------------

def generate_commandes(n=50000):
    commandes = []

    clients = df_clients["id_client"].tolist()
    produits = [f"P{i:05}" for i in range(1000)]

    villes = ["tanger","TNG","Tnja","CAS","Rabat"]

    for i in range(n):

        date = fake.date_between("-2y","today")

        # formats de date différents
        if random.random() < 0.3:
            date = date.strftime("%d/%m/%Y")
        elif random.random() < 0.3:
            date = date.strftime("%b %d %Y")

        quantite = random.randint(1,5)

        if random.random() < 0.02:
            quantite = -1 * quantite  # erreur

        prix = round(random.uniform(100,5000),2)

        if random.random() < 0.03:
            prix = 0  # erreur

        commandes.append([
            f"CMD{i:06}",
            random.choice(clients),
            random.choice(produits),
            date,
            quantite,
            prix,
            random.choice(["OK","KO","DONE"]),
            random.choice(villes),
            random.choice(["CASH","CARD"]),
            f"L{random.randint(1,50)}" if random.random() > 0.07 else None,
            fake.date_between("-1y","today")
        ])

    return pd.DataFrame(commandes, columns=[
        "id_commande","id_client","id_produit","date_commande",
        "quantite","prix_unitaire","statut","ville_livraison",
        "mode_paiement","id_livreur","date_livraison"
    ])

df_commandes = generate_commandes()
df_commandes.to_csv("data/raw/commandes_mexora.csv", index=False)

print("Données générées avec succès ✅")