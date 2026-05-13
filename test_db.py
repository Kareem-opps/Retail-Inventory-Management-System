# test_db.py
# This script tests the database connection and models.
# It creates tables, adds a product, places an order, and verifies stock reduction.

from flask import Flask
from config import Config
from models import db, Product, Order, User

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config.from_object(Config)

# Connect SQLAlchemy to the app
db.init_app(app)

# Run everything inside an application context
with app.app_context():
    
    # Step 1: Create all tables in the database
    db.create_all()
    print("All tables created successfully.")
    
    # Step 2: Add a test product
    print("\n--- Adding Products ---")
    p1 = Product.add_product("Gaming Laptop", "Electronics", 10, 15000.00, "Dell")
    print(f"Added: {p1}")
    
    p2 = Product.add_product("Wireless Mouse", "Accessories", 50, 350.00, "Logitech")
    print(f"Added: {p2}")
    
    p3 = Product.add_product("USB Cable", "Accessories", 100, 50.00, "Generic")
    print(f"Added: {p3}")
    
    # Step 3: Show all products from the database
    print("\n--- All Products in Database ---")
    all_products = Product.query.all()
    for p in all_products:
        print(f"ID: {p.id} | Name: {p.name} | Category: {p.category} | Qty: {p.quantity} | Price: {p.price} EGP")
    
    # Step 4: Update a product
    print("\n--- Updating Product ---")
    Product.update_product(1, price=14500.00, supplier="Dell Technologies")
    updated_p = Product.query.get(1)
    print(f"Updated: {updated_p}")
    
    # Step 5: Create an order and add items
    print("\n--- Placing an Order ---")
    order = Order.create_order("Karim Mohamed", "01099999999")
    print(f"Order created: {order}")
    
    success1 = order.add_item(1, 2)  # Order 2 Gaming Laptops
    print(f"Added 2x Gaming Laptop to order: {success1}")
    
    success2 = order.add_item(2, 5)  # Order 5 Wireless Mice
    print(f"Added 5x Wireless Mouse to order: {success2}")
    
    # Step 6: Verify stock was reduced
    print("\n--- Stock After Order ---")
    p1_after = Product.query.get(1)
    p2_after = Product.query.get(2)
    print(f"Gaming Laptop: was 10, now {p1_after.quantity}")
    print(f"Wireless Mouse: was 50, now {p2_after.quantity}")
    
    # Step 7: Test insufficient stock
    print("\n--- Testing Insufficient Stock ---")
    success3 = order.add_item(1, 100)  # Try ordering 100 laptops (only 8 left)
    print(f"Tried ordering 100 laptops: {success3} (should be False)")
    
    # Step 8: Show all orders
    print("\n--- All Orders in Database ---")
    all_orders = Order.query.all()
    for o in all_orders:
        print(f"Order ID: {o.id} | Customer: {o.customer_name} | Status: {o.status}")
        for item in o.items:
            print(f"  - {item.product.name} x{item.quantity}")
    
    print("\n" + "="*50)
    print("All tests completed successfully.")
    print("="*50)