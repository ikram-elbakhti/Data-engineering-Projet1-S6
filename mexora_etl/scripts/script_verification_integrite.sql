-- ==============================================================================
-- Script de Vérification de l'Intégrité du Data Warehouse Mexora
-- Objectif : S'assurer que les données chargées respectent les règles métiers et l'intégrité référentielle
-- ==============================================================================

-- 1. Vérification des orphelins : Faits sans dimension Client correspondante
SELECT 'Faits sans Client' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes f
LEFT JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client_sk
WHERE c.id_client_sk IS NULL;

-- 2. Vérification des orphelins : Faits sans dimension Produit correspondante
SELECT 'Faits sans Produit' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes f
LEFT JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
WHERE p.id_produit_sk IS NULL;

-- 3. Vérification des orphelins : Faits sans dimension Temps correspondante
SELECT 'Faits sans Date' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes f
LEFT JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
WHERE t.id_date IS NULL;

-- 4. Vérification des montants négatifs (doivent avoir été nettoyés par l'ETL)
SELECT 'Montants TTC Négatifs' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes
WHERE montant_ttc < 0;

-- 5. Vérification des quantités négatives ou nulles
SELECT 'Quantités Invalides (<=0)' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes
WHERE quantite_vendue <= 0;

-- 6. Vérification de l'unicité des clients (un seul client actif par identifiant naturel)
SELECT 'Clients Actifs en Doublon' AS test_name, COUNT(*) AS nb_erreurs
FROM (
    SELECT id_client_nk, COUNT(*)
    FROM dwh_mexora.dim_client
    WHERE est_actif = TRUE
    GROUP BY id_client_nk
    HAVING COUNT(*) > 1
) subquery;

-- 7. Vérification de l'unicité des produits (un seul produit actif par identifiant naturel)
SELECT 'Produits Actifs en Doublon' AS test_name, COUNT(*) AS nb_erreurs
FROM (
    SELECT id_produit_nk, COUNT(*)
    FROM dwh_mexora.dim_produit
    WHERE est_actif = TRUE
    GROUP BY id_produit_nk
    HAVING COUNT(*) > 1
) subquery;

-- 8. Cohérence entre Montant HT et Montant TTC (TVA 20%)
-- On accepte une petite marge d'erreur due aux arrondis
SELECT 'Cohérence HT/TTC (TVA 20%)' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes
WHERE ABS(montant_ttc - (montant_ht * 1.2)) > 0.1;

-- 9. Vérification des délais de livraison illogiques (ex: livraison avant commande)
SELECT 'Délais Livraison Négatifs' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes
WHERE delai_livraison_jours < 0;

-- 10. Cohérence du statut "Livre" et Délai de livraison
-- Si la commande est livrée, elle devrait généralement avoir un délai de livraison renseigné
SELECT 'Commandes Livrées sans Délai' AS test_name, COUNT(*) AS nb_erreurs
FROM dwh_mexora.fait_ventes
WHERE statut_commande = 'livre' 
  AND delai_livraison_jours IS NULL;
