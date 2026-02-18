import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="Tableau de Bord PDR Marrakech-Safi", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Make sure the filename matches exactly what you generated
    df = pd.read_csv("PDR_Marrakech_Safi_Projects.csv", sep=";")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ File not found! Please run the data generation script first.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filtres Régionaux")
selected_province = st.sidebar.multiselect(
    "Choisir la Province",
    options=df["Province"].unique(),
    default=df["Province"].unique() # Select all by default
)

selected_sector = st.sidebar.multiselect(
    "Choisir le Secteur",
    options=df["Secteur"].unique(),
    default=df["Secteur"].unique()
)

# Filter the data based on selection
df_filtered = df[
    (df["Province"].isin(selected_province)) & 
    (df["Secteur"].isin(selected_sector))
]

# --- MAIN DASHBOARD ---
st.title("📊 Suivi du PDR - Région Marrakech-Safi")
st.markdown("---")

# --- TOP KPIS (Key Performance Indicators) ---
# These represent the "Big Numbers" the Governor cares about
total_budget = df_filtered["Budget_DH"].sum()
total_projects = len(df_filtered)
avg_progress = df_filtered["Taux_Avancement"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Budget Total Investi", f"{total_budget:,.0f} DH")
col2.metric("Nombre de Projets", total_projects)
col3.metric("Taux d'Avancement Moyen", f"{avg_progress:.1f}%")

st.markdown("---")

# --- CHARTS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💰 Disparités Budgétaires par Province")
    # A Bar Chart showing which province gets the most money
    fig_budget = px.bar(
        df_filtered.groupby("Province")["Budget_DH"].sum().reset_index(),
        x="Budget_DH",
        y="Province",
        orientation="h",
        text_auto=".2s",
        color="Budget_DH",
        color_continuous_scale="Viridis",
        title="Budget Alloué par Province (DH)"
    )
    st.plotly_chart(fig_budget, use_container_width=True)

with col_right:
    st.subheader("🏗️ État d'Avancement des Projets")
    # A Pie Chart showing project status (Blocked, Done, In Progress)
    fig_status = px.pie(
        df_filtered,
        names="Statut",
        title="Répartition des Projets par Statut",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_status, use_container_width=True)

# --- DETAILED DATA TABLE ---
st.subheader("📋 Liste Détaillée des Projets")
st.dataframe(df_filtered)