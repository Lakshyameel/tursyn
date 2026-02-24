import re

def process_order(order_json, menu_df):
    price_map = dict(zip(menu_df["Item"].str.lower(), menu_df["Price"]))

    total = 0
    valid_items = []

    for item in order_json["items"]:
        name = item["name"].lower()
        qty = item.get("qty", 1)

        # safer matching
        match = next(
            (m for m in price_map if m == name or m in name.split()),
            None
        )

        if match:
            total += qty * price_map[match]
            valid_items.append(f"{qty} {match}")

    if not valid_items:
        return None, 0

    return ", ".join(valid_items), total