# Constantes nutritionnelles - chien et chat (NRC 2006 / valeurs retenues pour calculs)

# Coefficients besoin energetique d'entretien (BEE)
BEE_COEF_CHIEN = 130       # kcal EM/j = 130 * Pidéal^0.75 (NRC 2006, valeur TD)
BEE_EXPOSANT_CHIEN = 0.75

BEE_COEF_CHAT = 100        # kcal EM/j = 100 * Pidéal^0.67 (NRC 2006)
BEE_EXPOSANT_CHAT = 0.67

# Besoins entretien (g/Mcal)
PB_MCAL_ENTRETIEN_CHIEN = 60
CA_MCAL_CHIEN = 1.6
P_MCAL_CHIEN = 1.2

# Facteurs k2 - niveau d'activite/comportement (chien)
K2_OPTIONS = {
    "Hyperactif": 1.2,
    "Normal": 1.0,
    "Sedentaire / age": 0.9,
    "Tres calme": 0.8,
}

# Facteurs k1 - race (chien) - selection simplifiee pour commencer
K1_OPTIONS = {
    "Autre / non specifie": 1.0,
    "Races nordiques": 0.8,
    "Beagle": 0.9,
    "Labrador / Golden": 0.85,
    "Levriers, bergers belges/Beauce": 1.1,
}
