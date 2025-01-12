import json
import random
from datetime import datetime, timedelta

# Configuration Settings
number_of_orders = 10  # Number of orders to generate
start_order_id = 1000
customer_id_range = (1, 10)  # Range for customer IDs
product_id_range = (1000, 1051)  # Range for product numbers
price_range = (1000, 5000)  # Price range for each product
status_weights = (10, 70, 20)  # Weights for Canceled, Delivered, Shipped
delivery_days_range = (2, 5)  # Range of days for delivery after order date
order_date_past_days = 30  # How many days in the past can the order date be
num_products_range = (1, 5)  # Range for number of products per order
payment_methods = ['Credit Card', 'Apple Pay', 'COD', 'Debit Card', 'PayPal']
payment_method_weights = [30, 20, 10, 20, 20]  # Corresponding weights for payment methods
shipment_methods = ['FedEx', 'USPS', 'UPS']
shipment_method_weights = [40, 35, 25]  # Weights for shipment methods

# Initialize the starting order_id
order_id = start_order_id

def generate_order_id():
    global order_id  # Access the global order_id variable
    # Increment the order_id to ensure uniqueness
    order_id += 1

    # Randomly assign a customer_id
    customer_id = random.randint(*customer_id_range)

    # Decide how many products to add to the cart
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

    # Create the order data dictionary
    order_data = {
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

    return order_data

# Main logic to generate order data and save to a JSON file
orders = []
current_count = 0
while current_count < number_of_orders:
    orders.append(generate_order_id())
    current_count += 1

# Save to file
with open('order.json', 'w') as file:
    json.dump(orders, file, indent=4)
