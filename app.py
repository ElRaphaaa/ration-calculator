import streamlit as st
from models.energie import (
    poids_ideal, bee_chien, bee_chat, be_final_chien,
    be_gestation_chienne, be_lactation_chienne, be_croissance_chiot, k3_croissance,
    be_gestation_chat, be_lactation_chat, be_croissance_chaton, c_croissance_chat,
)
from models.besoins import (
    besoin_proteines_chien, besoin_calcium_chien, besoin_phosphore_chien,
    besoin_proteines_chat, besoin_calcium_chat, besoin_phosphore_chat,
    besoin_proteines_gestation_chienne, besoin_calcium_gestation_chienne, besoin_phosphore_gestation_chienne,
    besoin_proteines_lactation_chienne, besoin_calcium_lactation_chienne, besoin_phosphore_lactation_chienne,
    besoin_proteines_croissance_chiot, besoin_calcium_croissance_chiot, besoin_phosphore_croissance_chiot,
    besoin_proteines_gestation_chatte, besoin_calcium_gestation_chatte, besoin_phosphore_gestation_chatte,
    besoin_proteines_lactation_chatte, besoin_calcium_lactation_chatte, besoin_phosphore_lactation_chatte,
    besoin_proteines_croissance_chaton, besoin_calcium_croissance_chaton, besoin_phosphore_croissance_chaton,
    rpc_minimal, rpc_minimal_ajuste,
)
from models.ration import (
    charger_matieres_premieres, charger_amv, construire_ration,
)
from models.aliment_industriel import (
    calculer_em_aliment, calculer_rpc_aliment, calculer_quantite_journaliere,
)
from utils.constantes import K1_OPTIONS, K2_OPTIONS

st.set_page_config(page_title="Calculateur de rations", page_icon="🐾", layout="centered")
st.markdown("""
<style>
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    h1 {
        color: #4A7C59;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# NAVIGATION (SIDEBAR)
# ============================================================
st.sidebar.title("🐾 Menu")

pages = {
    "🏠 Accueil": "accueil",
    "🧮 Besoins de l'animal": "besoins",
    "🍖 Ration": "ration",
    "☣️ Toxicologie": "toxicologie",
}

choix_page = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
page = pages[choix_page]

st.sidebar.divider()
st.sidebar.caption("Projet de these veterinaire - ENVA")
st.sidebar.caption("Outil pedagogique de rationnement")


# ============================================================
# PAGE ACCUEIL
# ============================================================
if page == "accueil":
    st.title("🐾 Calculateur de rations - Chien & Chat")
    st.subheader("Outil d'aide au rationnement pour chien et chat")

    st.write(
        "Cette application vous aide a estimer les besoins nutritionnels de votre "
        "animal et a construire une ration adaptee, qu'elle soit menagere ou industrielle."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("#### 🧮 Besoins")
            st.write("Calculez les besoins energetiques et nutritionnels de votre animal selon son stade physiologique.")
    with col2:
        with st.container(border=True):
            st.markdown("#### 🍖 Ration")
            st.write("Construisez une ration menagere equilibree ou analysez un aliment industriel.")
    with col3:
        with st.container(border=True):
            st.markdown("#### ☣️ Toxicologie")
            st.write("Consultez les substances potentiellement toxiques (module en construction).")

    st.divider()
    st.info("👈 Utilisez le menu a gauche pour naviguer entre les sections.")

# ============================================================
# PAGE BESOINS
# ============================================================
elif page == "besoins":
    st.title("🧮 Besoins de l'animal")

    espece = st.selectbox("Espece", ["Chien 🐕", "Chat 🐈"])
    espece = "Chien" if espece.startswith("Chien") else "Chat"

    poids_reel = st.number_input("Poids reel (kg)", min_value=0.1, value=20.0, step=0.1)
    bcs = st.slider("BCS / NEC (1-9)", min_value=1, max_value=9, value=5)

    pi = poids_ideal(poids_reel, bcs)
    st.write(f"**Poids ideal estime :** {pi:.2f} kg")

    if espece == "Chien":
        bee = bee_chien(pi)
        st.write(f"**BEE entretien theorique (poids ideal {pi:.1f} kg) :** {bee:.0f} kcal EM/j")
        st.caption("Valeur de reference pour le stade Entretien. Pour les autres stades, voir le BE specifique ci-dessous.")

        stade = st.selectbox("Stade physiologique", ["Entretien", "Gestation (dernier tiers)", "Lactation", "Croissance (chiot)"])

        if stade == "Entretien":
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

        elif stade == "Gestation (dernier tiers)":
            poids_mere = st.number_input("Poids de la mere a vide (kg)", min_value=0.1, value=poids_reel, step=0.1)

            be = be_gestation_chienne(pi, poids_mere)
            st.write(f"**BE gestation (fin de gestation) :** {be:.0f} kcal EM/j")
            st.caption("BE = BEE(Pi) + 26 x P_mere - formule applicable au dernier tiers de gestation")

            pb = besoin_proteines_gestation_chienne(be)
            ca = besoin_calcium_gestation_chienne(be)
            p = besoin_phosphore_gestation_chienne(be)

        elif stade == "Lactation":
            poids_mere = st.number_input("Poids de la mere a vide (kg)", min_value=0.1, value=poids_reel, step=0.1)
            nb_chiots = st.number_input("Nombre de chiots", min_value=1, value=6, step=1)
            semaine = st.selectbox("Semaine de lactation", [1, 2, 3, 4], index=2)

            be = be_lactation_chienne(poids_mere, nb_chiots, semaine)
            st.write(f"**BE lactation (semaine {semaine}) :** {be:.0f} kcal EM/j")
            st.caption("BE = 145 x P_mere^0.75 + [P_mere x (24n+12m) x L]")

            pb = besoin_proteines_lactation_chienne(be)
            ca = besoin_calcium_lactation_chienne(be)
            p = besoin_phosphore_lactation_chienne(be)

        else:
            poids_chiot = st.number_input("Poids actuel du chiot (kg)", min_value=0.05, value=poids_reel, step=0.05)
            poids_adulte = st.number_input("Poids adulte attendu (kg)", min_value=0.5, value=20.0, step=0.5)

            be = be_croissance_chiot(poids_chiot, poids_adulte)
            ratio = poids_chiot / poids_adulte

            if ratio < 0.05:
                st.write(f"**BE croissance (nouveau-ne) :** {be:.0f} kcal EM/j")
                st.caption("BE = 250 x Pj (formule nouveau-ne)")
            else:
                k3 = k3_croissance(poids_chiot, poids_adulte)
                st.write(f"**BE croissance :** {be:.0f} kcal EM/j")
                st.caption(f"BE = Bee(Pj) x k3, avec k3 = (1.8 - Pj/Pad)/0.8 = {k3:.2f}")

            pb = besoin_proteines_croissance_chiot(be)
            ca = besoin_calcium_croissance_chiot(be)
            p = besoin_phosphore_croissance_chiot(be)

    else:
        bee = bee_chat(pi)
        st.write(f"**BEE entretien theorique (poids ideal {pi:.1f} kg) :** {bee:.0f} kcal EM/j")
        st.caption("Valeur de reference pour le stade Entretien. Pour les autres stades, voir le BE specifique ci-dessous.")

        stade = st.selectbox("Stade physiologique", ["Entretien", "Gestation", "Lactation", "Croissance (chaton)"])

        if stade == "Entretien":
            be = bee
            st.write(f"**BE (entretien) :** {be:.0f} kcal EM/j")
            st.info("Facteurs k1/k2 pour le chat a venir.")

            pb = besoin_proteines_chat(bee)
            ca = besoin_calcium_chat(bee)
            p = besoin_phosphore_chat(bee)

        elif stade == "Gestation":
            poids_mere = st.number_input("Poids de la mere a vide (kg)", min_value=0.1, value=poids_reel, step=0.1)

            be = be_gestation_chat(poids_mere)
            st.write(f"**BE gestation :** {be:.0f} kcal EM/j")
            st.caption("BE = 140 x P_mere^0.67")

            pb = besoin_proteines_gestation_chatte(be)
            ca = besoin_calcium_gestation_chatte(be)
            p = besoin_phosphore_gestation_chatte(be)

        elif stade == "Lactation":
            poids_mere = st.number_input("Poids de la mere a vide (kg)", min_value=0.1, value=poids_reel, step=0.1)
            nb_chatons = st.number_input("Nombre de chatons", min_value=1, value=4, step=1)
            semaine = st.selectbox("Semaine de lactation", [1, 2, 3, 4, 5, 6, 7], index=2)

            be = be_lactation_chat(poids_mere, nb_chatons, semaine)
            st.write(f"**BE lactation (semaine {semaine}) :** {be:.0f} kcal EM/j")
            st.caption("BE = 100 x P_mere^0.67 + P_mere x N x L")

            pb = besoin_proteines_lactation_chatte(be)
            ca = besoin_calcium_lactation_chatte(be)
            p = besoin_phosphore_lactation_chatte(be)

        else:
            poids_chaton = st.number_input("Poids actuel du chaton (kg)", min_value=0.05, value=poids_reel, step=0.05)
            poids_adulte = st.number_input("Poids adulte attendu (kg)", min_value=0.5, value=4.0, step=0.5)

            be = be_croissance_chaton(poids_chaton, poids_adulte)
            ratio = poids_chaton / poids_adulte

            if ratio < 0.05:
                st.write(f"**BE croissance (nouveau-ne) :** {be:.0f} kcal EM/j")
                st.caption("BE = 250 x Pj (formule nouveau-ne)")
            else:
                c = c_croissance_chat(poids_chaton, poids_adulte)
                st.write(f"**BE croissance :** {be:.0f} kcal EM/j")
                st.caption(f"BE = 100 x Pj^0.67 x C, avec C = 6.7 x [exp(-0.189 x Pj/Pad) - 0.66] = {c:.2f}")

            pb = besoin_proteines_croissance_chaton(be)
            ca = besoin_calcium_croissance_chaton(be)
            p = besoin_phosphore_croissance_chaton(be)

    st.divider()
    st.subheader("Besoins quotidiens")

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Proteines (PB)", f"{pb:.1f} g/j")
        col2.metric("Calcium (Ca)", f"{ca:.2f} g/j")
        col3.metric("Phosphore (P)", f"{p:.2f} g/j")

    rpc_min = rpc_minimal(pb, be)
    st.write(f"**RPC minimal requis :** {rpc_min:.0f} g PB/Mcal")
    st.caption("L'aliment choisi doit avoir un RPC superieur ou egal a cette valeur.")

    with st.expander("ℹ️ Comprendre ces resultats"):
        st.write(
            "- **BE** : Besoin Energetique, la quantite d'energie (en kcal) que l'animal doit recevoir par jour.\n"
            "- **Proteines (PB)** : quantite de proteines brutes necessaires par jour.\n"
            "- **Calcium / Phosphore** : mineraux essentiels, leur equilibre (rapport Ca/P) est crucial "
            "notamment pour la croissance osseuse et la prevention de troubles musculo-squelettiques.\n"
            "- **RPC (Rapport Protido-Calorique)** : indique la concentration en proteines de l'aliment "
            "par rapport a son apport energetique. Un aliment doit avoir un RPC superieur ou egal "
            "a celui requis par l'animal pour couvrir ses besoins proteiques."
        )

    st.session_state["espece"] = espece
    st.session_state["stade"] = stade
    st.session_state["bee"] = bee
    st.session_state["be"] = be
    st.session_state["pb"] = pb
    st.session_state["ca"] = ca
    st.session_state["p"] = p
    st.session_state["rpc_min"] = rpc_min

    st.success("✅ Besoins calcules. Rendez-vous dans l'onglet 'Ration' pour construire la ration.")


# ============================================================
# PAGE RATION
# ============================================================
elif page == "ration":
    st.title("🍖 Construction de la ration")

    if "be" not in st.session_state:
        st.warning("⚠️ Renseignez d'abord les informations dans la section '🧮 Besoins de l'animal'.")
    else:
        espece = st.session_state["espece"]
        stade = st.session_state["stade"]
        bee = st.session_state["bee"]
        be = st.session_state["be"]
        pb = st.session_state["pb"]
        ca = st.session_state["ca"]
        p = st.session_state["p"]
        rpc_min = st.session_state["rpc_min"]

        emoji_espece = "🐕" if espece == "Chien" else "🐈"
        with st.container(border=True):
            st.markdown(f"### {emoji_espece} {espece} - {stade}")
            st.write(f"**Besoin energetique (BE) :** {be:.0f} kcal EM/j")

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
                if stade == "Entretien":
                    pct_pb_viande = 0.80
                else:
                    pct_pb_viande = 0.90
                pct_energie_huile = 0.05
                pct_energie_legume = 0.05
                nom_graisse = None
                pct_energie_graisse = 0.0
            else:
                pct_pb_viande = 0.90
                pct_energie_huile = 0.04
                pct_energie_legume = 0.03
                pct_energie_graisse = 0.0
                nom_graisse = col_a.selectbox("Graisse", noms_graisses)

            if st.button("Calculer la ration"):
                resultat = construire_ration(
                    bee=be, besoin_pb=pb, besoin_ca=ca, besoin_p=p,
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


# ============================================================
# PAGE TOXICOLOGIE
# ============================================================
else:
    st.title("☣️ Toxicologie")
    st.info("Module en construction - arrive prochainement !")