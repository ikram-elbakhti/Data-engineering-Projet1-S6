# =====================================================================
# MEXORA PREMIUM BUSINESS INTELLIGENCE DASHBOARD
# Designed with state-of-the-art Web UX, glassmorphism, and Outfit fonts.
# =====================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
from sqlalchemy import create_engine
from mexora_etl.config.settings import DB_CONFIG

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Mexora Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM GLOWING DARK STYLE SYSTEM ---
st.markdown("""
    <style>
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #0B0F19 !important;
        color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0E1626 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebar"] * {
        color: #94A3B8 !important;
    }
    
    /* Custom Titles & Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em;
    }
    
    /* Micro-Animations & Custom KPI Cards */
    .kpi-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Styled Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0B0F19;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
    
    /* Modern Streamlit Metric Overrides */
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }
    
    /* Styled Selectboxes & Radio Inputs */
    div[data-baseweb="select"] {
        background-color: #111827 !important;
        border-radius: 8px !important;
    }
    
    /* Glassmorphic Container & Native Streamlit Container Styling */
    .glass-container, div[data-testid="stVerticalBlockBorder"] {
        background: rgba(17, 24, 39, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(12px) !important;
    /* Fix top white space and padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Custom Premium Table to avoid horizontal scroll */
    .premium-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.85em;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #F8FAFC;
        border-radius: 8px 8px 0 0;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    .premium-table thead tr {
        background-color: rgba(99, 102, 241, 0.2);
        color: #F8FAFC;
        text-align: left;
        font-weight: 600;
    }
    .premium-table th,
    .premium-table td {
        padding: 12px 15px;
    }
    .premium-table tbody tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .premium-table tbody tr:nth-of-type(even) {
        background-color: rgba(255, 255, 255, 0.02);
    }
    .premium-table tbody tr:last-of-type {
        border-bottom: 2px solid #6366F1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION & CACHING ---
@st.cache_resource
def get_connection():
    try:
        password = urllib.parse.quote_plus(DB_CONFIG['password'])
        url = f"postgresql://{DB_CONFIG['user']}:{password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        return create_engine(url)
    except Exception as e:
        st.error(f"❌ Erreur de connexion à la base de données : {e}")
        return None

engine = get_connection()

# Helper for KPI HTML rendering
def render_kpi(title, value, delta=None, delta_direction="up", icon="📈", glow_color="99, 102, 241"):
    delta_html = ""
    if delta is not None:
        color = "#10B981" if delta_direction == "up" else "#EF4444"
        arrow = "▲" if delta_direction == "up" else "▼"
        delta_html = f'<div style="color: {color}; font-size: 0.85rem; font-weight: 600; margin-top: 4px;">{arrow} {delta}</div>'
    
    html = (
        f'<div class="kpi-card" style="background: rgba(17, 24, 39, 0.75); border: 1px solid rgba(255, 255, 255, 0.06); '
        f'border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25); backdrop-filter: blur(16px); '
        f'display: flex; align-items: center; gap: 20px; margin-bottom: 16px;">'
        f'<div style="background: rgba({glow_color}, 0.12); color: rgb({glow_color}); width: 52px; height: 52px; '
        f'border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; '
        f'box-shadow: 0 0 20px 0 rgba({glow_color}, 0.2);">{icon}</div>'
        f'<div>'
        f'<div style="color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">{title}</div>'
        f'<div style="color: #F8FAFC; font-size: 1.75rem; font-weight: 700; margin-top: 4px; font-family: \'Outfit\', sans-serif;">{value}</div>'
        f'{delta_html}'
        f'</div></div>'
    )
    return html

def render_html_table(df):
    html = '<table class="premium-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# Helper to style Plotly charts consistently
def style_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Plus Jakarta Sans',
        font_color='#94A3B8',
        title_font_family='Outfit',
        title_font_color='#F8FAFC',
        title_font_size=18,
        title_font_weight=600,
        legend_title_font_color='#F8FAFC',
        legend_font_color='#94A3B8',
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Plus Jakarta Sans"
        ),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.04)',
            linecolor='rgba(255, 255, 255, 0.08)',
            tickcolor='rgba(255, 255, 255, 0.08)',
            title_font_color='#94A3B8',
            tickfont=dict(color='#94A3B8')
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.04)',
            linecolor='rgba(255, 255, 255, 0.08)',
            tickcolor='rgba(255, 255, 255, 0.08)',
            title_font_color='#94A3B8',
            tickfont=dict(color='#94A3B8')
        )
    )
    return fig

# --- SIDEBAR BRANDING & MENU ---
with st.sidebar:
    st.markdown(
        '<div style="text-align: center; padding: 20px 0 10px 0;">'
        '<span style="font-size: 2.2rem; font-weight: 800; font-family: \'Outfit\', sans-serif; '
        'background: linear-gradient(135deg, #6366F1 0%, #10B981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">'
        'MEXORA</span>'
        '<div style="color: #64748B; font-size: 0.85rem; font-weight: 500; margin-top: 4px; letter-spacing: 0.1em; text-transform: uppercase;">'
        'Business Intelligence</div>'
        '</div>'
        '<hr style="border-top: 1px solid rgba(255, 255, 255, 0.05); margin: 15px 0 25px 0;">',
        unsafe_allow_html=True
    )
    
    # Custom Sidebar Radio menu
    menu = st.radio(
        "Navigation",
        ["📈 Évolution & Géographie", "🏆 Focus Performance Ville", "👥 Segments Clients", "⚠️ Analyse des Retours", "🌙 Effet Ramadan", "🚚 Performance Livreurs"],
        index=0
    )
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    st.sidebar.caption("Mexora DWH • v2.0 Premium")

# Main Application Entry check
if engine is None:
    st.warning("⚠️ Connexion DB non initialisée. Veuillez configurer vos paramètres dans settings.py.")
    st.stop()

# --- PAGE 1: ÉVOLUTION DU CA & GÉOGRAPHIE ---
if menu == "📈 Évolution & Géographie":
    st.markdown("<h1 style='margin-bottom: 25px;'>📈 Analyse de la Croissance et Géographie</h1>", unsafe_allow_html=True)
    
    # Fetch KPI Data
    query_kpi = """
    WITH ca_mensuel AS (
        SELECT annee, mois, SUM(ca_ttc) AS ca_total
        FROM reporting_mexora.mv_ca_mensuel
        GROUP BY annee, mois
    )
    SELECT annee, mois, ca_total,
           LAG(ca_total) OVER (ORDER BY annee, mois) AS ca_prec,
           ROUND(((ca_total - LAG(ca_total) OVER (ORDER BY annee, mois)) / NULLIF(LAG(ca_total) OVER (ORDER BY annee, mois), 0)) * 100, 2) AS evol
    FROM ca_mensuel ORDER BY annee DESC, mois DESC LIMIT 1
    """
    try:
        kpi_data = pd.read_sql(query_kpi, engine)
    except Exception as e:
        st.error(f"Erreur SQL KPI : {e}")
        kpi_data = pd.DataFrame()
        
    # Fetch Top Region
    try:
        top_reg = pd.read_sql("""
            SELECT region_admin, SUM(ca_ttc) as ca 
            FROM reporting_mexora.mv_ca_mensuel 
            GROUP BY 1 ORDER BY 2 DESC LIMIT 1
        """, engine)
    except Exception as e:
        st.error(f"Erreur SQL Top Région : {e}")
        top_reg = pd.DataFrame()

    # Display KPI Cards
    col1, col2, col3 = st.columns(3)
    
    if not kpi_data.empty:
        ca_total = kpi_data['ca_total'].iloc[0]
        evol = kpi_data['evol'].iloc[0]
        evol_dir = "up" if evol >= 0 else "down"
        col1.markdown(render_kpi("CA Mois Actuel", f"{ca_total:,.0f} DH", f"{evol}% vs M-1", evol_dir, "💰", "99, 102, 241"), unsafe_allow_html=True)
        col2.markdown(render_kpi("Évolution vs M-1", f"{evol:+,.2f}%", None, None, "📈", "16, 185, 129" if evol >= 0 else "239, 68, 68"), unsafe_allow_html=True)
    else:
        col1.markdown(render_kpi("CA Mois Actuel", "N/A", None, None, "💰"), unsafe_allow_html=True)
        col2.markdown(render_kpi("Évolution vs M-1", "N/A", None, None, "📈"), unsafe_allow_html=True)
        
    if not top_reg.empty:
        reg_name = top_reg['region_admin'].iloc[0]
        reg_ca = top_reg['ca'].iloc[0]
        col3.markdown(render_kpi("Top Région", reg_name, f"{reg_ca:,.0f} DH", "up", "👑", "245, 158, 11"), unsafe_allow_html=True)
    else:
        col3.markdown(render_kpi("Top Région", "N/A", None, None, "👑"), unsafe_allow_html=True)

    # 12-Month Line Chart
    with st.container(border=True):
        st.markdown("### 📊 Évolution mensuelle du CA (Comparaison Annuelle)")
        
        try:
            df_evol = pd.read_sql("""
                SELECT annee, mois, libelle_mois, SUM(ca_ttc) as ca
                FROM reporting_mexora.mv_ca_mensuel
                GROUP BY 1, 2, 3 ORDER BY 1, 2
            """, engine)
        except Exception as e:
            st.error(f"Erreur SQL Évolution : {e}")
            df_evol = pd.DataFrame()
            
        if not df_evol.empty:
            # Line Chart with Premium Colors
            fig_evol = px.line(
                df_evol, 
                x='libelle_mois', 
                y='ca', 
                color='annee', 
                markers=True, 
                line_shape='spline',
                color_discrete_sequence=['#6366F1', '#10B981', '#FF5A36'],
                labels={'libelle_mois': 'Mois', 'ca': 'Chiffre d\'Affaires (DH)', 'annee': 'Année'}
            )
            fig_evol.update_traces(line=dict(width=3), marker=dict(size=8, symbol='circle'))
            style_chart(fig_evol)
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Aucune donnée d'évolution disponible.")

    # Regional Treemap
    with st.container(border=True):
        st.markdown("### 🗺️ Répartition Géographique du Chiffre d'Affaires")
        
        try:
            df_geo = pd.read_sql("""
                SELECT region_admin, zone_geo, SUM(ca_ttc) as ca, SUM(volume_vendu) as volume
                FROM reporting_mexora.mv_ca_mensuel
                GROUP BY 1, 2 ORDER BY ca DESC
            """, engine)
        except Exception as e:
            st.error(f"Erreur SQL Géo : {e}")
            df_geo = pd.DataFrame()
            
        if not df_geo.empty:
            col_g1, col_g2 = st.columns([3, 2])
            
            with col_g1:
                fig_geo = px.treemap(
                    df_geo, 
                    path=['zone_geo', 'region_admin'], 
                    values='ca',
                    color='ca',
                    color_continuous_scale='Purples',
                    labels={'ca': 'CA Total (DH)', 'labels': 'Zone / Région'}
                )
                fig_geo.update_layout(margin=dict(t=30, l=10, r=10, b=10))
                st.plotly_chart(fig_geo, use_container_width=True)
                
            with col_g2:
                df_fmt = df_geo.rename(columns={'region_admin': 'Région', 'zone_geo': 'Zone', 'ca': 'CA (DH)', 'volume': 'Volume'})
                df_fmt['CA (DH)'] = df_fmt['CA (DH)'].apply(lambda x: f"{x:,.0f} DH".replace(',', ' '))
                df_fmt['Volume'] = df_fmt['Volume'].apply(lambda x: f"{x} u")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)
        else:
            st.info("Aucune donnée géographique disponible.")

# --- PAGE 2: FOCUS PERFORMANCE VILLE ---
elif menu == "🏆 Focus Performance Ville":
    st.markdown("<h1 style='margin-bottom: 25px;'>🏆 Performance Produits - Focus Ville</h1>", unsafe_allow_html=True)
    
    # Fetch available cities from dim_region
    try:
        villes_dispo = pd.read_sql("SELECT DISTINCT ville FROM dwh_mexora.dim_region ORDER BY ville", engine)['ville'].tolist()
    except Exception as e:
        villes_dispo = ["Tanger", "Casablanca", "Rabat", "Marrakech", "Fès", "Agadir"]
    
    default_index = villes_dispo.index("Tanger") if "Tanger" in villes_dispo else 0

    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            ville_sel = st.selectbox("Sélectionner la Ville", villes_dispo, index=default_index)
        with col_f2:
            annee_sel = st.selectbox("Sélectionner l'Année", [2023, 2024, 2025], index=1)
        with col_f3:
            trim_sel = st.selectbox("Sélectionner le Trimestre", [1, 2, 3, 4], index=0)
 
    query_top10 = f"""
        SELECT p.nom_produit, p.categorie, SUM(f.montant_ttc) as ca, SUM(f.quantite_vendue) as volume
        FROM dwh_mexora.fait_ventes f
        JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
        JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
        JOIN dwh_mexora.dim_region r ON f.id_region = r.id_region
        WHERE r.ville = '{ville_sel}' AND t.annee = {annee_sel} AND t.trimestre = {trim_sel} AND f.statut_commande = 'livre'
        GROUP BY p.nom_produit, p.categorie
        ORDER BY ca DESC LIMIT 10
    """
    try:
        df_top10 = pd.read_sql(query_top10, engine)
    except Exception as e:
        st.error(f"Erreur SQL Top {ville_sel} : {e}")
        df_top10 = pd.DataFrame()
        
    with st.container(border=True):
        if not df_top10.empty:
            col_t1, col_t2 = st.columns([3, 2])
            
            with col_t1:
                fig_top = px.bar(
                    df_top10, 
                    x='ca', 
                    y='nom_produit', 
                    orientation='h',
                    color='ca', 
                    color_continuous_scale='Tealgrn',
                    labels={'ca': 'CA Total (DH)', 'nom_produit': 'Produit'},
                    title=f"Top 10 Produits les plus vendus à {ville_sel} (T{trim_sel} {annee_sel})"
                )
                fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
                style_chart(fig_top)
                st.plotly_chart(fig_top, use_container_width=True)
                
            with col_t2:
                st.markdown("<h4 style='margin-bottom: 20px;'>Détails Analytiques</h4>", unsafe_allow_html=True)
                df_fmt = df_top10.rename(columns={'nom_produit': 'Produit', 'categorie': 'Catégorie', 'ca': 'CA (DH)', 'volume': 'Volume'})
                df_fmt['CA (DH)'] = df_fmt['CA (DH)'].apply(lambda x: f"{x:,.0f} DH".replace(',', ' '))
                df_fmt['Volume'] = df_fmt['Volume'].apply(lambda x: f"{x} u")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)
        else:
            st.info(f"Aucune commande livrée enregistrée à {ville_sel} pour le trimestre {trim_sel} de l'année {annee_sel}.")

# --- PAGE 3: SEGMENT CLIENT ---
elif menu == "👥 Segments Clients":
    st.markdown("<h1 style='margin-bottom: 25px;'>👥 Analyse des Segments Clients</h1>", unsafe_allow_html=True)
    
    query_seg = """
        SELECT c.segment_client, 
               COUNT(DISTINCT f.id_vente) as nb_cmd,
               SUM(f.montant_ttc) as ca_total,
               ROUND(SUM(f.montant_ttc) / COUNT(DISTINCT f.id_vente), 2) as panier_moyen
        FROM dwh_mexora.fait_ventes f
        JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client_sk
        WHERE f.statut_commande = 'livre'
        GROUP BY 1 ORDER BY panier_moyen DESC
    """
    try:
        df_seg = pd.read_sql(query_seg, engine)
    except Exception as e:
        st.error(f"Erreur SQL Segments : {e}")
        df_seg = pd.DataFrame()
        
    with st.container(border=True):
        if not df_seg.empty:
            c1, c2 = st.columns([4, 5])
            
            with c1:
                st.markdown("#### 🎯 Répartition du CA par Segment")
                # Color map for Gold, Silver, Bronze
                color_map = {
                    "Gold": "#F59E0B",    # Glowing Amber Gold
                    "Silver": "#94A3B8",  # Slate Silver
                    "Bronze": "#B45309"   # Bronze Copper
                }
                fig_donut = px.pie(
                    df_seg, 
                    values='ca_total', 
                    names='segment_client', 
                    hole=.6,
                    color='segment_client',
                    color_discrete_map=color_map
                )
                # Customizing donut style
                fig_donut.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    marker=dict(line=dict(color='#0B0F19', width=3))
                )
                style_chart(fig_donut)
                fig_donut.update_layout(showlegend=False)
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with c2:
                st.markdown("#### 📊 Panier Moyen et Volumes de Commandes")
                df_fmt = df_seg.rename(columns={'segment_client': 'Segment', 'panier_moyen': 'Panier Moyen', 'nb_cmd': 'Nombre Commandes', 'ca_total': 'CA Total (DH)'})
                df_fmt['Panier Moyen'] = df_fmt['Panier Moyen'].apply(lambda x: f"{x:,.2f} DH".replace(',', ' '))
                df_fmt['CA Total (DH)'] = df_fmt['CA Total (DH)'].apply(lambda x: f"{x:,.0f} DH".replace(',', ' '))
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)
                
                # Key analytical insights
                st.markdown("""
                    <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px; margin-top: 20px;">
                        <span style="font-weight: 600; color: #F8FAFC;">💡 Constats analytiques :</span>
                        <ul style="color: #94A3B8; font-size: 0.9rem; margin-top: 8px; padding-left: 20px;">
                            <li>Le segment <b style="color: #F59E0B;">Gold</b> présente le panier moyen le plus élevé de la clientèle.</li>
                            <li>Les clients <b style="color: #94A3B8;">Silver</b> et <b style="color: #B45309;">Bronze</b> génèrent la majorité du volume total de transactions de la plateforme.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Aucune donnée client disponible.")

    # Multi-client Bubble plot
    with st.container(border=True):
        st.markdown("### 🔵 Comportement Individuel des Clients par Segment (Échantillon)")
        query_scatter = """
            SELECT c.segment_client,
                   c.nom_complet,
                   COUNT(DISTINCT f.id_vente) as nb_commandes,
                   SUM(f.montant_ttc) as ca_total
            FROM dwh_mexora.fait_ventes f
            JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client_sk
            WHERE f.statut_commande = 'livre' AND c.nom_complet NOT LIKE '%%Inconnu%%'
            GROUP BY c.segment_client, c.nom_complet
            ORDER BY ca_total DESC LIMIT 150
        """
        try:
            df_scatter = pd.read_sql(query_scatter, engine)
        except Exception as e:
            st.error(f"Erreur SQL Échantillon : {e}")
            df_scatter = pd.DataFrame()
            
        if not df_scatter.empty:
            fig_scatter = px.scatter(
                df_scatter,
                x='nb_commandes',
                y='ca_total',
                color='segment_client',
                size='ca_total',
                hover_name='nom_complet',
                color_discrete_map={"Gold": "#F59E0B", "Silver": "#94A3B8", "Bronze": "#B45309"},
                labels={'nb_commandes': 'Nombre de Commandes', 'ca_total': 'CA Total (DH)', 'segment_client': 'Segment'},
                title="Comparatif : Commandes vs Contribution CA par Client"
            )
            style_chart(fig_scatter)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Aucune donnée comportementale disponible.")

# --- PAGE 4: TAUX DE RETOUR ---
elif menu == "⚠️ Analyse des Retours":
    st.markdown("<h1 style='margin-bottom: 25px;'>⚠️ Qualité et Analyse des Retours</h1>", unsafe_allow_html=True)
    
    # Dynamic Seuil Slider
    with st.container(border=True):
        st.markdown("#### ⚙️ Configuration du Seuil de Vigilance")
        seuil_alerte = st.slider("Seuil critique d'alerte de retour (%)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
    
    query_ret = """
        SELECT p.categorie,
               COUNT(*) FILTER (WHERE f.statut_commande = 'retourne') * 100.0 / COUNT(*) as taux_retour,
               COUNT(*) FILTER (WHERE f.statut_commande = 'retourne') as nb_retours,
               COUNT(*) as total_commandes
        FROM dwh_mexora.fait_ventes f
        JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
        GROUP BY 1 ORDER BY taux_retour DESC
    """
    try:
        df_ret = pd.read_sql(query_ret, engine)
    except Exception as e:
        st.error(f"Erreur SQL Taux Retour : {e}")
        df_ret = pd.DataFrame()
        
    with st.container(border=True):
        if not df_ret.empty:
            col_r1, col_r2 = st.columns([3, 2])
            
            with col_r1:
                # Color logic based on quality thresholds (Green < 60% of seuil, Orange 60-100% of seuil, Red > seuil)
                def get_color(val):
                    if val > seuil_alerte: return '#EF4444' # Crimson
                    if val >= seuil_alerte * 0.6: return '#F59E0B' # Orange
                    return '#10B981' # Mint Green

                df_ret['couleur'] = df_ret['taux_retour'].apply(get_color)
                
                fig_ret = go.Figure(go.Bar(
                    x=df_ret['taux_retour'], 
                    y=df_ret['categorie'],
                    orientation='h', 
                    marker_color=df_ret['couleur'],
                    text=df_ret['taux_retour'].round(2).astype(str) + "%",
                    textposition='auto',
                    hovertemplate="Catégorie : %{y}<br>Taux de retour : %{x:.2f}%<extra></extra>"
                ))
                fig_ret.update_layout(
                    title=f"Taux de retour par catégorie (Seuil alerte critique à {seuil_alerte}%)",
                    xaxis_title="Taux de retour (%)", 
                    yaxis={'categoryorder':'total ascending'}
                )
                
                # Ajout de la ligne d'alerte rouge dynamique
                fig_ret.add_vline(x=seuil_alerte, line_dash="dash", line_color="#EF4444", annotation_text=f"Alerte {seuil_alerte}%", annotation_font_color="#EF4444")
                style_chart(fig_ret)
                st.plotly_chart(fig_ret, use_container_width=True)
                
            with col_r2:
                st.markdown("<h4 style='margin-bottom: 20px;'>Indicateurs Qualité</h4>", unsafe_allow_html=True)
                df_fmt = df_ret.drop(columns=['couleur']).rename(columns={'categorie': 'Catégorie', 'taux_retour': 'Taux Retour (%)', 'nb_retours': 'Retours', 'total_commandes': 'Commandes Totales'})
                df_fmt['Taux Retour (%)'] = df_fmt['Taux Retour (%)'].apply(lambda x: f"{x:.2f}%")
                st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)
                
                # Highlight card for high return rates
                alertes_depassees = df_ret[df_ret['taux_retour'] > seuil_alerte]
                if not alertes_depassees.empty:
                    for idx, row in alertes_depassees.iterrows():
                        st.markdown(f"""
                            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 15px; margin-top: 15px;">
                                <span style="font-weight: 600; color: #EF4444;">🚨 ALERTE CRITIQUE :</span><br>
                                <span style="color: #E2E8F0; font-size: 0.9rem;">
                                    La catégorie <b>{row['categorie']}</b> dépasse le seuil critique avec un taux de retour de <b>{row['taux_retour']:.2f}%</b> ({row['nb_retours']} retours). Des actions correctives sont requises d'urgence auprès de nos fournisseurs.
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 15px; margin-top: 15px;">
                            <span style="font-weight: 600; color: #10B981;">✅ EXCELLENTE QUALITÉ :</span><br>
                            <span style="color: #E2E8F0; font-size: 0.9rem;">
                                Aucune catégorie ne dépasse le seuil d'alerte critique de <b>{seuil_alerte}%</b>. Les indicateurs sont au vert.
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Aucune commande enregistrée pour l'analyse des retours.")

    # Sub-category details table inside container
    with st.container(border=True):
        st.markdown("### 🔍 Analyse fine des Retours par Sous-Catégories")
        query_ret_sub = """
            SELECT p.sous_categorie, p.categorie,
                   COUNT(*) FILTER (WHERE f.statut_commande = 'retourne') as nb_retours,
                   COUNT(*) as total,
                   COUNT(*) FILTER (WHERE f.statut_commande = 'retourne') * 100.0 / COUNT(*) as taux_retour
            FROM dwh_mexora.fait_ventes f
            JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
            GROUP BY 1, 2 ORDER BY taux_retour DESC LIMIT 15
        """
        try:
            df_ret_sub = pd.read_sql(query_ret_sub, engine)
        except Exception as e:
            st.error(f"Erreur SQL Sous-Catégories : {e}")
            df_ret_sub = pd.DataFrame()
            
        if not df_ret_sub.empty:
            df_fmt = df_ret_sub.rename(columns={'sous_categorie': 'Sous-Catégorie', 'categorie': 'Catégorie', 'nb_retours': 'Retours', 'total': 'Volume Total', 'taux_retour': 'Taux Retour'})
            df_fmt['Taux Retour'] = df_fmt['Taux Retour'].apply(lambda x: f"{x:.2f}%")
            st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)
        else:
            st.info("Aucune donnée fine par sous-catégorie disponible.")

# --- PAGE 5: EFFET RAMADAN ---
elif menu == "🌙 Effet Ramadan":
    st.markdown("<h1 style='margin-bottom: 25px;'>🌙 Analyse de l'Effet Ramadan</h1>", unsafe_allow_html=True)
    
    query_ram = """
        SELECT t.periode_ramadan,
               AVG(f.montant_ttc) as ca_moyen_jour,
               SUM(f.quantite_vendue) as volume_total
        FROM dwh_mexora.fait_ventes f
        JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
        JOIN dwh_mexora.dim_produit p ON f.id_produit = p.id_produit_sk
        WHERE p.categorie = 'Alimentation' AND f.statut_commande = 'livre'
        GROUP BY 1
    """
    try:
        df_ram = pd.read_sql(query_ram, engine)
    except Exception as e:
        st.error(f"Erreur SQL Ramadan : {e}")
        df_ram = pd.DataFrame()
        
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    if not df_ram.empty and len(df_ram) >= 2:
        # Calculate Index
        try:
            ca_hors = df_ram[df_ram['periode_ramadan']==False]['ca_moyen_jour'].iloc[0]
            ca_ram = df_ram[df_ram['periode_ramadan']==True]['ca_moyen_jour'].iloc[0]
            indice = round((ca_ram / ca_hors - 1) * 100, 2)
        except IndexError:
            indice = 0.0
        
        st.markdown(f"""
            <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px;">
                <span style="font-size: 1.1rem; color: #94A3B8; font-weight: 500;">Indice de performance Ramadan (Secteur Alimentation)</span>
                <div style="font-size: 3rem; font-weight: 800; color: #FF5A36; font-family: 'Outfit', sans-serif; margin-top: 5px;">
                     {indice:+.2f}%
                </div>
                <span style="font-size: 0.9rem; color: #64748B;">Surcroît moyen des ventes journalières durant le mois sacré</span>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ram_vol = px.bar(
                df_ram, 
                x='periode_ramadan', 
                y='volume_total', 
                title="Volume Vendu de Produits Alimentaires",
                color='periode_ramadan', 
                color_discrete_map={True: '#FF5A36', False: '#1E293B'},
                labels={'periode_ramadan': 'Période Ramadan', 'volume_total': 'Volume Total Vendu (u)'}
            )
            # Standardize X-axis labels
            fig_ram_vol.update_layout(xaxis=dict(tickmode='array', tickvals=[True, False], ticktext=['Ramadan 🌙', 'Hors Ramadan ☀️']))
            style_chart(fig_ram_vol)
            fig_ram_vol.update_layout(showlegend=False)
            st.plotly_chart(fig_ram_vol, use_container_width=True)
            
        with col2:
            fig_ram_ca = px.bar(
                df_ram, 
                x='periode_ramadan', 
                y='ca_moyen_jour', 
                title="Panier Moyen Alimentaire Journalier",
                color='periode_ramadan', 
                color_discrete_map={True: '#10B981', False: '#1E293B'},
                labels={'periode_ramadan': 'Période Ramadan', 'ca_moyen_jour': 'CA Moyen Journalier (DH)'}
            )
            fig_ram_ca.update_layout(xaxis=dict(tickmode='array', tickvals=[True, False], ticktext=['Ramadan 🌙', 'Hors Ramadan ☀️']))
            style_chart(fig_ram_ca)
            fig_ram_ca.update_layout(showlegend=False)
            st.plotly_chart(fig_ram_ca, use_container_width=True)
    else:
        st.info("Aucune donnée temporelle relative à la période du Ramadan n'a pu être segmentée pour le secteur Alimentation.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE 6: PERFORMANCE DES LIVREURS ---
elif menu == "🚚 Performance Livreurs":
    st.markdown("<h1 style='margin-bottom: 25px;'>🚚 Analyse de la Performance des Livreurs</h1>", unsafe_allow_html=True)
    
    # Filter selection inside a Glass Container
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        annee_sel = st.selectbox("Sélectionner l'Année (Logistique)", [2023, 2024, 2025], index=1)
    with col_f2:
        mois_dispo = [("Janvier", 1), ("Février", 2), ("Mars", 3), ("Avril", 4), ("Mai", 5), ("Juin", 6),
                      ("Juillet", 7), ("Août", 8), ("Septembre", 9), ("Octobre", 10), ("Novembre", 11), ("Décembre", 12)]
        # Default index to Mai (index 4) for testing
        mois_sel_name = st.selectbox("Sélectionner le Mois (Logistique)", [m[0] for m in mois_dispo], index=4)
        mois_sel_num = next(m[1] for m in mois_dispo if m[0] == mois_sel_name)
    st.markdown("</div>", unsafe_allow_html=True)

    query_liv = f"""
        SELECT nom_livreur, nb_livraisons, delai_moyen_jours, nb_livraisons_retard, taux_retard_pct
        FROM reporting_mexora.mv_performance_livreurs
        WHERE annee = {annee_sel} AND mois = {mois_sel_num}
        ORDER BY nb_livraisons DESC
    """
    try:
        df_liv = pd.read_sql(query_liv, engine)
    except Exception as e:
        st.error(f"Erreur SQL Livreurs : {e}")
        df_liv = pd.DataFrame()
        
    if not df_liv.empty:
        total_liv = df_liv['nb_livraisons'].sum()
        avg_delay = (df_liv['delai_moyen_jours'] * df_liv['nb_livraisons']).sum() / total_liv if total_liv > 0 else 0
        total_retards = df_liv['nb_livraisons_retard'].sum()
        late_rate = (total_retards / total_liv) * 100 if total_liv > 0 else 0
        
        # Display KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(render_kpi("Livraisons Totales", f"{total_liv:,.0f} u", None, None, "📦", "99, 102, 241"), unsafe_allow_html=True)
        col2.markdown(render_kpi("Délai Moyen", f"{avg_delay:.2f} j", None, None, "⏱️", "16, 185, 129" if avg_delay <= 2.5 else "245, 158, 11"), unsafe_allow_html=True)
        col3.markdown(render_kpi("Total Retards (>3j)", f"{total_retards:,.0f} u", None, None, "🚨", "239, 68, 68"), unsafe_allow_html=True)
        col4.markdown(render_kpi("Taux Retard Global", f"{late_rate:.2f}%", None, None, "📉", "16, 185, 129" if late_rate < 15 else "239, 68, 68"), unsafe_allow_html=True)
        
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([3, 2])
        
        with col_c1:
            # Bar chart of late rates by delivery person
            df_liv_sorted = df_liv.sort_values(by='taux_retard_pct', ascending=True)
            fig_liv = px.bar(
                df_liv_sorted,
                x='taux_retard_pct',
                y='nom_livreur',
                orientation='h',
                color='taux_retard_pct',
                color_continuous_scale='Reds',
                labels={'taux_retard_pct': 'Taux de Retard (%)', 'nom_livreur': 'Livreur'},
                title=f"Taux de retard par Livreur (Seuil de tolérance cible à 15%)"
            )
            # Add a vertical target line at 15%
            fig_liv.add_vline(x=15, line_dash="dash", line_color="#10B981", annotation_text="Cible 15%", annotation_font_color="#10B981")
            style_chart(fig_liv)
            st.plotly_chart(fig_liv, use_container_width=True)
            
        with col_c2:
            st.markdown("<h4 style='margin-bottom: 20px;'>Détails Logistiques</h4>", unsafe_allow_html=True)
            import pandas as pd
            df_fmt = df_liv.rename(columns={'nom_livreur': 'Livreur', 'nb_livraisons': 'Livraisons', 'delai_moyen_jours': 'Délai Moyen (j)', 'nb_livraisons_retard': 'Retards', 'taux_retard_pct': 'Retard (%)'})
            df_fmt['Retard (%)'] = df_fmt['Retard (%)'].apply(lambda x: f"{x:.2f}%")
            df_fmt['Délai Moyen (j)'] = df_fmt['Délai Moyen (j)'].apply(lambda x: f"{x:.2f} j" if pd.notnull(x) else "N/A")
            st.markdown(render_html_table(df_fmt), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Check for underperforming delivery partners
        underperforming = df_liv[(df_liv['taux_retard_pct'] > 15) & (df_liv['nb_livraisons'] > 1)]
        if not underperforming.empty:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #EF4444; margin-bottom: 15px;'>⚠️ Alerte Performance Transporteurs</h4>", unsafe_allow_html=True)
            for idx, row in underperforming.iterrows():
                st.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.05); border-left: 4px solid #EF4444; border-radius: 4px; padding: 12px; margin-bottom: 10px;">
                        Le partenaire <b>{row['nom_livreur']}</b> a un taux de retard critique de <span style="color: #EF4444; font-weight: bold;">{row['taux_retard_pct']:.1f}%</span> sur <b>{row['nb_livraisons']}</b> livraisons (délai moyen de {row['delai_moyen_jours']:.2f} jours).
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(render_kpi("Livraisons Totales", "0 u", None, None, "📦"), unsafe_allow_html=True)
        col2.markdown(render_kpi("Délai Moyen", "N/A", None, None, "⏱️"), unsafe_allow_html=True)
        col3.markdown(render_kpi("Total Retards (>3j)", "0 u", None, None, "🚨"), unsafe_allow_html=True)
        col4.markdown(render_kpi("Taux Retard Global", "N/A", None, None, "📉"), unsafe_allow_html=True)
        
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.info(f"Aucune donnée de livraison enregistrée pour le mois de {mois_sel_name} {annee_sel}.")
        st.markdown("</div>", unsafe_allow_html=True)
