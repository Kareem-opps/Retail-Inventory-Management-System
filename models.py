# models.py
# Database models for the Inventory Management System.
# These classes replace the in-memory lists with permanent database tables.
# SQLAlchemy handles all SQL queries automatically - you write Python, not SQL.

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy object.
# We create it here and connect it to the Flask app later in app.py.
db = SQLAlchemy()


# ============================================================================
# USER MODEL
# Table: users
# Purpose: Stores login credentials for system access.
# ============================================================================
class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Explicit table name
    
    # Primary key, auto-increments automatically
    id = db.Column(db.Integer, primary_key=True)
    
    # Username must be unique so two users cannot have the same name
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # Stores hashed password, NEVER plain text.
    # 200 characters gives enough room for the hash algorithm output.
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Automatically sets the timestamp when a user is created
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        # String representation for debugging
        return f"<User {self.username}>"


# ============================================================================
# PRODUCT MODEL
# Table: products
# Purpose: Replaces your original Product class and Product.inventory list.
#          All products are now rows in this table, permanently stored.
# ============================================================================
class Product(db.Model):
    __tablename__ = 'products'
    
    # Primary key, auto-increments.
    # This replaces your manual product_id generation (last_id + 1).
    id = db.Column(db.Integer, primary_key=True)
    
    # Product details - these map directly to your original __init__ parameters
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)
    supplier = db.Column(db.String(100), nullable=False)
    
    # Minimum stock quantity before the product is considered low stock.
    reorder_level = db.Column(
    db.Integer,
    nullable=False,
    default=5
    )
    
    # Timestamp for when the product was added
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: connects Product to OrderItem.
    # This lets us see which orders contain this product.
    # backref='product' means OrderItem gets a .product attribute to access the full Product object.
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    # ========== CLASS METHODS (replace your @classmethod methods) ==========
    # These work exactly like your original methods, but interact with the database
    # instead of modifying Product.inventory list.
    
    @classmethod
    def add_product(cls, name, category, quantity, price, supplier):
        """
        Creates a new product and saves it to the database.
        This replaces: Product.inventory.append(new_product)
        """
        new_product = cls(
            name=name,
            category=category,
            quantity=quantity,
            price=price,
            supplier=supplier
        )
        # Stage the new product for saving
        db.session.add(new_product)
        # Commit (save) to the database permanently
        db.session.commit()
        return new_product

    @classmethod
    def update_product(cls, product_id, quantity=None, price=None, supplier=None):
        """
        Updates a product by ID.
        Only modifies fields that are provided (not None).
        Returns the updated product or None if not found.
        """
        # cls.query.get() is equivalent to: SELECT * FROM products WHERE id = product_id
        product = cls.query.get(product_id)
        if product:
            if quantity is not None:
                product.quantity = quantity
            if price is not None:
                product.price = price
            if supplier is not None:
                product.supplier = supplier
            # Save changes to database
            db.session.commit()
        return product

    @classmethod
    def delete_product(cls, product_id):
        """
        Deletes a product by ID from the database.
        Returns True if found and deleted, False otherwise.
        This replaces: Product.inventory.remove(product)
        """
        product = cls.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f"<Product {self.name} (ID: {self.id})>"


# ============================================================================
# ORDER MODEL
# Table: orders
# Purpose: Replaces your Order class and Order.orders_list.
#          Represents a customer order header.
#          Order items are stored separately in OrderItem table.
# ============================================================================
class Order(db.Model):
    __tablename__ = 'orders'
    
    # Primary key, auto-increments starting from 1.
    # Your original code started from 1001 - you can set that manually if needed,
    # but auto-increment from 1 is cleaner.
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer information stored directly on the order
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    
    # Timestamp for when order was created
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Order status for tracking (Pending, Shipped, Delivered, Cancelled)
    status = db.Column(db.String(20), default='Pending')
    
    # Relationship: one Order has many OrderItems.
    # lazy=True means OrderItems are loaded when accessed.
    # cascade='all, delete-orphan' means deleting an Order also deletes its OrderItems.
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @classmethod
    def create_order(cls, customer_name=None, customer_phone=None):
        """
        Creates a new empty order and saves it to the database.
        This is called before adding individual items to the order.
        Replaces your original Order.create_order().
        """
        new_order = cls(
            customer_name=customer_name,
            customer_phone=customer_phone
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order

    def add_item(self, product_id, quantity):
        """
        Adds a product to this order and reduces stock.
        Checks if enough quantity is available before adding.
        This replaces your original place_order() method.
        Returns True if successful, False if product not found or insufficient stock.
        """
        # Find the product by ID
        product = Product.query.get(product_id)
        
        # Check if product exists and has enough quantity
        if product and product.quantity >= quantity:
            # Reduce the stock (same logic as your original code)
            product.quantity -= quantity
            
            # Create a new OrderItem linking this order to the product
            item = OrderItem(
                order_id=self.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(item)
            
            # Save both the stock reduction and the new order item
            db.session.commit()
            return True
        
        return False

    def get_total(self):
        """
        Calculates the total price of this order.
        Loops through all order items and sums (quantity * price).
        """
        total = 0
        for item in self.items:
            total += item.quantity * item.product.price
        return total

    def __repr__(self):
        return f"<Order {self.id} by {self.customer_name}>"


# ============================================================================
# ORDER ITEM MODEL
# Table: order_items
# Purpose: Each row represents one product inside an order.
#          This is a junction table connecting orders and products.
#          One order can have many order_items.
# ============================================================================
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key linking to the orders table
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    # Foreign key linking to the products table
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Quantity of this product in the order
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<OrderItem: Product {self.product_id} x{self.quantity} in Order {self.order_id}>"