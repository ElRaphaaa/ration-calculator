"""
Calculs des besoins energetiques - chien et chat (entretien)
"""

from utils.constantes import (
    BEE_COEF_CHIEN, BEE_EXPOSANT_CHIEN,
    BEE_COEF_CHAT, BEE_EXPOSANT_CHAT,
)


def poids_ideal(poids_reel: float, bcs: int) -> float:
    """
    Calcule le poids ideal a partir du poids reel et du BCS (1-9).
    Formule : Pi = Pr * 100 / (100 + (BCS - 5) * 10)
    """
    return poids_reel * 100 / (100 + (bcs - 5) * 10)


def bee_chien(poids_ideal_kg: float) -> float:
    """Besoin energetique d'entretien (BEE) chien, en kcal EM/j."""
    return BEE_COEF_CHIEN * (poids_ideal_kg ** BEE_EXPOSANT_CHIEN)


def bee_chat(poids_ideal_kg: float) -> float:
    """Besoin energetique d'entretien (BEE) chat, en kcal EM/j."""
    return BEE_COEF_CHAT * (poids_ideal_kg ** BEE_EXPOSANT_CHAT)


def be_final_chien(bee: float, k1: float = 1.0, k2: float = 1.0) -> float:
    """
    Besoin energetique corrige (BE) pour le chien a l'entretien.
    BE = BEE * k1 * k2
    """
    return bee * k1 * k2

def be_gestation_chienne(poids_ideal_kg, poids_mere_kg):
    # BE fin de gestation = Bee(Pi) + 26 * P_mere (kcal EM/j)
    # P_mere = poids a vide (hors produits de gestation)
    return bee_chien(poids_ideal_kg) + 26 * poids_mere_kg

def production_lait_45j(poids_mere_kg, nb_chiots):
    if poids_mere_kg < 8:
        c = 1.6
    elif poids_mere_kg <= 25:
        c = 1.8
    else:
        c = 2.0
    return poids_mere_kg * c + (nb_chiots - 4) * poids_mere_kg / 10


def be_lactation_chienne(poids_mere_kg, nb_chiots, semaine_lactation):
    n = min(nb_chiots, 4)
    m = max(nb_chiots - 4, 0)

    facteurs_l = {1: 0.75, 2: 0.95, 3: 1.1, 4: 1.2}
    l = facteurs_l.get(semaine_lactation, 1.2)

    return 145 * (poids_mere_kg ** 0.75) + poids_mere_kg * (24 * n + 12 * m) * l

def k3_croissance(poids_chiot_kg, poids_adulte_kg):
    return (1.8 - poids_chiot_kg / poids_adulte_kg) / 0.8


def be_croissance_chiot(poids_chiot_kg, poids_adulte_kg, seuil_nouveau_ne=0.05):
    ratio = poids_chiot_kg / poids_adulte_kg
    if ratio < seuil_nouveau_ne:
        return 250 * poids_chiot_kg
    k3 = k3_croissance(poids_chiot_kg, poids_adulte_kg)
    return bee_chien(poids_chiot_kg) * k3
