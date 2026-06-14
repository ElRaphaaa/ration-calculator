import pandas as pd


def charger_matieres_premieres(chemin="data/matieres_premieres.csv"):
    return pd.read_csv(chemin)


def charger_amv(chemin="data/amv.csv"):
    return pd.read_csv(chemin)


def construire_ration(bee, besoin_pb, besoin_ca, besoin_p,
                       mp_df, amv_df,
                       nom_viande, nom_huile, nom_legume, nom_glucide,
                       pct_pb_viande, pct_energie_huile, pct_energie_legume,
                       nom_graisse=None, pct_energie_graisse=0.0):
    viande = mp_df[mp_df["nom"] == nom_viande].iloc[0]
    huile = mp_df[mp_df["nom"] == nom_huile].iloc[0]
    legume = mp_df[mp_df["nom"] == nom_legume].iloc[0]
    glucide = mp_df[mp_df["nom"] == nom_glucide].iloc[0]

    # 1. Quantite de viande pour couvrir pct_pb_viande du besoin PB
    qte_viande = (pct_pb_viande * besoin_pb) / (viande["pb_g_100g"] / 100)

    # 2. Quantite d huile
    qte_huile = (pct_energie_huile * bee) / (huile["energie_kcal_100g"] / 100)

    # 3. Quantite de graisse (optionnelle, ex: chat)
    if nom_graisse is not None and pct_energie_graisse > 0:
        graisse = mp_df[mp_df["nom"] == nom_graisse].iloc[0]
        qte_graisse = (pct_energie_graisse * bee) / (graisse["energie_kcal_100g"] / 100)
    else:
        graisse = None
        qte_graisse = 0.0

    # 4. Quantite de legumes
    qte_legume = (pct_energie_legume * bee) / (legume["energie_kcal_100g"] / 100)

    # 5. Energie deja couverte
    energie_viande = qte_viande * viande["energie_kcal_100g"] / 100
    energie_huile = qte_huile * huile["energie_kcal_100g"] / 100
    energie_graisse = qte_graisse * graisse["energie_kcal_100g"] / 100 if graisse is not None else 0.0
    energie_legume = qte_legume * legume["energie_kcal_100g"] / 100
    energie_restante = bee - (energie_viande + energie_huile + energie_graisse + energie_legume)

    # 6. Quantite de glucide pour le reste de l energie
    qte_glucide = energie_restante / (glucide["energie_kcal_100g"] / 100)
    if qte_glucide < 0:
        qte_glucide = 0

    # 7. Apports Ca/P de la ration de base
    composants = [
        (qte_viande, viande),
        (qte_huile, huile),
        (qte_legume, legume),
        (qte_glucide, glucide),
    ]
    if graisse is not None:
        composants.append((qte_graisse, graisse))

    ca_base = sum(q * c["ca_g_100g"] / 100 for q, c in composants)
    p_base = sum(q * c["p_g_100g"] / 100 for q, c in composants)

    # 8. Manque Ca / P
    manque_ca = max(besoin_ca - ca_base, 0)
    manque_p = max(besoin_p - p_base, 0)

    # 9. Choix de l AMV
    if manque_p > 0:
        rapport_cible = manque_ca / manque_p
    else:
        rapport_cible = 999

    amv_df = amv_df.copy()
    amv_df["diff_rapport"] = (amv_df["rapport_ca_p"] - rapport_cible).abs()
    amv_choisi = amv_df.sort_values("diff_rapport").iloc[0]

    # 10. Quantite d AMV
    qte_amv_par_p = manque_p / (amv_choisi["pourcent_p"] / 100) if amv_choisi["pourcent_p"] > 0 else 0
    qte_amv_par_ca = manque_ca / (amv_choisi["pourcent_ca"] / 100) if amv_choisi["pourcent_ca"] > 0 else 0
    qte_amv = max(qte_amv_par_ca, qte_amv_par_p)

    # 11. Verification rapport Ca/P final
    ca_final = ca_base + qte_amv * amv_choisi["pourcent_ca"] / 100
    p_final = p_base + qte_amv * amv_choisi["pourcent_p"] / 100
    rapport_final = ca_final / p_final if p_final > 0 else None

    return {
        "qte_viande": qte_viande,
        "qte_huile": qte_huile,
        "qte_graisse": qte_graisse,
        "qte_legume": qte_legume,
        "qte_glucide": qte_glucide,
        "ca_base": ca_base,
        "p_base": p_base,
        "manque_ca": manque_ca,
        "manque_p": manque_p,
        "amv_choisi": amv_choisi["nom"],
        "qte_amv": qte_amv,
        "ca_final": ca_final,
        "p_final": p_final,
        "rapport_final": rapport_final,
    }
