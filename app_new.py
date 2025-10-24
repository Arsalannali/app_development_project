"""
================================================================================
BUSINESS MANAGEMENT SYSTEM - Main Application File
================================================================================

This is the main Flask application for the Business Management System.
It integrates multiple modules:
- HR Module (Employee Management, Payroll, Attendance, Leaves, Recruitment)
- Finance Module (General Ledger, Budgets, Accounts Payable/Receivable)
- CRM Module (Customer Management, Sales, Support Tickets, Feedback)
- Trading Module (Product Management, Orders, Warehouse, Logistics)

Author: Bareera International
Last Updated: October 3, 2025
================================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import bcrypt
import json
import os
from functools import wraps
from datetime import datetime

# Import module blueprints
from modules.hr.routes import hr_bp
from modules.finance.routes import finance_bp
from modules.crm.routes import crm_bp
from modules.trading.routes import trading_bp

# =============================================================================
# APPLICATION INITIALIZATION
# =============================================================================
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production!

# =============================================================================
# DATA FILE PATHS
# =============================================================================
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

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
                return redirect(url_for('main_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================
# Register all module blueprints
app.register_blueprint(hr_bp, url_prefix='/hr')
app.register_blueprint(finance_bp, url_prefix='/finance')
app.register_blueprint(crm_bp, url_prefix='/crm')
app.register_blueprint(trading_bp, url_prefix='/trading')

# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.route('/')
def main_dashboard():
    """Main dashboard for module navigation."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Global login page and authentication handler."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = read_json_file(USERS_FILE)
        user = next((u for u in users if u['username'] == username), None)
        
        if user and user['active'] and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['employee_id'] = user.get('employee_id')
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('main_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Global logout handler."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html')
        
        # Check minimum length
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('change_password.html')
        
        # Get current user
        users = read_json_file(USERS_FILE)
        user = next((u for u in users if u['user_id'] == session.get('user_id')), None)
        
        if user and bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Update password
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user['password_hash'] = hashed
            write_json_file(USERS_FILE, users)
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('main_dashboard'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('change_password.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        users = read_json_file(USERS_FILE)
        user = next((u for u in users if u['username'] == username), None)
        
        if user:
            # For now, just show a simple message
            # In a real application, you would send an email
            flash('Password reset instructions would be sent to your email.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Username not found.', 'danger')
    
    return render_template('forgot_password.html')

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Run Flask development server
    app.run(debug=True, port=5003, host='0.0.0.0', use_reloader=False)
