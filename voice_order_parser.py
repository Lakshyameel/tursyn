import re

def parse_voice_order(text):
    items = []
    parts = text.split(",")

    for p in parts:
        p = p.strip().lower()
        qty_match = re.search(r'\d+', p)
        qty = int(qty_match.group()) if qty_match else 1
        name = re.sub(r'\d+', '', p).strip()

        if name:
            items.append({"name": name, "qty": qty})

    return {"items": items}