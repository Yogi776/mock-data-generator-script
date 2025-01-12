import json
import random
from datetime import datetime, timedelta

# Initialize the starting order_id
order_id = 1000

def generate_order_id():
    global order_id  # Access the global order_id variable
    # Increment the order_id to ensure uniqueness
    order_id += 1

    # Randomly assign a customer_id between 1 and 10
    customer_id = random.randint(1, 10)

    # Decide how many products to add to the cart, can be between 1 and 5
    num_products = random.randint(1, 5)

    products = []
    line_items = []
    prices = []
    statuses = []
    delivery_dates = []
    payment_methods = []
    shipment_methods = []
    order_date = datetime.now() - timedelta(days=random.randint(0, 30))
    order_date_str = order_date.strftime('%Y-%m-%d %H:%M:%S')

    for i in range(num_products):
        product_number = random.randint(1000, 1051)
        product_id = f"SKU-{product_number}"
        products.append(product_id)
        line_items.append(i + 1)  # Line item numbers starting from 1
        price = random.randint(1000, 5000)  # Generate a random price for each product
        prices.append(price)

        # Assign individual status to each product
        status = random.choices(
            ['Canceled', 'Delivered', 'Shipped'],
            weights=(10, 70, 20),
            k=1
        )[0]
        statuses.append(status)

        # Calculate individual delivery dates, 2 to 5 days after the order date
        if status != 'Canceled':  # Only calculate delivery dates for non-canceled products
            delivery_days = random.randint(2, 5)
            delivery_date = order_date + timedelta(days=delivery_days)
            delivery_date_str = delivery_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            delivery_date_str = "N/A"  # No delivery date for canceled products
        delivery_dates.append(delivery_date_str)

        # Randomly assign a payment method for each product
        payment_method = random.choice(['Credit Card', 'Apple Pay', 'COD', 'Debit Card', 'PayPal'])
        payment_methods.append(payment_method)

        # Randomly assign a shipment method for each product
        shipment_method = random.choice(['FedEx', 'USPS', 'UPS'])
        shipment_methods.append(shipment_method)

    # Create a dictionary to hold the order ID, customer ID, product IDs, line items, prices, order date, delivery dates, statuses, payment methods, and shipment methods
    order_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "product_ids": products,
        "line_items": line_items,
        "prices": prices,
        "order_date": order_date_str,
        "delivery_dates": delivery_dates,
        "order_status": statuses,
        "payment_methods": payment_methods,
        "shipment_methods": shipment_methods
    }

    # Convert the dictionary to JSON format
    order_json = json.dumps(order_data, indent=4)

    # Return the JSON data
    return order_json

# Initialize a counter for the while loop
counter = 0

# Generate and print order IDs with all details for 10 transactions
while counter < 10:
    print(generate_order_id())
    counter += 1
