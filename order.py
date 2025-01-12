import json
import random
from datetime import datetime, timedelta
import logging
from tqdm import tqdm

# Setup logging for error handling and informational messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration Settings
number_of_orders = 1000000  # Set this to a larger number like 1000000 to simulate larger data generation
start_order_id = 1000
customer_id_range = (1, 1000)
product_id_range = (1000, 1051)
price_range = (1000, 5000)
status_weights = (10, 70, 20)
delivery_days_range = (2, 5)
order_date_past_days = 30
num_products_range = (1, 5)
payment_methods = ['Credit Card', 'Apple Pay', 'COD', 'Debit Card', 'PayPal']
payment_method_weights = [30, 20, 10, 20, 20]
shipment_methods = ['FedEx', 'USPS', 'UPS']
shipment_method_weights = [40, 35, 25]

# Initialize the starting order_id
order_id = start_order_id

def generate_order_id():
    global order_id  # Access the global order_id variable
    order_id += 1

    customer_id = random.randint(*customer_id_range)
    num_products = random.randint(*num_products_range)

    products = []
    line_items = []
    prices = []
    statuses = []
    delivery_dates = []
    payment_choices = []
    shipment_choices = []
    order_date = datetime.now() - timedelta(days=random.randint(0, order_date_past_days))
    order_date_str = order_date.strftime('%Y-%m-%d %H:%M:%S')

    for i in range(num_products):
        product_number = random.randint(*product_id_range)
        product_id = f"SKU-{product_number}"
        products.append(product_id)
        line_items.append(i + 1)
        price = random.randint(*price_range)
        prices.append(price)

        status = random.choices(['Canceled', 'Delivered', 'Shipped'], weights=status_weights, k=1)[0]
        statuses.append(status)

        if status != 'Canceled':
            delivery_days = random.randint(*delivery_days_range)
            delivery_date = order_date + timedelta(days=delivery_days)
            delivery_date_str = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            delivery_date_str = "N/A"
        delivery_dates.append(delivery_date_str)

        payment_choice = random.choices(payment_methods, weights=payment_method_weights, k=1)[0]
        payment_choices.append(payment_choice)

        shipment_choice = random.choices(shipment_methods, weights=shipment_method_weights, k=1)[0]
        shipment_choices.append(shipment_choice)

    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "product_ids": products,
        "line_items": line_items,
        "prices": prices,
        "order_date": order_date_str,
        "delivery_dates": delivery_dates,
        "statuses": statuses,
        "payment_methods": payment_choices,
        "shipment_methods": shipment_choices
    }

# Generate order data and save to a JSON file
orders = []
current_count = 0
with tqdm(total=number_of_orders, desc="Generating orders") as pbar:
    while current_count < number_of_orders:
        orders.append(generate_order_id())
        current_count += 1
        pbar.update(1)

# Save the collected data to a file in JSON format
try:
    with open('order.json', 'w') as file:
        json.dump(orders, file, indent=4)
    logging.info("Orders successfully saved to 'order.json'.")
except Exception as e:
    logging.error("Failed to write to file: %s", e)
