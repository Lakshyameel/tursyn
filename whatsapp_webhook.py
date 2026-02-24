from flask import Flask, request
from voice_order_parser import parse_voice_order
from order_engine import process_order
from database import save_order
import pandas as pd

app = Flask(__name__)

menu = pd.read_csv("data/menu.csv")

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    text = request.json.get("message")

    order_json = parse_voice_order(text)
    items, total = process_order(order_json, menu)

    if total > 0:
        save_order(items, total, source="whatsapp")
        return {"status":"saved"}
    return {"status":"invalid"}

app.run(port=5001)