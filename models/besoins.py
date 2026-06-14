from utils.constantes import (
    PB_MCAL_ENTRETIEN_CHIEN, CA_MCAL_CHIEN, P_MCAL_CHIEN,
    PB_MCAL_ENTRETIEN_CHAT, CA_MCAL_CHAT, P_MCAL_CHAT,
)


def besoin_proteines_chien(bee):
    # Besoin proteique entretien chien (g PB/j) = 60 * (BEE/1000)
    return PB_MCAL_ENTRETIEN_CHIEN * (bee / 1000)


def besoin_calcium_chien(bee):
    # Besoin calcium entretien chien (g/j) = 1.6 * (BEE/1000)
    return CA_MCAL_CHIEN * (bee / 1000)


def besoin_phosphore_chien(bee):
    # Besoin phosphore entretien chien (g/j) = 1.2 * (BEE/1000)
    return P_MCAL_CHIEN * (bee / 1000)


def besoin_proteines_chat(bee):
    # Besoin proteique entretien chat (g PB/j)
    return PB_MCAL_ENTRETIEN_CHAT * (bee / 1000)


def besoin_calcium_chat(bee):
    # Besoin calcium entretien chat (g/j)
    return CA_MCAL_CHAT * (bee / 1000)


def besoin_phosphore_chat(bee):
    # Besoin phosphore entretien chat (g/j)
    return P_MCAL_CHAT * (bee / 1000)


def rpc_minimal(besoin_pb_g, bee):
    # RPC minimal requis en g PB/Mcal = besoin PB (g/j) / BEE (Mcal/j)
    return besoin_pb_g / (bee / 1000)


def rpc_aliment(pb_pourcent, em_kcal_par_kg):
    # RPC d un aliment donne en g PB/Mcal
    pb_g_par_kg = pb_pourcent * 10
    em_mcal_par_kg = em_kcal_par_kg / 1000
    return pb_g_par_kg / em_mcal_par_kg

