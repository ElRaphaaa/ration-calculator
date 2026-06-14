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