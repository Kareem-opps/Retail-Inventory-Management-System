"""
This program is a simple inventory and order management system.

- The `Product` class manages all products in stock. 
  It lets you add products, update them, or delete them using unique `product_id`s.
  All products are stored in the shared class list `Product.inventory`.

- The `Order` class represents a customer's order. 
  It lets you place an order for a product, checks if enough stock is available,
  reduces the stock, and records the ordered items with customer information.

At the end, you can:
  - Add multiple products
  - Update or delete a product by ID
  - Place an order for any product
  - Access and print any product by its `product_id` as an employee.
"""

class Product:
    inventory = []  # Class variable: holds all product objects for the whole company.

    def __init__(self, product_id, name, category, quantity, price, supplier):
        # Initialize a single product with its basic info.
        self.product_id = product_id
        self.name = name 
        self.category = category
        self.quantity = quantity
        self.price = price
        self.supplier = supplier

    def __str__(self):
        # Make printing a product more readable.
        return (f"\nProduct ID: {self.product_id}, Name: {self.name}, "
                f"Category: {self.category}, Quantity: {self.quantity}, "
                f"Price: {self.price}, Supplier: {self.supplier}\n")

    @classmethod
    def add_product(cls, name, category, quantity, price, supplier):
        # Adds a new product with a unique ID.
        if len(cls.inventory) > 0:
            product_id = cls.inventory[-1].product_id + 1  # ID is last ID + 1
        else:
            product_id = 1  # Start with ID 1 if empty

        new_product = cls(product_id, name, category, quantity, price, supplier)
        cls.inventory.append(new_product)  # Add to inventory
        return f"{new_product}Product added successfully."  # Shows product details

    @classmethod
    def update_product(cls, product_id, quantity=None, price=None, supplier=None):
        # Updates quantity, price, or supplier for a specific product.
        for product in cls.inventory:
            if product.product_id == product_id:
                if quantity is not None:
                    product.quantity = quantity
                if price is not None:
                    product.price = price
                if supplier is not None:
                    product.supplier = supplier
                return f"Product ID {product_id} updated successfully."
        return f"Product ID {product_id} not found."

    @classmethod
    def delete_product(cls, product_id):
        # Deletes a product from the inventory by ID.
        for product in cls.inventory:
            if product.product_id == product_id:
                cls.inventory.remove(product)
                return f"Product ID {product_id} deleted successfully."
        return f"Product ID {product_id} not found."


class Order:
    orders_list = []  # Class variable to keep track of all orders

    def __init__(self, order_id, products, customer_info=None):
        """
        Initialize a new Order object.

        :param order_id: Unique ID for the order.
        :param products: A list of tuples, e.g., [(product_id, quantity), ...]
        :param customer_info: Optional dictionary with customer info (default: None)
        """
        self.order_id = order_id           # Unique ID for this order
        self.products = products           # List of (product_id, quantity) tuples
        self.customer_info = customer_info # Optional customer details

    @classmethod
    def create_order(cls, products=None, customer_info=None):  # Automatic Generator order_ID
        if len(cls.orders_list) > 0:
            order_id = cls.orders_list[-1].order_id + 1
        else:
            order_id = 1001

        new_order = cls(order_id, products or [], customer_info)
        cls.orders_list.append(new_order)
        return new_order

    def place_order(self, product_id, quantity, customer_info=None):
        """
        Places an order for a product:
         - Checks if product exists and has enough stock
         - Reduces stock by ordered quantity
         - Adds the item to this order's list
         - Optionally updates customer info
        """
        for product in Product.inventory:
            if product.product_id == product_id and product.quantity >= quantity:
                product.quantity -= quantity  # Reduce stock
                self.products.append((product_id, quantity))  # Record in this order

                if customer_info:
                    self.customer_info = customer_info  # Update customer info if given

                return f"Order placed successfully. Order ID: {self.order_id}"

        return "Order could not be placed. Product not found or insufficient quantity."

def cli():
    try:
        while True:
            print("\n====== Inventory & Order System ======")
            print("1. Add Product")
            print("2. View Inventory")
            print("3. Update Product")
            print("4. Delete Product")
            print("5. Place Order")
            print("6. View Inventory Value")
            print("7. Exit")
            
            choice = input("Enter your choice: ")

            if choice == "1":
                name = input("Name: ")
                category = input("Category: ")
                quantity = int(input("Quantity: "))
                price = float(input("Price: "))
                supplier = input("Supplier: ")
                print(Product.add_product(name, category, quantity, price, supplier))

            elif choice == "2":
                if not Product.inventory:
                    print("No products in inventory.")
                for p in Product.inventory:
                    print(p)

            elif choice == "3":
                pid = int(input("Enter Product ID to update: "))
                quantity = input("New Quantity (leave blank to skip): ")
                price = input("New Price (leave blank to skip): ")
                supplier = input("New Supplier (leave blank to skip): ")
                print(Product.update_product(
                    pid,
                    quantity=int(quantity) if quantity else None,
                    price=float(price) if price else None,
                    supplier=supplier if supplier else None))

            elif choice == "4":
                pid = int(input("Enter Product ID to delete: "))
                print(Product.delete_product(pid))

            elif choice == "5":
                pid = int(input("Enter Product ID to order: "))
                quantity = int(input("Enter quantity: "))
                name = input("Customer Name: ")
                phone = input("Customer Phone: ")
                order = Order.create_order()
                print(order.place_order(pid, quantity, {"name": name, "phone": phone}))

            elif choice == "6":
                total = sum(p.quantity * p.price for p in Product.inventory)
                print(f"Total inventory value: {total} EGP")

            elif choice == "7":
                print("Exiting program.")
                break

            else:
                print("Invalid choice. Try again.")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")

# To run Programe
if __name__ == "__main__":
    cli()