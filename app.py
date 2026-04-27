import streamlit as st
import pandas as pd
import plotly.express as px

# ── Configuration de la page
st.set_page_config(
    page_title="Finances Publiques Guadeloupe",
    page_icon="🇬🇵",
    layout="wide"
)

# ── Chargement des données
df = pd.read_csv("guadeloupe_clean.csv")
df = df.rename(columns={
    "Nom 2024 Commune": "Commune",
    "Nom 2024 Département": "Département"
}).drop(columns=["Montant"])

# ── Titre principal
st.title("💰 Finances Publiques des Communes de Guadeloupe 2024")
st.markdown("Source : OFGL — Observatoire des Finances et de la Gestion publique Locales")
st.divider()

# ── Sidebar
st.sidebar.title("🔍 Filtres")

communes = sorted(df["Commune"].unique())
commune_selectionnee = st.sidebar.multiselect(
    "Sélectionne une ou plusieurs communes",
    options=communes,
    default=communes
)

df_filtre = df[df["Commune"].isin(commune_selectionnee)]

# ── Kpis
depenses_totales = df_filtre[df_filtre["Agrégat"] == "Dépenses totales"]["Montant en millions"].sum()
recettes_totales = df_filtre[df_filtre["Agrégat"] == "Recettes totales"]["Montant en millions"].sum()
encours_dette = df_filtre[df_filtre["Agrégat"] == "Encours de dette"]["Montant en millions"].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Dépenses totales", value=f"{depenses_totales:.2f} M€")

with col2:
    st.metric(label="Recettes totales", value=f"{recettes_totales:.2f} M€")

with col3:
    st.metric(label="Encours de dette", value=f"{encours_dette:.2f} M€")


st.divider()


# ── Test
st.subheader("📋 Données détaillées")
st.dataframe(
    df_filtre[["Commune", "Agrégat", "Montant en millions", "Population totale", "Montant en € par habitant"]],
    use_container_width=True
)

# ── Barplot budget par commune
st.subheader("📊 Budget total par commune")

budget_par_commune = df_filtre.groupby("Commune")["Montant en millions"].sum().reset_index()

fig_1 = px.bar(
    budget_par_commune.sort_values("Montant en millions", ascending=False),
    x="Commune",
    y="Montant en millions",
    title="Budget total par commune — Guadeloupe 2024",
    color="Montant en millions",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_1, use_container_width=True)

# ── Pie chart agrégats clés
st.subheader("🥧 Répartition par agrégat")

agregats_cles = [
    "Dépenses totales",
    "Recettes totales",
    "Frais de personnel",
    "Impôts et taxes",
    "Epargne nette",
    "Encours de dette"
]



budget_agregats = df_filtre[df_filtre["Agrégat"].isin(agregats_cles)].groupby("Agrégat")["Montant en millions"].sum().reset_index()

fig_2 = px.pie(
    budget_agregats,
    values="Montant en millions",
    names="Agrégat",
    title="Répartition du budget selon les agrégats clés"
)

st.plotly_chart(fig_2, use_container_width=True)

communes_limitees = commune_selectionnee[:3]  # max 3
cols = st.columns(len(communes_limitees))

for i, commune in enumerate(communes_limitees):
    with cols[i]:
        # filtre les données pour cette commune uniquement
        df_commune = df_filtre[df_filtre["Commune"] == commune]
        # calcule les agrégats clés pour cette commune
        budget_commune = df_commune[df_commune["Agrégat"].isin(agregats_cles)].groupby("Agrégat")["Montant en millions"].sum().reset_index()
        # crée le pie chart
        fig = px.pie(
            budget_commune,
            values="Montant en millions",
            names="Agrégat",
            title=commune,
            height=350,
            width=350   
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Scatter plot population vs budget
st.subheader("📊 Corrélation entre population et budget")

population = df_filtre[["Commune", "Population totale"]].drop_duplicates()
budget_par_com_popul = pd.merge(budget_par_commune, population, on="Commune")

fig_3 = px.scatter(
        budget_par_com_popul,
        x="Population totale",
        y="Montant en millions",
        text="Commune",
        size="Montant en millions",
        title="Corrélation entre population et budget communal — Guadeloupe 2024",
        log_x=True,
        log_y=True,
        labels={
            "Population totale": "Population (échelle log)",
            "Montant en millions": "Budget total en M€ (échelle log)"
        }
    )

fig_3.update_traces(textposition="top center")
st.plotly_chart(fig_3, use_container_width=True)

# ── Heatmap budget par commune et agrégat
st.subheader("🔥 Budget et dépenses par commune et agrégat")

pivot = df_filtre[df_filtre["Agrégat"].isin(agregats_cles)].pivot_table(
        index="Commune",
        columns="Agrégat",
        values="Montant en millions",
        aggfunc="sum"
    )

pivot_sorted = pivot.sort_values("Dépenses totales", ascending=False)

fig_4=px.imshow(
    pivot_sorted,
    title="Budget par commune et agrégat — Guadeloupe 2024",
    color_continuous_scale="Blues",
    aspect="auto"
    )

st.plotly_chart(fig_4, use_container_width=True)

