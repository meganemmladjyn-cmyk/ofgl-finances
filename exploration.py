import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd

    ################################################

    # Nettoyage (J1)

    ################################################

    df = pd.read_csv("ofgl-base-communes.csv", sep=";")
    #print(df.shape)
    #print(df.head())

    #Sélectionner les colones utiles
    df_guadeloupe= df[["Exercice","Nom 2024 Commune","Nom 2024 Département","Agrégat",
        "Montant","Montant en millions","Population totale","Montant en € par habitant"]]

    #print(df_guadeloupe.shape)
    #print(df_guadeloupe.head())

    #Détecter les valeurs maquantes
    #print(df_guadeloupe[df_guadeloupe["Montant"]==0].shape)
    #print(df_guadeloupe[df_guadeloupe["Montant"] == 0]["Nom 2024 Commune"].value_counts())
    #print(df_guadeloupe[df_guadeloupe["Montant"] == 0]["Agrégat"].value_counts())

    # 810 lignes avec Montant = 0 — données valides
    # Correspondent à des postes budgétaires non utilisés par certaines communes

    #--------

    #Recherche des doublons et des valeur null
    #print(df_guadeloupe.isnull().sum())
    #print(df_guadeloupe.duplicated().sum())
    #print(df_guadeloupe[df_guadeloupe.duplicated(keep=False)].sort_values("Nom 2024 Commune")[["Nom 2024 Commune", "Agrégat", "Montant", "Population totale"]].head(10))
    df_guadeloupe=df_guadeloupe.drop_duplicates(keep='first')
    #print(df_guadeloupe.shape)
    #print(df_guadeloupe.duplicated().sum())

    #--------

    #Vérifier les types de données
    #print(df_guadeloupe.dtypes)

    #--------

    #Exporter
    df_guadeloupe.to_csv('guadeloupe_clean.csv' , index = False)
    #print("Export réussi")



    ################################################

    # Analyse exploratoire (J2)

    ################################################

    df = pd.read_csv("guadeloupe_clean.csv")
    #print(df.shape)
    print(df.head())

    df=df.rename(columns={"Nom 2024 Commune" : "Commune","Nom 2024 Département" : "Département"}).drop(columns=["Montant"])

    #Répartition du budget par commune
    budget_par_commune=df.groupby("Commune")["Montant en millions"].sum().reset_index()
    budget_par_commune


    #Top 5 communes par montant total
    Top_5_gros_budget=budget_par_commune.sort_values(by='Montant en millions', ascending = False)
    #print(Top_5_gros_budget.head())

    Top_5_petit_budget=budget_par_commune.sort_values(by='Montant en millions', ascending = True)
    #print(Top_5_petit_budget.head())


    #Répartition par agrégat
    budget_par_agregat=df.groupby("Agrégat")["Montant en millions"].sum().reset_index()
    budget_par_agregat

    agregats_cles = [
        "Dépenses totales",
        "Recettes totales",
        "Frais de personnel",
        "Impôts et taxes",
        "Epargne nette",
        "Encours de dette"
    ]

    budget_agregats_cles = budget_par_agregat[budget_par_agregat["Agrégat"].isin(agregats_cles)]
    budget_agregats_cles


    # Montant moyen par habitant par commune
    montant_moy_par_habitant = df.groupby("Commune")["Montant en € par habitant"].mean().reset_index()
    montant_moy_par_habitant

    #Détection anomalies 
    #print(df["Montant en € par habitant"].describe())

    #print(df[df["Montant en € par habitant"] < 0][["Commune", "Agrégat", "Montant en € par habitant"]].head(10))
    #print(df[df["Montant en € par habitant"] > 2000][["Commune", "Agrégat", "Montant en € par habitant"]].head(10))
    # Valeurs négatives sur Epargne brute — normales comptablement
    # Valeurs élevées sur petites communes — effet population faible


    ################################################

    # Les visualisations (J3)

    ################################################

    import plotly.express as px

    fig = px.bar(budget_par_commune.sort_values("Montant en millions", ascending =False),
              x="Commune",
              y='Montant en millions',
              title="Budget total par commune - Guadeloupe 2024",
              color="Montant en millions", 
              color_continuous_scale="Blues"
    )
    #fig.show()

    fig_2=px.pie(data_frame=budget_agregats_cles, 
                values= "Montant en millions",
                names="Agrégat",
                title= 'repartition du budget selon les agrégat clés'
    )
    #fig_2.show()

    population = df[["Commune", "Population totale"]].drop_duplicates()
    budget_par_com_popul=pd.merge(budget_par_commune, population, on="Commune")

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
    #fig_3.show()

    pivot = df[df["Agrégat"].isin(agregats_cles)].pivot_table(
        index="Commune",
        columns="Agrégat",
        values="Montant en millions",
        aggfunc="sum"
    )
    pivot

    pivot_sorted = pivot.sort_values("Dépenses totales", ascending=False)

    fig_4=px.imshow(
        pivot_sorted,
        title="Budget par commune et agrégat — Guadeloupe 2024",
        color_continuous_scale="Blues",
        aspect="auto"
    )
    fig_4.show()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
