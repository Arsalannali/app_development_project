"""
================================================================================
TRADING MODULE - Routes and Business Logic
================================================================================

This module contains all Trading-related routes and functionality including:
- Product Management
- Order Processing
- Warehouse Management
- Logistics Tracking

Author: Bareera International
Last Updated: October 3, 2025
================================================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
import os
from functools import wraps
from datetime import datetime

# Create Trading Blueprint
trading_bp = Blueprint('trading', __name__, template_folder='../../templates/trading', url_prefix='/trading')

# =============================================================================
# DATA FILE PATHS
# =============================================================================
# Get the project root directory (where app_new.py is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'trading')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
WAREHOUSE_FILE = os.path.join(DATA_DIR, 'warehouse.json')
LOGISTICS_FILE = os.path.join(DATA_DIR, 'logistics.json')

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def read_json_file(filepath):
    """Read and return data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def write_json_file(filepath, data):
    """Write data to a JSON file with proper formatting."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# =============================================================================
# AUTHENTICATION & AUTHORIZATION DECORATORS
# =============================================================================
def login_required(f):
    """Decorator to ensure user is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to ensure user has one of the required roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('trading.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# ROUTES - TRADING DASHBOARD
# =============================================================================

@trading_bp.route('/')
def dashboard():
    """Trading Module Dashboard."""
    if not session.get('user_id'):
        flash('Please log in to access the Trading module.', 'warning')
        return redirect(url_for('login'))
    
    # Get basic stats for dashboard
    products = read_json_file(PRODUCTS_FILE)
    orders = read_json_file(ORDERS_FILE)
    warehouse_items = read_json_file(WAREHOUSE_FILE)
    logistics = read_json_file(LOGISTICS_FILE)
    
    # Calculate basic statistics
    total_products = len(products)
    total_orders = len(orders)
    low_stock_items = len([w for w in warehouse_items if w.get('quantity', 0) < w.get('min_stock', 10)])
    pending_orders = len([o for o in orders if o.get('status') == 'Pending'])
    
    return render_template('trading/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         low_stock_items=low_stock_items,
                         pending_orders=pending_orders)

# =============================================================================
# ROUTES - PRODUCT MANAGEMENT
# =============================================================================

@trading_bp.route('/products')
@login_required
def products_list():
    """List all products."""
    products = read_json_file(PRODUCTS_FILE)
    return render_template('trading/products_list.html', products=products)

@trading_bp.route('/products/add', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff', 'Sales Staff')
def product_add():
    """Add a new product."""
    if request.method == 'POST':
        products = read_json_file(PRODUCTS_FILE)
        
        new_product = {
            'product_id': max([p.get('product_id', 0) for p in products], default=0) + 1,
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'price': float(request.form.get('price', 0)),
            'cost': float(request.form.get('cost', 0)),
            'sku': request.form.get('sku'),
            'barcode': request.form.get('barcode', ''),
            'status': 'Active',
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        products.append(new_product)
        write_json_file(PRODUCTS_FILE, products)
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('trading.products_list'))
    
    return render_template('trading/product_form.html', product=None)

@trading_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff', 'Sales Staff')
def product_edit(product_id):
    """Edit a product."""
    products = read_json_file(PRODUCTS_FILE)
    product = next((p for p in products if p['product_id'] == product_id), None)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('trading.products_list'))
    
    if request.method == 'POST':
        product['name'] = request.form.get('name')
        product['description'] = request.form.get('description')
        product['category'] = request.form.get('category')
        product['price'] = float(request.form.get('price', 0))
        product['cost'] = float(request.form.get('cost', 0))
        product['sku'] = request.form.get('sku')
        product['barcode'] = request.form.get('barcode', '')
        product['status'] = request.form.get('status', 'Active')
        
        write_json_file(PRODUCTS_FILE, products)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('trading.products_list'))
    
    return render_template('trading/product_form.html', product=product)

@trading_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@role_required('Admin')
def product_delete(product_id):
    """Delete a product."""
    products = read_json_file(PRODUCTS_FILE)
    product = next((p for p in products if p['product_id'] == product_id), None)
    
    if product:
        products = [p for p in products if p['product_id'] != product_id]
        write_json_file(PRODUCTS_FILE, products)
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found.', 'danger')
    
    return redirect(url_for('trading.products_list'))

# =============================================================================
# ROUTES - ORDER MANAGEMENT
# =============================================================================

@trading_bp.route('/orders')
@login_required
def orders_list():
    """List all orders."""
    orders = read_json_file(ORDERS_FILE)
    products = read_json_file(PRODUCTS_FILE)
    
    # Add product names to orders
    product_lookup = {p.get('product_id'): p for p in products if p.get('product_id')}
    for order in orders:
        product = product_lookup.get(order.get('product_id'))
        order['product_name'] = product.get('name') if product else 'Unknown'
    
    return render_template('trading/orders_list.html', orders=orders)

@trading_bp.route('/orders/add', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff', 'Sales Staff')
def order_add():
    """Add a new order."""
    if request.method == 'POST':
        orders = read_json_file(ORDERS_FILE)
        
        new_order = {
            'order_id': max([o.get('order_id', 0) for o in orders], default=0) + 1,
            'customer_name': request.form.get('customer_name'),
            'customer_email': request.form.get('customer_email'),
            'customer_phone': request.form.get('customer_phone'),
            'product_id': int(request.form.get('product_id')),
            'quantity': int(request.form.get('quantity', 1)),
            'unit_price': float(request.form.get('unit_price', 0)),
            'total_amount': float(request.form.get('quantity', 1)) * float(request.form.get('unit_price', 0)),
            'order_date': request.form.get('order_date'),
            'delivery_date': request.form.get('delivery_date'),
            'status': 'Pending',
            'notes': request.form.get('notes', ''),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        orders.append(new_order)
        write_json_file(ORDERS_FILE, orders)
        
        flash('Order added successfully!', 'success')
        return redirect(url_for('trading.orders_list'))
    
    products = read_json_file(PRODUCTS_FILE)
    return render_template('trading/order_form.html', order=None, products=products)

@trading_bp.route('/orders/edit/<int:order_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff')
def order_edit(order_id):
    """Edit an order."""
    orders = read_json_file(ORDERS_FILE)
    order = next((o for o in orders if o.get('order_id') == order_id), None)
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('trading.orders_list'))
    
    if request.method == 'POST':
        order['customer_name'] = request.form.get('customer_name')
        order['customer_email'] = request.form.get('customer_email')
        order['product_id'] = int(request.form.get('product_id'))
        order['quantity'] = int(request.form.get('quantity'))
        order['total_amount'] = float(request.form.get('total_amount', 0))
        order['status'] = request.form.get('status', 'Pending')
        order['shipping_address'] = request.form.get('shipping_address')
        order['notes'] = request.form.get('notes', '')
        
        write_json_file(ORDERS_FILE, orders)
        flash('Order updated successfully!', 'success')
        return redirect(url_for('trading.orders_list'))
    
    products = read_json_file(PRODUCTS_FILE)
    return render_template('trading/order_form.html', order=order, products=products)

@trading_bp.route('/orders/delete/<int:order_id>', methods=['POST'])
@role_required('Admin', 'Trading Staff')
def order_delete(order_id):
    """Delete an order."""
    orders = read_json_file(ORDERS_FILE)
    order = next((o for o in orders if o.get('order_id') == order_id), None)
    
    if order:
        orders = [o for o in orders if o.get('order_id') != order_id]
        write_json_file(ORDERS_FILE, orders)
        flash('Order deleted successfully!', 'success')
    else:
        flash('Order not found.', 'danger')
    
    return redirect(url_for('trading.orders_list'))

@trading_bp.route('/orders/update-status/<int:order_id>', methods=['POST'])
@role_required('Admin', 'Trading Staff', 'Sales Staff')
def order_update_status(order_id):
    """Update order status."""
    orders = read_json_file(ORDERS_FILE)
    order = next((o for o in orders if o['order_id'] == order_id), None)
    
    if order:
        order['status'] = request.form.get('status')
        order['updated_by'] = session.get('user_id')
        order['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        write_json_file(ORDERS_FILE, orders)
        flash('Order status updated successfully!', 'success')
    else:
        flash('Order not found.', 'danger')
    
    return redirect(url_for('trading.orders_list'))

# =============================================================================
# ROUTES - WAREHOUSE MANAGEMENT
# =============================================================================

@trading_bp.route('/warehouse')
@login_required
def warehouse_list():
    """List warehouse inventory."""
    warehouse_items = read_json_file(WAREHOUSE_FILE)
    products = read_json_file(PRODUCTS_FILE)
    
    # Add product names to warehouse items
    product_lookup = {p.get('product_id'): p for p in products if p.get('product_id')}
    for item in warehouse_items:
        product = product_lookup.get(item.get('product_id'))
        item['product_name'] = product.get('name') if product else 'Unknown'
    
    return render_template('trading/warehouse_list.html', warehouse_items=warehouse_items)

@trading_bp.route('/warehouse/add', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff')
def warehouse_add():
    """Add warehouse inventory item."""
    if request.method == 'POST':
        warehouse_items = read_json_file(WAREHOUSE_FILE)
        
        new_item = {
            'item_id': max([i.get('item_id', 0) for i in warehouse_items], default=0) + 1,
            'product_id': int(request.form.get('product_id')),
            'quantity': int(request.form.get('quantity', 0)),
            'min_stock': int(request.form.get('min_stock', 10)),
            'max_stock': int(request.form.get('max_stock', 100)),
            'location': request.form.get('location'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_by': session.get('user_id')
        }
        
        warehouse_items.append(new_item)
        write_json_file(WAREHOUSE_FILE, warehouse_items)
        
        flash('Warehouse item added successfully!', 'success')
        return redirect(url_for('trading.warehouse_list'))
    
    products = read_json_file(PRODUCTS_FILE)
    return render_template('trading/warehouse_form.html', item=None, products=products)

@trading_bp.route('/warehouse/edit/<int:item_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff')
def warehouse_edit(item_id):
    """Edit warehouse inventory item."""
    warehouse_items = read_json_file(WAREHOUSE_FILE)
    item = next((i for i in warehouse_items if i.get('item_id') == item_id), None)
    
    if not item:
        flash('Warehouse item not found.', 'danger')
        return redirect(url_for('trading.warehouse_list'))
    
    if request.method == 'POST':
        item['product_id'] = int(request.form.get('product_id'))
        item['quantity'] = int(request.form.get('quantity', 0))
        item['min_stock'] = int(request.form.get('min_stock', 10))
        item['max_stock'] = int(request.form.get('max_stock', 100))
        item['location'] = request.form.get('location')
        item['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['updated_by'] = session.get('user_id')
        
        write_json_file(WAREHOUSE_FILE, warehouse_items)
        flash('Warehouse item updated successfully!', 'success')
        return redirect(url_for('trading.warehouse_list'))
    
    products = read_json_file(PRODUCTS_FILE)
    return render_template('trading/warehouse_form.html', item=item, products=products)

@trading_bp.route('/warehouse/delete/<int:item_id>', methods=['POST'])
@role_required('Admin', 'Trading Staff')
def warehouse_delete(item_id):
    """Delete warehouse inventory item."""
    warehouse_items = read_json_file(WAREHOUSE_FILE)
    item = next((i for i in warehouse_items if i.get('item_id') == item_id), None)
    
    if item:
        warehouse_items = [i for i in warehouse_items if i.get('item_id') != item_id]
        write_json_file(WAREHOUSE_FILE, warehouse_items)
        flash('Warehouse item deleted successfully!', 'success')
    else:
        flash('Warehouse item not found.', 'danger')
    
    return redirect(url_for('trading.warehouse_list'))

# =============================================================================
# ROUTES - LOGISTICS MANAGEMENT
# =============================================================================

@trading_bp.route('/logistics')
@login_required
def logistics_list():
    """List logistics tracking."""
    logistics = read_json_file(LOGISTICS_FILE)
    orders = read_json_file(ORDERS_FILE)
    
    # Add order info to logistics
    order_lookup = {o.get('order_id'): o for o in orders if o.get('order_id')}
    for log in logistics:
        order = order_lookup.get(log.get('order_id'))
        log['customer_name'] = order.get('customer_name') if order else 'Unknown'
    
    return render_template('trading/logistics_list.html', logistics=logistics)

@trading_bp.route('/logistics/add', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff')
def logistics_add():
    """Add logistics tracking."""
    if request.method == 'POST':
        logistics = read_json_file(LOGISTICS_FILE)
        
        new_logistics = {
            'logistics_id': max([l.get('logistics_id', 0) for l in logistics], default=0) + 1,
            'order_id': int(request.form.get('order_id')),
            'tracking_number': request.form.get('tracking_number'),
            'carrier': request.form.get('carrier'),
            'status': request.form.get('status', 'Processing'),
            'estimated_delivery': request.form.get('estimated_delivery'),
            'actual_delivery': request.form.get('actual_delivery', ''),
            'notes': request.form.get('notes', ''),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logistics.append(new_logistics)
        write_json_file(LOGISTICS_FILE, logistics)
        
        flash('Logistics tracking added successfully!', 'success')
        return redirect(url_for('trading.logistics_list'))
    
    orders = read_json_file(ORDERS_FILE)
    return render_template('trading/logistics_form.html', logistics=None, orders=orders)

@trading_bp.route('/logistics/edit/<int:logistics_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Trading Staff')
def logistics_edit(logistics_id):
    """Edit logistics tracking."""
    logistics = read_json_file(LOGISTICS_FILE)
    log = next((l for l in logistics if l.get('logistics_id') == logistics_id), None)
    
    if not log:
        flash('Logistics record not found.', 'danger')
        return redirect(url_for('trading.logistics_list'))
    
    if request.method == 'POST':
        log['order_id'] = int(request.form.get('order_id'))
        log['tracking_number'] = request.form.get('tracking_number')
        log['carrier'] = request.form.get('carrier')
        log['status'] = request.form.get('status', 'Processing')
        log['estimated_delivery'] = request.form.get('estimated_delivery')
        log['actual_delivery'] = request.form.get('actual_delivery', '')
        log['notes'] = request.form.get('notes', '')
        
        write_json_file(LOGISTICS_FILE, logistics)
        flash('Logistics tracking updated successfully!', 'success')
        return redirect(url_for('trading.logistics_list'))
    
    orders = read_json_file(ORDERS_FILE)
    return render_template('trading/logistics_form.html', logistics=log, orders=orders)

@trading_bp.route('/logistics/delete/<int:logistics_id>', methods=['POST'])
@role_required('Admin', 'Trading Staff')
def logistics_delete(logistics_id):
    """Delete logistics tracking."""
    logistics = read_json_file(LOGISTICS_FILE)
    log = next((l for l in logistics if l.get('logistics_id') == logistics_id), None)
    
    if log:
        logistics = [l for l in logistics if l.get('logistics_id') != logistics_id]
        write_json_file(LOGISTICS_FILE, logistics)
        flash('Logistics tracking deleted successfully!', 'success')
    else:
        flash('Logistics record not found.', 'danger')
    
    return redirect(url_for('trading.logistics_list'))
