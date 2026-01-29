import requests


def get_food_info(product_name):
    url = (
        "https://world.openfoodfacts.org/cgi/search.pl"
        f"?search_terms={product_name}&json=true"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return None

    products = r.json().get("products", [])
    if not products:
        return None

    p = products[0]
    return {
        "name": p.get("product_name", product_name),
        "calories": p.get("nutriments", {}).get("energy-kcal_100g", 0)
    }
