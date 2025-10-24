"""
================================================================================
CRM MODULE - Routes and Business Logic
================================================================================

This module contains all CRM-related routes and functionality including:
- Customer Management
- Sales Pipeline
- Support Tickets
- Customer Feedback

Author: Bareera International
Last Updated: October 3, 2025
================================================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
import os
from functools import wraps
from datetime import datetime

# Create CRM Blueprint
crm_bp = Blueprint('crm', __name__, template_folder='../../templates/crm', url_prefix='/crm')

# =============================================================================
# DATA FILE PATHS
# =============================================================================
# Get the project root directory (where app_new.py is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'crm')
CUSTOMERS_FILE = os.path.join(DATA_DIR, 'customers.json')
SALES_FILE = os.path.join(DATA_DIR, 'sales.json')
TICKETS_FILE = os.path.join(DATA_DIR, 'tickets.json')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.json')

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
                return redirect(url_for('crm.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# ROUTES - CRM DASHBOARD
# =============================================================================

@crm_bp.route('/')
def dashboard():
    """CRM Module Dashboard."""
    if not session.get('user_id'):
        flash('Please log in to access the CRM module.', 'warning')
        return redirect(url_for('login'))
    
    # Get basic stats for dashboard
    customers = read_json_file(CUSTOMERS_FILE)
    sales = read_json_file(SALES_FILE)
    tickets = read_json_file(TICKETS_FILE)
    
    # Calculate basic statistics
    total_customers = len(customers)
    total_sales = len(sales)
    active_tickets = len([t for t in tickets if t.get('status') == 'Open'])
    total_revenue = sum([s.get('amount', 0) for s in sales if s.get('status') == 'Completed'])
    
    return render_template('crm/dashboard.html', 
                         total_customers=total_customers,
                         total_sales=total_sales,
                         active_tickets=active_tickets,
                         total_revenue=total_revenue)

# =============================================================================
# ROUTES - CUSTOMER MANAGEMENT
# =============================================================================

@crm_bp.route('/customers')
@login_required
def customers_list():
    """List all customers."""
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/customers_list.html', customers=customers)

@crm_bp.route('/customers/add', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff', 'Sales Staff')
def customer_add():
    """Add a new customer."""
    if request.method == 'POST':
        customers = read_json_file(CUSTOMERS_FILE)
        
        new_customer = {
            'id': max([c.get('id', 0) for c in customers], default=0) + 1,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'company': request.form.get('company', ''),
            'address': request.form.get('address', ''),
            'city': request.form.get('city', ''),
            'country': request.form.get('country', ''),
            'customer_type': request.form.get('customer_type', 'Individual'),
            'status': 'Active',
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        customers.append(new_customer)
        write_json_file(CUSTOMERS_FILE, customers)
        
        flash('Customer added successfully!', 'success')
        return redirect(url_for('crm.customers_list'))
    
    return render_template('crm/customer_form.html', customer=None)

@crm_bp.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff', 'Sales Staff')
def customer_edit(customer_id):
    """Edit a customer."""
    customers = read_json_file(CUSTOMERS_FILE)
    customer = next((c for c in customers if c['id'] == customer_id), None)
    
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('crm.customers_list'))
    
    if request.method == 'POST':
        customer['name'] = request.form.get('name')
        customer['email'] = request.form.get('email')
        customer['phone'] = request.form.get('phone')
        customer['company'] = request.form.get('company', '')
        customer['address'] = request.form.get('address', '')
        customer['city'] = request.form.get('city', '')
        customer['country'] = request.form.get('country', '')
        customer['customer_type'] = request.form.get('customer_type', 'Individual')
        customer['status'] = request.form.get('status', 'Active')
        
        write_json_file(CUSTOMERS_FILE, customers)
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('crm.customers_list'))
    
    return render_template('crm/customer_form.html', customer=customer)

@crm_bp.route('/customers/delete/<int:customer_id>', methods=['POST'])
@role_required('Admin')
def customer_delete(customer_id):
    """Delete a customer."""
    customers = read_json_file(CUSTOMERS_FILE)
    customer = next((c for c in customers if c['id'] == customer_id), None)
    
    if customer:
        customers = [c for c in customers if c['id'] != customer_id]
        write_json_file(CUSTOMERS_FILE, customers)
        flash('Customer deleted successfully!', 'success')
    else:
        flash('Customer not found.', 'danger')
    
    return redirect(url_for('crm.customers_list'))

# =============================================================================
# ROUTES - SALES MANAGEMENT
# =============================================================================

@crm_bp.route('/sales')
@login_required
def sales_list():
    """List all sales."""
    sales = read_json_file(SALES_FILE)
    customers = read_json_file(CUSTOMERS_FILE)
    
    # Add customer names to sales
    customer_lookup = {c['id']: c for c in customers}
    for sale in sales:
        customer = customer_lookup.get(sale.get('customer_id'))
        sale['customer_name'] = customer.get('name') if customer else 'Unknown'
    
    return render_template('crm/sales_list.html', sales=sales)

@crm_bp.route('/sales/add', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff', 'Sales Staff')
def sale_add():
    """Add a new sale."""
    if request.method == 'POST':
        sales = read_json_file(SALES_FILE)
        
        new_sale = {
            'id': max([s.get('id', 0) for s in sales], default=0) + 1,
            'customer_id': int(request.form.get('customer_id')),
            'product': request.form.get('product'),
            'amount': float(request.form.get('amount', 0)),
            'quantity': int(request.form.get('quantity', 1)),
            'sale_date': request.form.get('sale_date'),
            'status': request.form.get('status', 'Pending'),
            'notes': request.form.get('notes', ''),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        sales.append(new_sale)
        write_json_file(SALES_FILE, sales)
        
        flash('Sale added successfully!', 'success')
        return redirect(url_for('crm.sales_list'))
    
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/sale_form.html', sale=None, customers=customers)

@crm_bp.route('/sales/edit/<int:sale_id>', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff', 'Sales Staff')
def sale_edit(sale_id):
    """Edit a sale."""
    sales = read_json_file(SALES_FILE)
    sale = next((s for s in sales if s['id'] == sale_id), None)
    
    if not sale:
        flash('Sale not found.', 'danger')
        return redirect(url_for('crm.sales_list'))
    
    if request.method == 'POST':
        sale['customer_id'] = int(request.form.get('customer_id'))
        sale['product'] = request.form.get('product')
        sale['amount'] = float(request.form.get('amount', 0))
        sale['quantity'] = int(request.form.get('quantity', 1))
        sale['sale_date'] = request.form.get('sale_date')
        sale['status'] = request.form.get('status')
        sale['notes'] = request.form.get('notes', '')
        
        write_json_file(SALES_FILE, sales)
        flash('Sale updated successfully!', 'success')
        return redirect(url_for('crm.sales_list'))
    
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/sale_form.html', sale=sale, customers=customers)

@crm_bp.route('/sales/delete/<int:sale_id>', methods=['POST'])
@role_required('Admin', 'CRM Staff')
def sale_delete(sale_id):
    """Delete a sale."""
    sales = read_json_file(SALES_FILE)
    sales = [s for s in sales if s['id'] != sale_id]
    write_json_file(SALES_FILE, sales)
    
    flash('Sale deleted successfully!', 'success')
    return redirect(url_for('crm.sales_list'))

# =============================================================================
# ROUTES - SUPPORT TICKETS
# =============================================================================

@crm_bp.route('/tickets')
@login_required
def tickets_list():
    """List all support tickets."""
    tickets = read_json_file(TICKETS_FILE)
    customers = read_json_file(CUSTOMERS_FILE)
    
    # Add customer names to tickets
    customer_lookup = {c['id']: c for c in customers}
    for ticket in tickets:
        customer = customer_lookup.get(ticket.get('customer_id'))
        ticket['customer_name'] = customer.get('name') if customer else 'Unknown'
    
    return render_template('crm/tickets_list.html', tickets=tickets)

@crm_bp.route('/tickets/add', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff')
def ticket_add():
    """Add a new support ticket."""
    if request.method == 'POST':
        tickets = read_json_file(TICKETS_FILE)
        
        new_ticket = {
            'ticket_id': max([t.get('ticket_id', 0) for t in tickets], default=0) + 1,
            'customer_id': int(request.form.get('customer_id')),
            'subject': request.form.get('subject'),
            'description': request.form.get('description'),
            'priority': request.form.get('priority', 'Medium'),
            'status': 'Open',
            'assigned_to': request.form.get('assigned_to', ''),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        tickets.append(new_ticket)
        write_json_file(TICKETS_FILE, tickets)
        
        flash('Support ticket created successfully!', 'success')
        return redirect(url_for('crm.tickets_list'))
    
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/ticket_form.html', ticket=None, customers=customers)

@crm_bp.route('/tickets/update-status/<int:ticket_id>', methods=['POST'])
@role_required('Admin', 'CRM Staff')
def ticket_update_status(ticket_id):
    """Update ticket status."""
    tickets = read_json_file(TICKETS_FILE)
    ticket = next((t for t in tickets if t['ticket_id'] == ticket_id), None)
    
    if ticket:
        ticket['status'] = request.form.get('status')
        ticket['assigned_to'] = request.form.get('assigned_to', '')
        ticket['updated_by'] = session.get('user_id')
        ticket['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        write_json_file(TICKETS_FILE, tickets)
        flash('Ticket status updated successfully!', 'success')
    else:
        flash('Ticket not found.', 'danger')
    
    return redirect(url_for('crm.tickets_list'))

@crm_bp.route('/tickets/edit/<int:ticket_id>', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff')
def ticket_edit(ticket_id):
    """Edit a support ticket."""
    tickets = read_json_file(TICKETS_FILE)
    ticket = next((t for t in tickets if t.get('ticket_id') == ticket_id), None)
    
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('crm.tickets_list'))
    
    if request.method == 'POST':
        ticket['customer_id'] = int(request.form.get('customer_id'))
        ticket['subject'] = request.form.get('subject')
        ticket['description'] = request.form.get('description')
        ticket['priority'] = request.form.get('priority', 'Medium')
        ticket['status'] = request.form.get('status', 'Open')
        ticket['assigned_to'] = request.form.get('assigned_to', '')
        
        write_json_file(TICKETS_FILE, tickets)
        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('crm.tickets_list'))
    
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/ticket_form.html', ticket=ticket, customers=customers)

@crm_bp.route('/tickets/delete/<int:ticket_id>', methods=['POST'])
@role_required('Admin', 'CRM Staff')
def ticket_delete(ticket_id):
    """Delete a support ticket."""
    tickets = read_json_file(TICKETS_FILE)
    ticket = next((t for t in tickets if t.get('ticket_id') == ticket_id), None)
    
    if ticket:
        tickets = [t for t in tickets if t.get('ticket_id') != ticket_id]
        write_json_file(TICKETS_FILE, tickets)
        flash('Ticket deleted successfully!', 'success')
    else:
        flash('Ticket not found.', 'danger')
    
    return redirect(url_for('crm.tickets_list'))

# =============================================================================
# ROUTES - CUSTOMER FEEDBACK
# =============================================================================

@crm_bp.route('/feedback')
@login_required
def feedback_list():
    """List all customer feedback."""
    feedback = read_json_file(FEEDBACK_FILE)
    customers = read_json_file(CUSTOMERS_FILE)
    
    # Add customer names to feedback
    customer_lookup = {c['id']: c for c in customers}
    for fb in feedback:
        customer = customer_lookup.get(fb.get('customer_id'))
        fb['customer_name'] = customer.get('name') if customer else 'Unknown'
    
    return render_template('crm/feedback_list.html', feedback=feedback)

@crm_bp.route('/feedback/add', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff')
def feedback_add():
    """Add customer feedback."""
    if request.method == 'POST':
        feedback = read_json_file(FEEDBACK_FILE)
        
        new_feedback = {
            'feedback_id': max([f.get('feedback_id', 0) for f in feedback], default=0) + 1,
            'customer_id': int(request.form.get('customer_id')),
            'rating': int(request.form.get('rating')),
            'comment': request.form.get('comment'),
            'category': request.form.get('category'),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        feedback.append(new_feedback)
        write_json_file(FEEDBACK_FILE, feedback)
        
        flash('Feedback recorded successfully!', 'success')
        return redirect(url_for('crm.feedback_list'))
    
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/feedback_form.html', feedback=None, customers=customers)

@crm_bp.route('/feedback/edit/<int:feedback_id>', methods=['GET', 'POST'])
@role_required('Admin', 'CRM Staff')
def feedback_edit(feedback_id):
    """Edit customer feedback."""
    feedback = read_json_file(FEEDBACK_FILE)
    fb = next((f for f in feedback if f.get('feedback_id') == feedback_id), None)
    
    if not fb:
        flash('Feedback not found.', 'danger')
        return redirect(url_for('crm.feedback_list'))
    
    if request.method == 'POST':
        fb['customer_id'] = int(request.form.get('customer_id'))
        fb['rating'] = int(request.form.get('rating'))
        fb['comment'] = request.form.get('comment')
        fb['category'] = request.form.get('category')
        
        write_json_file(FEEDBACK_FILE, feedback)
        flash('Feedback updated successfully!', 'success')
        return redirect(url_for('crm.feedback_list'))
    
    customers = read_json_file(CUSTOMERS_FILE)
    return render_template('crm/feedback_form.html', feedback=fb, customers=customers)

@crm_bp.route('/feedback/delete/<int:feedback_id>', methods=['POST'])
@role_required('Admin', 'CRM Staff')
def feedback_delete(feedback_id):
    """Delete customer feedback."""
    feedback = read_json_file(FEEDBACK_FILE)
    fb = next((f for f in feedback if f.get('feedback_id') == feedback_id), None)
    
    if fb:
        feedback = [f for f in feedback if f.get('feedback_id') != feedback_id]
        write_json_file(FEEDBACK_FILE, feedback)
        flash('Feedback deleted successfully!', 'success')
    else:
        flash('Feedback not found.', 'danger')
    
    return redirect(url_for('crm.feedback_list'))
