import requests


def rechercher_produit(code_barre):
    url = f"https://world.openpetfoodfacts.org/api/v2/product/{code_barre}.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except Exception:
        return None

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    nutriments = product.get("nutriments", {})
    nom = product.get("product_name", "Produit sans nom")

    pb = nutriments.get("proteins_100g")
    mg = nutriments.get("fat_100g")
    cb = nutriments.get("fiber_100g")
    mm = nutriments.get("ash_100g")
    eau = nutriments.get("water_100g")

    return {
        "nom": nom,
        "pb": pb,
        "mg": mg,
        "cb": cb,
        "mm": mm,
        "eau": eau,
    }
