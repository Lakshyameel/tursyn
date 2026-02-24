import pandas as pd
import re
from database import create_orders_table, save_order, get_all_orders
from analytics import show_analytics

menu = pd.read_csv("data/menu.csv")

create_orders_table()

def place_order():
    print("\nMenu:\n")
    for index, row in menu.iterrows():
        print(f"{row['Item']} - ₹{row['Price']}")

    order_input = input("\nEnter your order (Example: 2 Pizza, 1 Coke): ")
    orders = order_input.split(",")

    total_bill = 0
    print("\nOrder Summary:\n")

    for order in orders:
        order = order.strip().lower()

        quantity_match = re.search(r'\d+', order)
        quantity = int(quantity_match.group()) if quantity_match else 1

        item_text = re.sub(r'\d+', '', order).strip()

        matched_item = None

        for index, row in menu.iterrows():
            if row["Item"].lower() in item_text:
                matched_item = row
                break

        if matched_item is not None:
            price = matched_item["Price"]
            item_total = quantity * price
            total_bill += item_total
            print(f"{quantity} {matched_item['Item']} = ₹{item_total}")
        else:
            print(f"Item not found for: {order}")

    print(f"\nTotal Bill = ₹{total_bill}")

    confirm = input("\nConfirm Order? (yes/no): ")

    if confirm.lower() == "yes":
        save_order(order_input, total_bill)
        print("Order Confirmed and Saved!")
    else:
        print("Order Cancelled.")


def view_orders():
    orders = get_all_orders()
    if not orders:
        print("\nNo orders found.")
        return

    print("\n===== ALL ORDERS =====\n")
    for row in orders:
        print(row)
    print("\n======================\n")


# 🔥 MAIN ADMIN LOOP
while True:
    print("\n====== AI RESTAURANT SYSTEM ======")
    print("1. Place Order")
    print("2. View Orders")
    print("3. View Analytics")
    print("4. Exit")

    choice = input("\nEnter choice: ")

    if choice == "1":
        place_order()
    elif choice == "2":
        view_orders()
    elif choice == "3":
        show_analytics()
    elif choice == "4":
        print("Exiting system...")
        break
    else:
        print("Invalid choice. Try again.")
