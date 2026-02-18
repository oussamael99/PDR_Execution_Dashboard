import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Système d'Aide à la Décision - Marrakech-Safi", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("PDR_Marrakech_Safi_Projects.csv", sep=";")
        
        # --- NEW FEATURE: SIMULATE GPS COORDINATES ---
        # Since we don't have real GPS data, we simulate it around Marrakech coordinates
        # Center of Marrakech-Safi approx: 31.6 -8.0
        # We add random "jitter" to scatter points across the region
        np.random.seed(42) # Consistent random numbers
        df["lat"] = 31.62 + np.random.uniform(-0.5, 0.5, len(df))
        df["lon"] = -8.00 + np.random.uniform(-0.8, 0.8, len(df))
        
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Veuillez générer le fichier CSV d'abord (Step 1).")
    st.stop()

# --- SIDEBAR: FILTERS & EXPORT ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Flag_of_Morocco.svg/1200px-Flag_of_Morocco.svg.png", width=50)
st.sidebar.title("🔍 Filtres PDR")

selected_province = st.sidebar.multiselect(
    "Province", options=df["Province"].unique(), default=df["Province"].unique()
)
selected_sector = st.sidebar.multiselect(
    "Secteur", options=df["Secteur"].unique(), default=df["Secteur"].unique()
)

# Apply Filters
df_filtered = df[
    (df["Province"].isin(selected_province)) & 
    (df["Secteur"].isin(selected_sector))
]

# --- NEW FEATURE: EXPORT DATA ---
st.sidebar.markdown("---")
st.sidebar.header("📂 Exportation")
csv = df_filtered.to_csv(index=False, sep=";").encode('utf-8-sig')
st.sidebar.download_button(
    label="📥 Télécharger en Excel (CSV)",
    data=csv,
    file_name='Projets_PDR_Filtres.csv',
    mime='text/csv',
    help="Télécharger les données filtrées pour usage administratif."
)

# --- HEADER & KPIs ---
st.title("🗺️ Tableau de Bord Stratégique : Région Marrakech-Safi")
st.markdown("### Suivi de l'Exécution du Plan de Développement Régional (PDR)")

# Custom CSS to make metrics look like "Government Cards"
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #f0f2f6;
    border: 1px solid #dcdcdc;
    padding: 10px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Budget Engagé", f"{df_filtered['Budget_DH'].sum()/1e6:.1f} MDH", delta="En Millions de DH")
col2.metric("🏗️ Projets Actifs", len(df_filtered))
col3.metric("⚠️ Projets en Retard", len(df_filtered[df_filtered["Statut"] == "En Retard"]), delta_color="inverse")
col4.metric("✅ Taux d'Achèvement Moyen", f"{df_filtered['Taux_Avancement'].mean():.1f}%")

st.markdown("---")

# --- ROW 2: MAP & ALERTS (The "Territorial Intelligence" Layer) ---
col_map, col_alerts = st.columns([2, 1])

with col_map:
    st.subheader("📍 Carte Territoriale des Projets")
    # Using Plotly Mapbox for professional look
    fig_map = px.scatter_mapbox(
        df_filtered, 
        lat="lat", 
        lon="lon", 
        color="Secteur",
        size="Budget_DH", # Bigger budget = Bigger dot
        hover_name="Intitulé_Projet",
        hover_data={"Province": True, "Statut": True, "lat": False, "lon": False},
        zoom=7, 
        center={"lat": 31.62, "lon": -8.00},
        mapbox_style="carto-positron", # Clean map style
        title="Répartition Géographique des Investissements"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with col_alerts:
    st.subheader("🚨 Alertes Critiques")
    st.markdown("Projets nécessitant une **intervention immédiate** (Statut: Suspendu ou En Retard > 10MDH).")
    
    # Filter for "Critical" projects
    critical_projects = df_filtered[
        (df_filtered["Statut"].isin(["Suspendu", "En Retard"])) & 
        (df_filtered["Budget_DH"] > 5000000) # Only big projects
    ].sort_values("Budget_DH", ascending=False).head(5)
    
    for index, row in critical_projects.iterrows():
        st.error(f"**{row['Province']}**: {row['Intitulé_Projet']} ({row['Statut']})")

# --- ROW 3: ANALYTICS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Répartition Budgétaire par Province")
    fig_bar = px.bar(
        df_filtered.groupby("Province")["Budget_DH"].sum().reset_index(),
        x="Budget_DH", y="Province", orientation="h",
        color="Budget_DH", color_continuous_scale="Viridis",
        text_auto=".2s"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("📈 Avancement par Secteur")
    # Box plot is better for engineering roles: it shows distribution of progress
    fig_box = px.box(
        df_filtered, 
        x="Secteur", 
        y="Taux_Avancement", 
        color="Secteur",
        title="Dispersion de l'avancement des projets par secteur"
    )
    st.plotly_chart(fig_box, use_container_width=True)

col_left2, = st.columns(1)

with col_left2:
    st.subheader("🏗️ État d'Avancement des Projets")
    # A Pie Chart showing project status (Blocked, Done, In Progress)
    fig_status = px.pie(
        df_filtered,
        names="Statut",
        title="Répartition des Projets par Statut",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.subheader("📋 Liste Détaillée des Projets")
st.dataframe(df_filtered)

