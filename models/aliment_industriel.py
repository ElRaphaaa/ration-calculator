def calculer_ena(pb, mg, cb, mm, eau):
    # ENA = 100 - (MG + PB + CB + Mm + eau), tous en %
    ena = 100 - (mg + pb + cb + mm + eau)
    return max(ena, 0)


def calculer_em_reglementaire(pb, mg, ena):
    # Formule Atwater modifiee reglementaire (Arrete 8/04/1999)
    # EM en MJ/kg, conversion en kcal/kg ensuite
    em_mj_par_kg = 0.1464 * pb + 0.3556 * mg + 0.1464 * ena
    em_kcal_par_kg = em_mj_par_kg * 1000 / 4.1855
    return em_kcal_par_kg


def calculer_em_chat_humide(pb, mg, ena):
    # Formule specifique chat si eau > 14% (NRC 1986)
    # Resultat directement en kcal/100g -> on multiplie par 10 pour kcal/kg
    em_kcal_100g = 0.1632 * pb + 0.3222 * mg + 0.1255 * ena - 0.2092
    return em_kcal_100g * 10


def calculer_em_aliment(pb, mg, cb, mm, eau, espece="Chien"):
    ena = calculer_ena(pb, mg, cb, mm, eau)

    if espece == "Chat" and eau > 14:
        em = calculer_em_chat_humide(pb, mg, ena)
    else:
        em = calculer_em_reglementaire(pb, mg, ena)

    return em, ena


def calculer_rpc_aliment(pb, em_kcal_par_kg):
    # RPC en g PB/Mcal
    pb_g_par_kg = pb * 10  # %PB sur matiere telle quelle -> g/kg
    em_mcal_par_kg = em_kcal_par_kg / 1000
    return pb_g_par_kg / em_mcal_par_kg


def calculer_quantite_journaliere(be_kcal, em_kcal_par_kg):
    # Quantite d aliment a donner par jour (en grammes)
    if em_kcal_par_kg <= 0:
        return 0
    return (be_kcal / em_kcal_par_kg) * 1000
