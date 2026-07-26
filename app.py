# app.py
# Main entry point for the Retail Inventory Management web application.

from math import isfinite

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from models import db, Product, Order


# ==========================================================
# APPLICATION SETUP
# ==========================================================

# Create the Flask application.
app = Flask(__name__)

# Load settings from config.py.
app.config.from_object(Config)

# Connect SQLAlchemy to the Flask application.
db.init_app(app)


# ==========================================================
# PRODUCT MANAGEMENT HELPERS
# ==========================================================

PRODUCT_SORT_OPTIONS = {
    "id": ("ID", Product.id),
    "name": ("Name", Product.name),
    "category": ("Category", Product.category),
    "price": ("Price", Product.price),
    "quantity": ("Quantity", Product.quantity),
    "reorder_level": ("Reorder Level", Product.reorder_level),
}

STOCK_STATUS_OPTIONS = (
    ("in_stock", "In Stock"),
    ("low_stock", "Low Stock"),
    ("out_of_stock", "Out of Stock"),
)


def get_product_stock_status(product):
    """Return the display metadata for a product's calculated stock status."""
    if product.quantity == 0:
        return {
            "key": "out_of_stock",
            "label": "Out of Stock",
            "badge_class": "text-bg-danger",
        }

    if product.quantity <= product.reorder_level:
        return {
            "key": "low_stock",
            "label": "Low Stock",
            "badge_class": "text-bg-warning",
        }

    return {
        "key": "in_stock",
        "label": "In Stock",
        "badge_class": "text-bg-success",
    }


def get_stock_status_condition(status):
    """Return the allowlisted SQL condition matching the stock-status rules."""
    conditions = {
        "in_stock": Product.quantity > Product.reorder_level,
        "low_stock": and_(
            Product.quantity > 0,
            Product.quantity <= Product.reorder_level,
        ),
        "out_of_stock": Product.quantity == 0,
    }
    return conditions.get(status)


def validate_product_form(form):
    """Validate and normalize the shared Add/Edit Product form."""
    values = {
        "name": form.get("name", "").strip(),
        "category": form.get("category", "").strip(),
        "supplier": form.get("supplier", "").strip(),
        "price": form.get("price", "").strip(),
        "quantity": form.get("quantity", "").strip(),
        "reorder_level": form.get("reorder_level", "").strip(),
    }
    errors = {}

    for field, label in (
        ("name", "Name"),
        ("category", "Category"),
        ("supplier", "Supplier"),
    ):
        if not values[field]:
            errors[field] = f"{label} is required."
        elif len(values[field]) > 100:
            errors[field] = f"{label} must be 100 characters or fewer."

    price = None
    try:
        price = float(values["price"])
        if not isfinite(price) or price <= 0:
            errors["price"] = "Price must be greater than 0."
    except (TypeError, ValueError):
        errors["price"] = "Enter a valid price greater than 0."

    quantity = None
    try:
        quantity = int(values["quantity"])
        if quantity < 0:
            errors["quantity"] = "Quantity must be 0 or greater."
    except (TypeError, ValueError):
        errors["quantity"] = "Enter a valid whole-number quantity."

    reorder_level = None
    try:
        reorder_level = int(values["reorder_level"])
        if reorder_level < 0:
            errors["reorder_level"] = "Reorder Level must be 0 or greater."
    except (TypeError, ValueError):
        errors["reorder_level"] = "Enter a valid whole-number reorder level."

    cleaned_data = None
    if not errors:
        cleaned_data = {
            "name": values["name"],
            "category": values["category"],
            "supplier": values["supplier"],
            "price": price,
            "quantity": quantity,
            "reorder_level": reorder_level,
        }

    return cleaned_data, values, errors


def get_product_form_values(product=None):
    """Return form-ready values for a new or existing product."""
    if product is None:
        return {
            "name": "",
            "category": "",
            "supplier": "",
            "price": "",
            "quantity": "0",
            "reorder_level": "5",
        }

    return {
        "name": product.name,
        "category": product.category,
        "supplier": product.supplier,
        "price": str(product.price),
        "quantity": str(product.quantity),
        "reorder_level": str(product.reorder_level),
    }


# ==========================================================
# ROUTES
# ==========================================================

@app.route("/")
def home():
    """
    Redirect the root URL to the main dashboard.
    This makes the dashboard the application's default landing page.
    """
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    """
    Display the inventory dashboard with key product and order statistics.
    """

    # Count all products stored in the products table.
    total_products = Product.query.count()

    # Retrieve all products to calculate total inventory value.
    products = Product.query.all()

    # Calculate the total value of the current inventory.
    inventory_value = sum(
        product.quantity * product.price
        for product in products
    )

    # Count products whose current quantity reached
    # or dropped below their reorder level.
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.reorder_level
    ).count()

    # Count all orders stored in the orders table.
    total_orders = Order.query.count()

    # Send all dashboard statistics to dashboard.html.
    return render_template(
        "dashboard.html",
        total_products=total_products,
        inventory_value=inventory_value,
        low_stock_products=low_stock_products,
        total_orders=total_orders
    )


@app.route("/products")
def products():
    """
    Display searchable, filterable, and safely sortable products.
    """
    search = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "").strip()
    selected_supplier = request.args.get("supplier", "").strip()
    selected_stock_status = request.args.get("stock_status", "").strip()
    selected_sort = request.args.get("sort", "id").strip()
    selected_direction = request.args.get("direction", "asc").strip()

    if selected_stock_status not in dict(STOCK_STATUS_OPTIONS):
        selected_stock_status = ""
    if selected_sort not in PRODUCT_SORT_OPTIONS:
        selected_sort = "id"
    if selected_direction not in {"asc", "desc"}:
        selected_direction = "asc"

    query = Product.query

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.category.ilike(search_term),
                Product.supplier.ilike(search_term),
            )
        )

    if selected_category:
        query = query.filter(Product.category == selected_category)
    if selected_supplier:
        query = query.filter(Product.supplier == selected_supplier)

    stock_condition = get_stock_status_condition(selected_stock_status)
    if stock_condition is not None:
        query = query.filter(stock_condition)

    sort_column = PRODUCT_SORT_OPTIONS[selected_sort][1]
    sort_expression = (
        sort_column.desc()
        if selected_direction == "desc"
        else sort_column.asc()
    )
    order_expressions = [sort_expression]
    if selected_sort != "id":
        order_expressions.append(Product.id.asc())
    all_products = query.order_by(*order_expressions).all()

    categories = [
        category
        for (category,) in (
            db.session.query(Product.category)
            .filter(Product.category.isnot(None), Product.category != "")
            .distinct()
            .order_by(Product.category.asc())
            .all()
        )
    ]
    suppliers = [
        supplier
        for (supplier,) in (
            db.session.query(Product.supplier)
            .filter(Product.supplier.isnot(None), Product.supplier != "")
            .distinct()
            .order_by(Product.supplier.asc())
            .all()
        )
    ]

    stock_statuses = {
        product.id: get_product_stock_status(product)
        for product in all_products
    }

    return render_template(
        "products/list.html",
        products=all_products,
        categories=categories,
        suppliers=suppliers,
        stock_statuses=stock_statuses,
        stock_status_options=STOCK_STATUS_OPTIONS,
        sort_options=PRODUCT_SORT_OPTIONS,
        search=search,
        selected_category=selected_category,
        selected_supplier=selected_supplier,
        selected_stock_status=selected_stock_status,
        selected_sort=selected_sort,
        selected_direction=selected_direction,
        has_active_filters=bool(
            search
            or selected_category
            or selected_supplier
            or selected_stock_status
        ),
    )


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    """
    Display and process the Add Product form.
    """
    form_values = get_product_form_values()
    errors = {}

    if request.method == "POST":
        product_data, form_values, errors = validate_product_form(request.form)

        if not errors:
            product = Product(**product_data)
            try:
                db.session.add(product)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                flash(
                    "The product could not be saved. Please try again.",
                    "danger",
                )
            else:
                flash(f'"{product.name}" was added successfully.', "success")
                return redirect(
                    url_for("product_details", product_id=product.id)
                )

    return render_template(
        "products/add.html",
        form_values=form_values,
        errors=errors,
    )


@app.route("/products/<int:product_id>")
def product_details(product_id):
    """Display all stored details for one product."""
    product = Product.query.get_or_404(product_id)
    return render_template(
        "products/details.html",
        product=product,
        stock_status=get_product_stock_status(product),
    )


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    """Display and process the Edit Product form."""
    product = Product.query.get_or_404(product_id)
    form_values = get_product_form_values(product)
    errors = {}

    if request.method == "POST":
        product_data, form_values, errors = validate_product_form(request.form)

        if not errors:
            product.name = product_data["name"]
            product.category = product_data["category"]
            product.supplier = product_data["supplier"]
            product.price = product_data["price"]
            product.quantity = product_data["quantity"]
            product.reorder_level = product_data["reorder_level"]

            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                flash(
                    "The product changes could not be saved. Please try again.",
                    "danger",
                )
            else:
                flash(f'"{product.name}" was updated successfully.', "success")
                return redirect(
                    url_for("product_details", product_id=product.id)
                )

    return render_template(
        "products/edit.html",
        product=product,
        form_values=form_values,
        errors=errors,
    )


@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    """Delete an unreferenced product after confirmation."""
    product = Product.query.get_or_404(product_id)

    if product.order_items:
        flash(
            "This product cannot be deleted because it is used in an existing order.",
            "warning",
        )
        return redirect(url_for("product_details", product_id=product.id))

    product_name = product.name
    try:
        db.session.delete(product)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash(
            "The product could not be deleted. It may be referenced by other records.",
            "danger",
        )
    else:
        flash(f'"{product_name}" was deleted successfully.', "success")

    return redirect(url_for("products"))


# ==========================================================
# APPLICATION START
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)
