import streamlit as st
from models.energie import poids_ideal, bee_chien, bee_chat, be_final_chien
from models.besoins import (
    besoin_proteines_chien, besoin_calcium_chien, besoin_phosphore_chien,
    besoin_proteines_chat, besoin_calcium_chat, besoin_phosphore_chat,
    rpc_minimal,
)
from models.ration import (
    charger_matieres_premieres, charger_amv, construire_ration,
)
from models.aliment_industriel import (
    calculer_em_aliment, calculer_rpc_aliment, calculer_quantite_journaliere,
)
from utils.constantes import K1_OPTIONS, K2_OPTIONS

from models.besoins import (
    besoin_proteines_chien, besoin_calcium_chien, besoin_phosphore_chien,
    besoin_proteines_chat, besoin_calcium_chat, besoin_phosphore_chat,
    rpc_minimal, rpc_minimal_ajuste,
)

st.set_page_config(page_title="Calculateur de rations", page_icon="🐾")

st.title("🐾 Calculateur de rations - Chien & Chat")
st.caption("Version de test - entretien uniquement")

espece = st.selectbox("Espece", ["Chien", "Chat"])

poids_reel = st.number_input("Poids reel (kg)", min_value=0.1, value=20.0, step=0.1)
bcs = st.slider("BCS / NEC (1-9)", min_value=1, max_value=9, value=5)

pi = poids_ideal(poids_reel, bcs)
st.write(f"**Poids ideal estime :** {pi:.2f} kg")

if espece == "Chien":
    bee = bee_chien(pi)
    st.write(f"**BEE (entretien theorique) :** {bee:.0f} kcal EM/j")

    race = st.selectbox("Race / categorie (k1)", list(K1_OPTIONS.keys()))
    activite = st.selectbox("Niveau d'activite (k2)", list(K2_OPTIONS.keys()), index=1)

    k1 = K1_OPTIONS[race]
    k2 = K2_OPTIONS[activite]

    be = be_final_chien(bee, k1, k2)
    st.write(f"**BE corrige (k1={k1}, k2={k2}) :** {be:.0f} kcal EM/j")

    k_global = k1 * k2
    if k_global < 1:
        st.warning(
            f"k = k1 x k2 = {k_global:.2f} < 1 (restriction energetique). "
            f"Les besoins en PB/Ca/P restent calcules sur le BEE theorique (non restreint). "
            f"L'aliment choisi doit avoir un RPC >= {60/k_global:.0f} g PB/Mcal "
            f"(au lieu de 60) pour ne pas restreindre les proteines."
        )

    pb = besoin_proteines_chien(bee)
    ca = besoin_calcium_chien(bee)
    p = besoin_phosphore_chien(bee)

else:
    bee = bee_chat(pi)
    st.write(f"**BEE (entretien) :** {bee:.0f} kcal EM/j")
    be = bee
    st.info("Facteurs k1/k2 pour le chat a venir.")

    pb = besoin_proteines_chat(bee)
    ca = besoin_calcium_chat(bee)
    p = besoin_phosphore_chat(bee)

st.divider()
st.subheader("Besoins quotidiens (calcules sur le BEE theorique)")

col1, col2, col3 = st.columns(3)
col1.metric("Proteines (PB)", f"{pb:.1f} g/j")
col2.metric("Calcium (Ca)", f"{ca:.2f} g/j")
col3.metric("Phosphore (P)", f"{p:.2f} g/j")

rpc_min = rpc_minimal(pb, bee)
st.write(f"**RPC minimal requis :** {rpc_min:.0f} g PB/Mcal")
st.caption("L'aliment choisi doit avoir un RPC superieur ou egal a cette valeur.")

# --- Choix du type de ration ---
st.divider()
type_ration = st.radio("Type de ration", ["Ration menagere", "Aliment industriel"])

if type_ration == "Ration menagere":
    st.subheader("Construction d'une ration menagere")

    mp_df = charger_matieres_premieres()
    amv_df = charger_amv()

    noms_viandes = mp_df[mp_df["categorie"] == "viande"]["nom"].tolist()
    noms_huiles = mp_df[mp_df["categorie"] == "huile"]["nom"].tolist()
    noms_graisses = mp_df[mp_df["categorie"] == "graisse"]["nom"].tolist()
    noms_legumes = mp_df[mp_df["categorie"] == "legume"]["nom"].tolist()
    noms_glucides = mp_df[mp_df["categorie"] == "glucide"]["nom"].tolist()

    col_a, col_b = st.columns(2)
    nom_viande = col_a.selectbox("Source proteique (viande/poisson)", noms_viandes)
    nom_huile = col_b.selectbox("Huile", noms_huiles)
    nom_legume = col_a.selectbox("Legume", noms_legumes)
    nom_glucide = col_b.selectbox("Glucide", noms_glucides)

    if espece == "Chien":
        pct_pb_viande = 0.80
        pct_energie_huile = 0.05
        pct_energie_legume = 0.05
        nom_graisse = None
        pct_energie_graisse = 0.0
    else:
        pct_pb_viande = 0.90
        pct_energie_huile = 0.04   # 2-5% selon §4.1 (NRC 2006)
        pct_energie_legume = 0.03  # 2-4% selon §4.1 (NRC 2006)
        pct_energie_graisse = 0.0
        nom_graisse = col_a.selectbox("Graisse", noms_graisses)

    if st.button("Calculer la ration"):
        resultat = construire_ration(
            bee=bee, besoin_pb=pb, besoin_ca=ca, besoin_p=p,
            mp_df=mp_df, amv_df=amv_df,
            nom_viande=nom_viande, nom_huile=nom_huile,
            nom_legume=nom_legume, nom_glucide=nom_glucide,
            pct_pb_viande=pct_pb_viande,
            pct_energie_huile=pct_energie_huile,
            pct_energie_legume=pct_energie_legume,
            nom_graisse=nom_graisse,
            pct_energie_graisse=pct_energie_graisse,
        )

        st.write("### Quantites journalieres")
        st.write(f"- **{nom_viande}** : {resultat['qte_viande']:.0f} g")
        st.write(f"- **{nom_huile}** : {resultat['qte_huile']:.1f} g")
        if nom_graisse is not None:
            st.write(f"- **{nom_graisse}** : {resultat['qte_graisse']:.1f} g")
        st.write(f"- **{nom_legume}** : {resultat['qte_legume']:.0f} g")
        st.write(f"- **{nom_glucide}** : {resultat['qte_glucide']:.0f} g")

        total_ration = (
            resultat['qte_viande'] + resultat['qte_huile']
            + resultat.get('qte_graisse', 0) + resultat['qte_legume']
            + resultat['qte_glucide']
        )
        st.write(f"**Total ration de base (hors AMV) : {total_ration:.0f} g/j**")

        st.write("### Verification Ca/P")
        st.write(f"Ca apporte par la ration de base : {resultat['ca_base']:.2f} g")
        st.write(f"P apporte par la ration de base : {resultat['p_base']:.2f} g")
        st.write(f"Manque Ca : {resultat['manque_ca']:.2f} g")
        st.write(f"Manque P : {resultat['manque_p']:.2f} g")

        st.write("### Complement AMV")
        st.write(f"AMV recommande : **{resultat['amv_choisi']}**")
        st.write(f"Quantite AMV : {resultat['qte_amv']:.1f} g")

        st.write("### Rapport Ca/P final")
        if resultat["rapport_final"] is not None:
            rapport = resultat["rapport_final"]
            st.write(f"Rapport Ca/P final : **{rapport:.2f}**")
            if rapport < 1:
                st.error("Rapport Ca/P < 1 : ATTENTION, carence relative en calcium - ration desequilibree")
            elif rapport < 2:
                st.warning("Rapport Ca/P entre 1 et 2 : minimum vital respecte, mais recommandation pratique (>= 2) non atteinte")
            else:
                st.success("Rapport Ca/P >= 2 : OK (conforme a la recommandation pour rations menageres)")
        else:
            st.warning("Impossible de calculer le rapport final (P = 0)")

else:
    st.subheader("Verification d'un aliment industriel")
    st.caption("Renseigne les valeurs de l'etiquette (analyse moyenne, sur matiere telle quelle)")

    col_x, col_y, col_z = st.columns(3)
    pb_aliment = col_x.number_input("Proteines brutes (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
    mg_aliment = col_y.number_input("Matieres grasses (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.1)
    cb_aliment = col_z.number_input("Cellulose brute / fibres (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)

    col_x2, col_y2 = st.columns(2)
    mm_aliment = col_x2.number_input("Matieres minerales / cendres (%)", min_value=0.0, max_value=100.0, value=7.0, step=0.1)
    eau_aliment = col_y2.number_input("Humidite / eau (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)

    if st.button("Analyser l'aliment"):
        em, ena = calculer_em_aliment(pb_aliment, mg_aliment, cb_aliment, mm_aliment, eau_aliment, espece=espece)
        rpc = calculer_rpc_aliment(pb_aliment, em)
        quantite = calculer_quantite_journaliere(be, em)

        st.write("### Resultats du calcul")
        st.write(f"ENA (extractif non azote) : {ena:.1f} %")
        st.write(f"Energie metabolisable (EM) : **{em:.0f} kcal/kg**")
        st.write(f"RPC de l'aliment : **{rpc:.0f} g PB/Mcal**")

        st.write("### Comparaison aux besoins")
        st.write(f"RPC minimal requis : {rpc_min:.0f} g PB/Mcal")
        if rpc >= rpc_min:
            st.success(f"RPC suffisant ({rpc:.0f} >= {rpc_min:.0f})")
        else:
            st.error(f"RPC insuffisant ({rpc:.0f} < {rpc_min:.0f}) : aliment trop pauvre en proteines pour ce besoin")

        st.write("### Quantite journaliere recommandee")
        st.write(f"Sur la base du BE = {be:.0f} kcal/j : **{quantite:.0f} g/j**")

        