import pandas as pd
from mexora_etl.utils.logger import get_logger

logger = get_logger(__name__)

import pandas as pd
from mexora_etl.utils.logger import get_logger

logger = get_logger(__name__)

def build_dim_temps(date_debut: str, date_fin: str) -> pd.DataFrame:
    """
    Génère la dimension temporelle complète entre deux dates.
    Inclut les jours fériés marocains et les périodes Ramadan.
    """
    dates = pd.date_range(start=date_debut, end=date_fin, freq='D')

    # Jours fériés marocains (liste partielle — à compléter)
    feries_maroc = [
        '2024-01-01',  # Nouvel An
        '2024-01-11',  # Manifeste de l'Indépendance
        '2024-05-01',  # Fête du Travail
        '2024-07-30',  # Fête du Trône
        '2024-08-14',  # Allégeance Oued Eddahab
        '2024-11-06',  # Marche Verte
        '2024-11-18',  # Fête de l'Indépendance
    ]

    # Périodes Ramadan 2022-2025 (approximatif)
    ramadan_periodes = [
        ('2022-04-02', '2022-05-01'),
        ('2023-03-22', '2023-04-20'),
        ('2024-03-10', '2024-04-09'),
    ]

    df = pd.DataFrame({
        'id_date':       dates.strftime('%Y%m%d').astype(int),
        'date_complete': dates,
        'jour':          dates.day,
        'mois':          dates.month,
        'trimestre':     dates.quarter,
        'annee':         dates.year,
        'semaine':       dates.isocalendar().week,
        'libelle_jour':  dates.strftime('%A'),
        'libelle_mois':  dates.strftime('%B'),
        'est_weekend':   dates.dayofweek >= 5,
        'est_ferie_maroc': dates.strftime('%Y-%m-%d').isin(feries_maroc),
    })

    # Calcul période Ramadan
    df['periode_ramadan'] = False
    for debut, fin in ramadan_periodes:
        masque = (df['date_complete'] >= debut) & (df['date_complete'] <= fin)
        df.loc[masque, 'periode_ramadan'] = True

    return df[['id_date', 'jour', 'mois', 'trimestre', 'annee', 'semaine',
               'libelle_jour', 'libelle_mois', 'est_weekend',
               'est_ferie_maroc', 'periode_ramadan']]

def calculer_segments_clients(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le segment client (Gold/Silver/Bronze) basé sur le CA cumulé
    des 12 derniers mois pour chaque client.
    """
    from datetime import date, timedelta
    
    date_limite = pd.Timestamp(date.today() - timedelta(days=365))
    
    df_recents = df_commandes[
        (df_commandes['date_commande'] >= date_limite) &
        (df_commandes['statut'] == 'livre')
    ].copy()
    
    df_recents['montant_ttc'] = df_recents['quantite'].astype(float) * df_recents['prix_unitaire'].astype(float)
    
    ca_par_client = df_recents.groupby('id_client')['montant_ttc'].sum().reset_index()
    ca_par_client.columns = ['id_client', 'ca_12m']
    
    def segmenter(ca):
        if ca >= 15000: return 'Gold'
        elif ca >= 5000: return 'Silver'
        else: return 'Bronze'
        
    ca_par_client['segment_client'] = ca_par_client['ca_12m'].apply(segmenter)
    return ca_par_client[['id_client', 'segment_client', 'ca_12m']]

def build_dim_client(df_clients: pd.DataFrame, df_commandes: pd.DataFrame) -> pd.DataFrame:
    segments = calculer_segments_clients(df_commandes)
    dim_client = df_clients.merge(segments[['id_client', 'segment_client']], on='id_client', how='left')
    dim_client['segment_client'] = dim_client['segment_client'].fillna('Bronze')
    
    # Selectionner les colonnes pour correspondre au schema DWH
    # id_client_nk, nom_complet, tranche_age, sexe, ville, segment_client, canal_acquisition
    dim_client['nom_complet'] = dim_client['nom'].fillna('') + ' ' + dim_client['prenom'].fillna('')
    dim_client['id_client_nk'] = dim_client['id_client']
    
    # Valeurs par defaut pour SCD Type 2
    dim_client['date_debut'] = pd.Timestamp('2000-01-01')
    dim_client['date_fin'] = pd.Timestamp('9999-12-31')
    dim_client['est_actif'] = True
    
    cols = ['id_client_nk', 'nom_complet', 'tranche_age', 'sexe', 'ville', 
            'segment_client', 'canal_acquisition', 'date_debut', 'date_fin', 'est_actif']
    
    dim_client = dim_client[cols]
    
    # Ajouter client inconnu
    inconnu = pd.DataFrame([['-1', 'Client Inconnu', 'Inconnu', 'U', 'Inconnu', 'Bronze', 'Inconnu', '2000-01-01', '9999-12-31', True]], columns=cols)
    dim_client = pd.concat([dim_client, inconnu], ignore_index=True)
    
    return dim_client

def build_dim_produit(df_produits: pd.DataFrame) -> pd.DataFrame:
    dim_produit = df_produits.copy()
    dim_produit['id_produit_nk'] = dim_produit['id_produit']
    dim_produit['nom_produit'] = dim_produit['nom']
    dim_produit['prix_standard'] = dim_produit['prix_catalogue']
    dim_produit['est_actif'] = dim_produit['actif']
    
    dim_produit['date_debut'] = pd.to_datetime(dim_produit.get('date_creation', '2000-01-01'))
    dim_produit['date_fin'] = pd.Timestamp('9999-12-31')
    
    cols = ['id_produit_nk', 'nom_produit', 'categorie', 'sous_categorie', 
            'marque', 'fournisseur', 'prix_standard', 'origine_pays',
            'date_debut', 'date_fin', 'est_actif']
    
    # Garder les colonnes existantes pour eviter des erreurs KeyError
    cols_existantes = [c for c in cols if c in dim_produit.columns]
    dim_produit = dim_produit[cols_existantes]
    
    # Ajouter produit inconnu
    inconnu = pd.DataFrame([['-1', 'Produit Inconnu', 'Inconnu', 'Inconnu', 'Inconnu', 'Inconnu', 0.0, 'Inconnu', '2000-01-01', '9999-12-31', True]], columns=cols)
    # Ne garder que les colonnes qui existent
    inconnu = inconnu[cols_existantes]
    dim_produit = pd.concat([dim_produit, inconnu], ignore_index=True)
    
    return dim_produit

def build_dim_region(df_regions: pd.DataFrame) -> pd.DataFrame:
    dim_region = df_regions.copy()
    if 'nom_ville_standard' in dim_region.columns:
        dim_region['ville'] = dim_region['nom_ville_standard']
    
    # On ne garde que les colonnes présentes dans la table dwh_mexora.dim_region
    cols_sql = ['ville', 'province', 'region_admin', 'zone_geo', 'pays']
    # Ajouter 'pays' par défaut si absent
    if 'pays' not in dim_region.columns:
        dim_region['pays'] = 'Maroc'
    
    dim_region = dim_region[[c for c in cols_sql if c in dim_region.columns]]
    
    # Ajouter une ligne par défaut pour les villes non trouvées
    inconnu = pd.DataFrame([['Non renseignée', 'Inconnu', 'Inconnu', 'Inconnu', 'Maroc']], columns=cols_sql)
    dim_region = pd.concat([dim_region, inconnu], ignore_index=True)
        
    return dim_region

def build_dim_livreur(df_commandes: pd.DataFrame) -> pd.DataFrame:
    livreurs = df_commandes['id_livreur'].unique()
    dim_livreur = pd.DataFrame({'id_livreur_nk': livreurs})
    dim_livreur['nom_livreur'] = 'Livreur ' + dim_livreur['id_livreur_nk'].astype(str)
    dim_livreur.loc[dim_livreur['id_livreur_nk'] == '-1', 'nom_livreur'] = 'Inconnu'
    return dim_livreur

def build_fait_ventes(df_commandes: pd.DataFrame, 
                      map_client: dict, map_produit: dict, 
                      map_region: dict, map_livreur: dict) -> pd.DataFrame:
    """
    Construit la table de faits en remplaçant les NK par les SK.
    """
    faits = df_commandes.copy()
    
    # Conversion date_commande en id_date
    faits['id_date'] = faits['date_commande'].dt.strftime('%Y%m%d').astype(int)
    
    # Mapping des Surrogate Keys
    faits['id_client']  = faits['id_client'].map(map_client).fillna(map_client.get('-1'))
    faits['id_produit'] = faits['id_produit'].map(map_produit).fillna(map_produit.get('-1'))
    faits['id_region']  = faits['ville_livraison'].map(map_region).fillna(map_region.get('Non renseignée'))
    faits['id_livreur'] = faits['id_livreur'].map(map_livreur).fillna(map_livreur.get('-1'))
    
    # Sécurité supplémentaire : s'il reste des NaNs (ex: si l'entrée Inconnu n'existe pas)
    faits['id_client']  = faits['id_client'].fillna(0).astype(int)
    faits['id_produit'] = faits['id_produit'].fillna(0).astype(int)
    faits['id_region']  = faits['id_region'].fillna(0).astype(int)
    faits['id_livreur'] = faits['id_livreur'].fillna(0).astype(int)

    # Calcul des mesures
    faits['quantite_vendue'] = faits['quantite'].astype(int)
    faits['montant_ttc'] = faits['quantite_vendue'] * faits['prix_unitaire'].astype(float)
    faits['montant_ht'] = faits['montant_ttc'] / 1.2
    faits['statut_commande'] = faits['statut']
    
    # Optionnel: calcul du délai de livraison
    if 'date_livraison' in faits.columns:
        faits['date_livraison'] = pd.to_datetime(faits['date_livraison'], errors='coerce')
        faits['delai_livraison_jours'] = (faits['date_livraison'] - faits['date_commande']).dt.days
    
    cols = ['id_date', 'id_produit', 'id_client', 'id_region', 'id_livreur', 
            'quantite_vendue', 'montant_ht', 'montant_ttc', 'statut_commande', 'delai_livraison_jours']
            
    return faits[[c for c in cols if c in faits.columns]]
