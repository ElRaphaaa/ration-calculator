import streamlit as st
from models.energie import poids_ideal, bee_chien, bee_chat, be_final_chien
from models.besoins import (
    besoin_proteines_chien, besoin_calcium_chien, besoin_phosphore_chien,
    besoin_proteines_chat, besoin_calcium_chat, besoin_phosphore_chat,
    rpc_minimal,
)
from utils.constantes import K1_OPTIONS, K2_OPTIONS

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

    pb = besoin_proteines_chien(bee)
    ca = besoin_calcium_chien(bee)
    p = besoin_phosphore_chien(bee)

else:
    bee = bee_chat(pi)
    st.write(f"**BEE (entretien) :** {bee:.0f} kcal EM/j")
    be = bee  # pas de k1/k2 pour le chat pour l'instant
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
