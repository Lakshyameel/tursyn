import re

number_words = {
    "one":1,"two":2,"to":2,"too":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,"ten":10
}

def extract_qty(text):
    digit = re.search(r'\d+', text)
    if digit:
        return int(digit.group())

    for word,val in number_words.items():
        if word in text:
            return val

    return 1


def llm_extract_order(text, menu_items):

    items = []
    parts = text.lower().split(",")

    for p in parts:
        qty = extract_qty(p)
        name = re.sub(r'\d+', '', p).strip()

        match = next((m for m in menu_items if m in name), None)

        if match:
            items.append({"name": match, "qty": qty})

    return {"items": items}