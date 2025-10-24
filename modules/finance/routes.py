"""
================================================================================
FINANCE MODULE - Routes and Business Logic
================================================================================

This module contains all Finance-related routes and functionality including:
- General Ledger
- Accounts Payable/Receivable
- Budget Management
- Financial Reports

Author: Bareera International
Last Updated: October 3, 2025
================================================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json
import os
from functools import wraps
from datetime import datetime

# Create Finance Blueprint
finance_bp = Blueprint('finance', __name__, template_folder='../../templates/finance', url_prefix='/finance')

# =============================================================================
# DATA FILE PATHS
# =============================================================================
# Get the project root directory (where app_new.py is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'finance')
LEDGER_FILE = os.path.join(DATA_DIR, 'ledger.json')
BUDGETS_FILE = os.path.join(DATA_DIR, 'budgets.json')
PAYABLES_FILE = os.path.join(DATA_DIR, 'payables.json')
RECEIVABLES_FILE = os.path.join(DATA_DIR, 'receivables.json')

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
                return redirect(url_for('finance.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# ROUTES - FINANCE DASHBOARD
# =============================================================================

@finance_bp.route('/')
def dashboard():
    """Finance Module Dashboard."""
    if not session.get('user_id'):
        flash('Please log in to access the Finance module.', 'warning')
        return redirect(url_for('login'))
    
    # Get basic stats for dashboard
    ledger_entries = read_json_file(LEDGER_FILE)
    budgets = read_json_file(BUDGETS_FILE)
    payables = read_json_file(PAYABLES_FILE)
    receivables = read_json_file(RECEIVABLES_FILE)
    
    # Calculate basic statistics
    total_revenue = sum([entry.get('amount', 0) for entry in ledger_entries if entry.get('type') == 'Credit'])
    total_expenses = sum([entry.get('amount', 0) for entry in ledger_entries if entry.get('type') == 'Debit'])
    net_balance = total_revenue - total_expenses
    pending_payables = len([p for p in payables if p.get('status') == 'Pending'])
    
    return render_template('finance/dashboard.html', 
                         total_revenue=total_revenue,
                         total_expenses=total_expenses,
                         net_balance=net_balance,
                         pending_payables=pending_payables)

# =============================================================================
# ROUTES - GENERAL LEDGER
# =============================================================================

@finance_bp.route('/ledger')
@login_required
def ledger_list():
    """List all ledger entries."""
    ledger_entries = read_json_file(LEDGER_FILE)
    return render_template('finance/ledger_list.html', entries=ledger_entries)

@finance_bp.route('/ledger/add', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def ledger_add():
    """Add a new ledger entry."""
    if request.method == 'POST':
        entries = read_json_file(LEDGER_FILE)
        
        new_entry = {
            'entry_id': max([e.get('entry_id', 0) for e in entries], default=0) + 1,
            'date': request.form.get('date'),
            'type': request.form.get('type'),
            'amount': float(request.form.get('amount', 0)),
            'description': request.form.get('description'),
            'account': request.form.get('account'),
            'reference': request.form.get('reference', ''),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        entries.append(new_entry)
        write_json_file(LEDGER_FILE, entries)
        
        flash('Ledger entry added successfully!', 'success')
        return redirect(url_for('finance.ledger_list'))
    
    return render_template('finance/ledger_form.html', entry=None)

@finance_bp.route('/ledger/edit/<int:entry_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def ledger_edit(entry_id):
    """Edit a ledger entry."""
    entries = read_json_file(LEDGER_FILE)
    entry = next((e for e in entries if e['entry_id'] == entry_id), None)
    
    if not entry:
        flash('Ledger entry not found.', 'danger')
        return redirect(url_for('finance.ledger_list'))
    
    if request.method == 'POST':
        entry['date'] = request.form.get('date')
        entry['type'] = request.form.get('type')
        entry['amount'] = float(request.form.get('amount', 0))
        entry['description'] = request.form.get('description')
        entry['account'] = request.form.get('account')
        entry['reference'] = request.form.get('reference', '')
        
        write_json_file(LEDGER_FILE, entries)
        flash('Ledger entry updated successfully!', 'success')
        return redirect(url_for('finance.ledger_list'))
    
    return render_template('finance/ledger_form.html', entry=entry)

@finance_bp.route('/ledger/delete/<int:entry_id>', methods=['POST'])
@role_required('Admin')
def ledger_delete(entry_id):
    """Delete a ledger entry."""
    entries = read_json_file(LEDGER_FILE)
    entry = next((e for e in entries if e['entry_id'] == entry_id), None)
    
    if entry:
        entries = [e for e in entries if e['entry_id'] != entry_id]
        write_json_file(LEDGER_FILE, entries)
        flash('Ledger entry deleted successfully!', 'success')
    else:
        flash('Ledger entry not found.', 'danger')
    
    return redirect(url_for('finance.ledger_list'))

# =============================================================================
# ROUTES - BUDGET MANAGEMENT
# =============================================================================

@finance_bp.route('/budgets')
@login_required
def budgets_list():
    """List all budgets."""
    budgets = read_json_file(BUDGETS_FILE)
    return render_template('finance/budgets_list.html', budgets=budgets)

@finance_bp.route('/budgets/add', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def budget_add():
    """Add a new budget."""
    if request.method == 'POST':
        budgets = read_json_file(BUDGETS_FILE)
        
        new_budget = {
            'budget_id': max([b.get('budget_id', 0) for b in budgets], default=0) + 1,
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'amount': float(request.form.get('amount', 0)),
            'period': request.form.get('period'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'description': request.form.get('description', ''),
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        budgets.append(new_budget)
        write_json_file(BUDGETS_FILE, budgets)
        
        flash('Budget created successfully!', 'success')
        return redirect(url_for('finance.budgets_list'))
    
    return render_template('finance/budget_form.html', budget=None)

@finance_bp.route('/budgets/edit/<int:budget_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def budget_edit(budget_id):
    """Edit a budget."""
    budgets = read_json_file(BUDGETS_FILE)
    budget = next((b for b in budgets if b.get('budget_id') == budget_id), None)
    
    if not budget:
        flash('Budget not found.', 'danger')
        return redirect(url_for('finance.budgets_list'))
    
    if request.method == 'POST':
        budget['name'] = request.form.get('name')
        budget['category'] = request.form.get('category')
        budget['amount'] = float(request.form.get('amount', 0))
        budget['period'] = request.form.get('period')
        budget['start_date'] = request.form.get('start_date')
        budget['end_date'] = request.form.get('end_date')
        budget['description'] = request.form.get('description', '')
        
        write_json_file(BUDGETS_FILE, budgets)
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('finance.budgets_list'))
    
    return render_template('finance/budget_form.html', budget=budget)

@finance_bp.route('/budgets/delete/<int:budget_id>', methods=['POST'])
@role_required('Admin')
def budget_delete(budget_id):
    """Delete a budget."""
    budgets = read_json_file(BUDGETS_FILE)
    budget = next((b for b in budgets if b.get('budget_id') == budget_id), None)
    
    if budget:
        budgets = [b for b in budgets if b.get('budget_id') != budget_id]
        write_json_file(BUDGETS_FILE, budgets)
        flash('Budget deleted successfully!', 'success')
    else:
        flash('Budget not found.', 'danger')
    
    return redirect(url_for('finance.budgets_list'))

# =============================================================================
# ROUTES - ACCOUNTS PAYABLE
# =============================================================================

@finance_bp.route('/payables')
@login_required
def payables_list():
    """List all payables."""
    payables = read_json_file(PAYABLES_FILE)
    return render_template('finance/payables_list.html', payables=payables)

@finance_bp.route('/payables/add', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def payable_add():
    """Add a new payable."""
    if request.method == 'POST':
        payables = read_json_file(PAYABLES_FILE)
        
        new_payable = {
            'payable_id': max([p.get('payable_id', 0) for p in payables], default=0) + 1,
            'vendor': request.form.get('vendor'),
            'amount': float(request.form.get('amount', 0)),
            'due_date': request.form.get('due_date'),
            'description': request.form.get('description'),
            'status': 'Pending',
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        payables.append(new_payable)
        write_json_file(PAYABLES_FILE, payables)
        
        flash('Payable added successfully!', 'success')
        return redirect(url_for('finance.payables_list'))
    
    return render_template('finance/payable_form.html', payable=None)

@finance_bp.route('/payables/edit/<int:payable_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def payable_edit(payable_id):
    """Edit a payable."""
    payables = read_json_file(PAYABLES_FILE)
    payable = next((p for p in payables if p.get('payable_id') == payable_id), None)
    
    if not payable:
        flash('Payable not found.', 'danger')
        return redirect(url_for('finance.payables_list'))
    
    if request.method == 'POST':
        payable['vendor'] = request.form.get('vendor')
        payable['amount'] = float(request.form.get('amount', 0))
        payable['due_date'] = request.form.get('due_date')
        payable['description'] = request.form.get('description')
        payable['status'] = request.form.get('status', 'Pending')
        
        write_json_file(PAYABLES_FILE, payables)
        flash('Payable updated successfully!', 'success')
        return redirect(url_for('finance.payables_list'))
    
    return render_template('finance/payable_form.html', payable=payable)

@finance_bp.route('/payables/delete/<int:payable_id>', methods=['POST'])
@role_required('Admin')
def payable_delete(payable_id):
    """Delete a payable."""
    payables = read_json_file(PAYABLES_FILE)
    payable = next((p for p in payables if p.get('payable_id') == payable_id), None)
    
    if payable:
        payables = [p for p in payables if p.get('payable_id') != payable_id]
        write_json_file(PAYABLES_FILE, payables)
        flash('Payable deleted successfully!', 'success')
    else:
        flash('Payable not found.', 'danger')
    
    return redirect(url_for('finance.payables_list'))

# =============================================================================
# ROUTES - ACCOUNTS RECEIVABLE
# =============================================================================

@finance_bp.route('/receivables')
@login_required
def receivables_list():
    """List all receivables."""
    receivables = read_json_file(RECEIVABLES_FILE)
    return render_template('finance/receivables_list.html', receivables=receivables)

@finance_bp.route('/receivables/add', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def receivable_add():
    """Add a new receivable."""
    if request.method == 'POST':
        receivables = read_json_file(RECEIVABLES_FILE)
        
        new_receivable = {
            'receivable_id': max([r.get('receivable_id', 0) for r in receivables], default=0) + 1,
            'customer': request.form.get('customer'),
            'amount': float(request.form.get('amount', 0)),
            'due_date': request.form.get('due_date'),
            'description': request.form.get('description'),
            'status': 'Pending',
            'created_by': session.get('user_id'),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        receivables.append(new_receivable)
        write_json_file(RECEIVABLES_FILE, receivables)
        
        flash('Receivable added successfully!', 'success')
        return redirect(url_for('finance.receivables_list'))
    
    return render_template('finance/receivable_form.html', receivable=None)

@finance_bp.route('/receivables/edit/<int:receivable_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Finance Staff')
def receivable_edit(receivable_id):
    """Edit a receivable."""
    receivables = read_json_file(RECEIVABLES_FILE)
    receivable = next((r for r in receivables if r.get('receivable_id') == receivable_id), None)
    
    if not receivable:
        flash('Receivable not found.', 'danger')
        return redirect(url_for('finance.receivables_list'))
    
    if request.method == 'POST':
        receivable['customer'] = request.form.get('customer')
        receivable['amount'] = float(request.form.get('amount', 0))
        receivable['due_date'] = request.form.get('due_date')
        receivable['description'] = request.form.get('description')
        receivable['status'] = request.form.get('status', 'Pending')
        
        write_json_file(RECEIVABLES_FILE, receivables)
        flash('Receivable updated successfully!', 'success')
        return redirect(url_for('finance.receivables_list'))
    
    return render_template('finance/receivable_form.html', receivable=receivable)

@finance_bp.route('/receivables/delete/<int:receivable_id>', methods=['POST'])
@role_required('Admin')
def receivable_delete(receivable_id):
    """Delete a receivable."""
    receivables = read_json_file(RECEIVABLES_FILE)
    receivable = next((r for r in receivables if r.get('receivable_id') == receivable_id), None)
    
    if receivable:
        receivables = [r for r in receivables if r.get('receivable_id') != receivable_id]
        write_json_file(RECEIVABLES_FILE, receivables)
        flash('Receivable deleted successfully!', 'success')
    else:
        flash('Receivable not found.', 'danger')
    
    return redirect(url_for('finance.receivables_list'))
