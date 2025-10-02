"""
================================================================================
HR MANAGEMENT SYSTEM - Main Application File
================================================================================

This is the main Flask application for the HR Management System.
It handles all routing, authentication, and business logic for:
- Employee Management
- Attendance Tracking
- Leave Management
- Payroll Processing
- Recruitment (Jobs & Applicants)
- User Authentication & Authorization

Author: Bareera International
Last Updated: October 3, 2025
================================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import bcrypt  # For password hashing and verification
import json  # For reading/writing JSON data files
import os  # For file path operations
from functools import wraps  # For creating decorators
from datetime import datetime  # For date/time operations
from werkzeug.utils import secure_filename  # For secure file uploads

# =============================================================================
# APPLICATION INITIALIZATION
# =============================================================================
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production!

# =============================================================================
# DATA FILE PATHS
# =============================================================================
# All data is stored in JSON files in the 'data' directory
DATA_DIR = 'data'
EMPLOYEES_FILE = os.path.join(DATA_DIR, 'employees.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
DEPARTMENTS_FILE = os.path.join(DATA_DIR, 'departments.json')
ATTENDANCE_FILE = os.path.join(DATA_DIR, 'attendance.json')
LEAVES_FILE = os.path.join(DATA_DIR, 'leaves.json')
PAYROLLS_FILE = os.path.join(DATA_DIR, 'payrolls.json')
JOBS_FILE = os.path.join(DATA_DIR, 'jobs.json')
APPLICANTS_FILE = os.path.join(DATA_DIR, 'applicants.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
FILES_DIR = os.path.join(DATA_DIR, 'files')

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # Allowed file types for resume uploads
MAX_FILE_SIZE = 16 * 1024 * 1024  # Maximum file size: 16MB

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
# JSON File Operations
# -----------------------------------------------------------------------------
def read_json_file(filepath):
    """
    Read and return data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        list/dict: Parsed JSON data, or empty list if file doesn't exist/invalid
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return empty list if file doesn't exist
    except json.JSONDecodeError:
        return []  # Return empty list if JSON is invalid

def write_json_file(filepath, data):
    """
    Write data to a JSON file with proper formatting.
    
    Args:
        filepath (str): Path to the JSON file
        data (list/dict): Data to write to the file
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)  # indent=2 makes file human-readable

# File Upload Helpers
# -----------------------------------------------------------------------------
def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """
    Save an uploaded file with a unique timestamp prefix.
    
    Args:
        file: FileStorage object from form upload
        
    Returns:
        str: Saved filename, or None if file is invalid
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to prevent filename conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(FILES_DIR, filename)
        file.save(filepath)
        return filename
    return None

# =============================================================================
# AUTHENTICATION & AUTHORIZATION DECORATORS
# =============================================================================

def login_required(f):
    """
    Decorator to ensure user is logged in before accessing a route.
    
    Usage: @login_required
    
    If user is not logged in, redirects to login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """
    Decorator to ensure user has one of the required roles.
    
    Usage: @role_required('Admin', 'HR Staff')
    
    Args:
        *roles: Variable number of allowed roles
        
    If user doesn't have required role, redirects to home page.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# ROUTES - MAIN PAGES
# =============================================================================

@app.route('/')
def index():
    """
    Home page / Dashboard.
    
    Displays different dashboard based on user role:
    - Admin/HR Staff: Full management dashboard
    - Employee: Personal dashboard with their own data
    """
    return render_template('index.html')

# =============================================================================
# ROUTES - AUTHENTICATION
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page and authentication handler.
    
    GET: Display login form
    POST: Authenticate user credentials and create session
    
    Supports three user roles:
    - Admin: Full system access
    - HR Staff: HR management access
    - Employee: Personal data access only
    """
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
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# =============================================================================
# ROUTES - ATTENDANCE MANAGEMENT
# =============================================================================

@app.route('/attendance')
@login_required
def attendance_list():
    """List attendance records"""
    attendance_records = read_json_file(ATTENDANCE_FILE)
    employees = read_json_file(EMPLOYEES_FILE)
    
    # Filter records based on user role
    current_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if current_role == 'Employee':
        # Employees can only see their own attendance records
        attendance_records = [r for r in attendance_records if r['employee_id'] == current_employee_id]
    elif current_role not in ['Admin', 'HR Staff']:
        # If somehow a user has an invalid role, redirect them
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    # Create employee lookup dictionary
    employee_lookup = {emp['employee_id']: emp for emp in employees}
    
    # Add employee names to attendance records
    for record in attendance_records:
        emp = employee_lookup.get(record['employee_id'])
        record['employee_name'] = f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown"
    
    return render_template('attendance/list.html', attendance_records=attendance_records)

@app.route('/attendance/mark', methods=['GET', 'POST'])
@login_required
def attendance_mark():
    """Mark attendance (check-in/check-out)"""
    current_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if request.method == 'POST':
        employee_id = int(request.form.get('employee_id'))
        
        # Check if employee is trying to mark attendance for someone else
        if current_role == 'Employee' and employee_id != current_employee_id:
            flash('You can only mark your own attendance.', 'danger')
            return redirect(url_for('attendance_mark'))
        
        action = request.form.get('action')  # 'check_in' or 'check_out'
        notes = request.form.get('notes', '')
        
        attendance_records = read_json_file(ATTENDANCE_FILE)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Find today's record for this employee
        today_record = None
        for record in attendance_records:
            if record['employee_id'] == employee_id and record['date'] == today:
                today_record = record
                break
        
        if action == 'check_in':
            if today_record:
                flash('You have already checked in today!', 'warning')
            else:
                new_record = {
                    'attendance_id': max([r.get('attendance_id', 0) for r in attendance_records], default=0) + 1,
                    'employee_id': employee_id,
                    'date': today,
                    'check_in_time': datetime.now().strftime('%H:%M:%S'),
                    'check_out_time': None,
                    'notes': notes,
                    'status': 'Present'
                }
                attendance_records.append(new_record)
                write_json_file(ATTENDANCE_FILE, attendance_records)
                flash('Check-in recorded successfully!', 'success')
        else:  # check_out
            if not today_record:
                flash('Please check in first!', 'warning')
            elif today_record['check_out_time']:
                flash('You have already checked out today!', 'warning')
            else:
                today_record['check_out_time'] = datetime.now().strftime('%H:%M:%S')
                if notes:
                    today_record['notes'] = notes
                write_json_file(ATTENDANCE_FILE, attendance_records)
                flash('Check-out recorded successfully!', 'success')
        
        return redirect(url_for('attendance_mark'))
    
    employees = read_json_file(EMPLOYEES_FILE)
    
    # For employees, only show their own record
    if current_role == 'Employee':
        employees = [emp for emp in employees if emp['employee_id'] == current_employee_id]
    
    return render_template('attendance/mark.html', employees=employees)

@app.route('/attendance/reports')
@role_required('Admin', 'HR Staff')
def attendance_reports():
    """Generate attendance reports"""
    attendance_records = read_json_file(ATTENDANCE_FILE)
    employees = read_json_file(EMPLOYEES_FILE)
    
    # Filter by date range if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id')
    
    filtered_records = attendance_records
    
    if start_date:
        filtered_records = [r for r in filtered_records if r['date'] >= start_date]
    if end_date:
        filtered_records = [r for r in filtered_records if r['date'] <= end_date]
    if employee_id:
        filtered_records = [r for r in filtered_records if r['employee_id'] == int(employee_id)]
    
    # Add employee names
    employee_lookup = {emp['employee_id']: emp for emp in employees}
    for record in filtered_records:
        emp = employee_lookup.get(record['employee_id'])
        record['employee_name'] = f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown"
    
    return render_template('attendance/reports.html', 
                         attendance_records=filtered_records, 
                         employees=employees,
                         start_date=start_date,
                         end_date=end_date,
                         employee_id=employee_id)

@app.route('/attendance/edit/<int:attendance_id>', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def attendance_edit(attendance_id):
    """Edit an attendance record"""
    attendance_records = read_json_file(ATTENDANCE_FILE)
    attendance = next((a for a in attendance_records if a['attendance_id'] == attendance_id), None)
    
    if not attendance:
        flash('Attendance record not found.', 'danger')
        return redirect(url_for('attendance_list'))
    
    if request.method == 'POST':
        attendance['date'] = request.form.get('date')
        attendance['check_in_time'] = request.form.get('check_in_time')
        attendance['check_out_time'] = request.form.get('check_out_time') or None
        attendance['notes'] = request.form.get('notes', '')
        attendance['status'] = request.form.get('status', 'Present')
        
        write_json_file(ATTENDANCE_FILE, attendance_records)
        flash('Attendance record updated successfully!', 'success')
        return redirect(url_for('attendance_list'))
    
    employees = read_json_file(EMPLOYEES_FILE)
    return render_template('attendance/edit.html', attendance=attendance, employees=employees)

@app.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
@role_required('Admin', 'HR Staff')
def attendance_delete(attendance_id):
    """Delete an attendance record"""
    attendance_records = read_json_file(ATTENDANCE_FILE)
    attendance = next((a for a in attendance_records if a['attendance_id'] == attendance_id), None)
    
    if attendance:
        attendance_records = [a for a in attendance_records if a['attendance_id'] != attendance_id]
        write_json_file(ATTENDANCE_FILE, attendance_records)
        flash('Attendance record deleted successfully!', 'success')
    else:
        flash('Attendance record not found.', 'danger')
    
    return redirect(url_for('attendance_list'))

# =============================================================================
# ROUTES - LEAVE MANAGEMENT
# =============================================================================

@app.route('/leaves')
@login_required
def leaves_list():
    """List leave requests"""
    leaves = read_json_file(LEAVES_FILE)
    employees = read_json_file(EMPLOYEES_FILE)
    
    # Filter leaves based on user role
    current_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if current_role == 'Employee':
        # Employees can only see their own leave requests
        leaves = [l for l in leaves if l['employee_id'] == current_employee_id]
    elif current_role not in ['Admin', 'HR Staff']:
        # If somehow a user has an invalid role, redirect them
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    # Create employee lookup dictionary
    employee_lookup = {emp['employee_id']: emp for emp in employees}
    
    # Add employee names to leave records
    for leave in leaves:
        emp = employee_lookup.get(leave['employee_id'])
        leave['employee_name'] = f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown"
    
    return render_template('leaves/list.html', leaves=leaves)

@app.route('/leaves/apply', methods=['GET', 'POST'])
@login_required
def leave_apply():
    """Apply for leave"""
    current_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if request.method == 'POST':
        employee_id = int(request.form.get('employee_id'))
        
        # Check if employee is trying to apply for leave for someone else
        if current_role == 'Employee' and employee_id != current_employee_id:
            flash('You can only apply for your own leave.', 'danger')
            return redirect(url_for('leave_apply'))
        
        leave_type = request.form.get('leave_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')
        
        leaves = read_json_file(LEAVES_FILE)
        
        new_leave = {
            'leave_id': max([l.get('leave_id', 0) for l in leaves], default=0) + 1,
            'employee_id': employee_id,
            'leave_type': leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason,
            'status': 'Pending',
            'applied_date': datetime.now().strftime('%Y-%m-%d'),
            'approved_by': None,
            'approved_date': None,
            'comments': None
        }
        
        leaves.append(new_leave)
        write_json_file(LEAVES_FILE, leaves)
        
        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('leaves_list'))
    
    employees = read_json_file(EMPLOYEES_FILE)
    
    # For employees, only show their own record
    if current_role == 'Employee':
        employees = [emp for emp in employees if emp['employee_id'] == current_employee_id]
    
    return render_template('leaves/apply.html', employees=employees)

@app.route('/leaves/approve/<int:leave_id>', methods=['POST'])
@role_required('Admin', 'HR Staff')
def leave_approve(leave_id):
    """Approve a leave request"""
    leaves = read_json_file(LEAVES_FILE)
    leave = next((l for l in leaves if l['leave_id'] == leave_id), None)
    
    if leave:
        leave['status'] = 'Approved'
        leave['approved_by'] = session.get('user_id')
        leave['approved_date'] = datetime.now().strftime('%Y-%m-%d')
        leave['comments'] = request.form.get('comments', '')
        
        write_json_file(LEAVES_FILE, leaves)
        flash('Leave request approved successfully!', 'success')
    else:
        flash('Leave request not found.', 'danger')
    
    return redirect(url_for('leaves_list'))

@app.route('/leaves/reject/<int:leave_id>', methods=['POST'])
@role_required('Admin', 'HR Staff')
def leave_reject(leave_id):
    """Reject a leave request"""
    leaves = read_json_file(LEAVES_FILE)
    leave = next((l for l in leaves if l['leave_id'] == leave_id), None)
    
    if leave:
        leave['status'] = 'Rejected'
        leave['approved_by'] = session.get('user_id')
        leave['approved_date'] = datetime.now().strftime('%Y-%m-%d')
        leave['comments'] = request.form.get('comments', '')
        
        write_json_file(LEAVES_FILE, leaves)
        flash('Leave request rejected.', 'info')
    else:
        flash('Leave request not found.', 'danger')
    
    return redirect(url_for('leaves_list'))

@app.route('/leaves/edit/<int:leave_id>', methods=['GET', 'POST'])
@login_required
def leave_edit(leave_id):
    """Edit a leave request"""
    leaves = read_json_file(LEAVES_FILE)
    leave = next((l for l in leaves if l['leave_id'] == leave_id), None)
    
    if not leave:
        flash('Leave request not found.', 'danger')
        return redirect(url_for('leaves_list'))
    
    # Check if user can edit this leave (employee can only edit their own pending leaves, HR/Admin can edit any)
    current_user_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if current_user_role not in ['Admin', 'HR Staff'] and (leave['employee_id'] != current_employee_id or leave['status'] != 'Pending'):
        flash('You can only edit your own pending leave requests.', 'danger')
        return redirect(url_for('leaves_list'))
    
    if request.method == 'POST':
        # Only allow editing of pending leaves, or allow HR/Admin to edit any
        if leave['status'] == 'Pending' or current_user_role in ['Admin', 'HR Staff']:
            leave['leave_type'] = request.form.get('leave_type')
            leave['start_date'] = request.form.get('start_date')
            leave['end_date'] = request.form.get('end_date')
            leave['reason'] = request.form.get('reason')
            
            # Reset approval fields if leave is being modified
            if current_user_role not in ['Admin', 'HR Staff']:
                leave['approved_by'] = None
                leave['approved_date'] = None
                leave['comments'] = None
            
            write_json_file(LEAVES_FILE, leaves)
            flash('Leave request updated successfully!', 'success')
        else:
            flash('Cannot edit approved or rejected leave requests.', 'danger')
        
        return redirect(url_for('leaves_list'))
    
    employees = read_json_file(EMPLOYEES_FILE)
    return render_template('leaves/edit.html', leave=leave, employees=employees)

@app.route('/leaves/delete/<int:leave_id>', methods=['POST'])
@login_required
def leave_delete(leave_id):
    """Delete a leave request"""
    leaves = read_json_file(LEAVES_FILE)
    leave = next((l for l in leaves if l['leave_id'] == leave_id), None)
    
    if not leave:
        flash('Leave request not found.', 'danger')
        return redirect(url_for('leaves_list'))
    
    # Check permissions
    current_user_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    # Employees can only delete their own pending leaves, HR/Admin can delete any
    if current_user_role not in ['Admin', 'HR Staff'] and (leave['employee_id'] != current_employee_id or leave['status'] != 'Pending'):
        flash('You can only delete your own pending leave requests.', 'danger')
        return redirect(url_for('leaves_list'))
    
    leaves = [l for l in leaves if l['leave_id'] != leave_id]
    write_json_file(LEAVES_FILE, leaves)
    flash('Leave request deleted successfully!', 'success')
    
    return redirect(url_for('leaves_list'))

# =============================================================================
# ROUTES - EMPLOYEE MANAGEMENT
# =============================================================================

@app.route('/employees')
@role_required('Admin', 'HR Staff')
def employees_list():
    """List all employees"""
    employees = read_json_file(EMPLOYEES_FILE)
    return render_template('employees/list.html', employees=employees)

@app.route('/employees/add', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def employee_add():
    """Add a new employee"""
    if request.method == 'POST':
        employees = read_json_file(EMPLOYEES_FILE)
        departments = read_json_file(DEPARTMENTS_FILE)
        
        # Generate new employee ID
        new_id = max([e['employee_id'] for e in employees], default=0) + 1
        
        new_employee = {
            'employee_id': new_id,
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'cnic': request.form.get('cnic'),
            'email': request.form.get('email'),
            'contact': request.form.get('contact'),
            'department': request.form.get('department'),
            'designation': request.form.get('designation'),
            'join_date': request.form.get('join_date'),
            'status': request.form.get('status', 'Active'),
            'salary': float(request.form.get('salary', 0))
        }
        
        employees.append(new_employee)
        write_json_file(EMPLOYEES_FILE, employees)
        
        flash(f'Employee {new_employee["first_name"]} {new_employee["last_name"]} added successfully!', 'success')
        return redirect(url_for('employees_list'))
    
    departments = read_json_file(DEPARTMENTS_FILE)
    return render_template('employees/form.html', employee=None, departments=departments)

@app.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def employee_edit(employee_id):
    """Edit an existing employee"""
    employees = read_json_file(EMPLOYEES_FILE)
    employee = next((e for e in employees if e['employee_id'] == employee_id), None)
    
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees_list'))
    
    if request.method == 'POST':
        employee['first_name'] = request.form.get('first_name')
        employee['last_name'] = request.form.get('last_name')
        employee['cnic'] = request.form.get('cnic')
        employee['email'] = request.form.get('email')
        employee['contact'] = request.form.get('contact')
        employee['department'] = request.form.get('department')
        employee['designation'] = request.form.get('designation')
        employee['join_date'] = request.form.get('join_date')
        employee['status'] = request.form.get('status')
        employee['salary'] = float(request.form.get('salary', 0))
        
        write_json_file(EMPLOYEES_FILE, employees)
        
        flash(f'Employee {employee["first_name"]} {employee["last_name"]} updated successfully!', 'success')
        return redirect(url_for('employees_list'))
    
    departments = read_json_file(DEPARTMENTS_FILE)
    return render_template('employees/form.html', employee=employee, departments=departments)

@app.route('/employees/delete/<int:employee_id>', methods=['POST'])
@role_required('Admin', 'HR Staff')
def employee_delete(employee_id):
    """Delete an employee"""
    employees = read_json_file(EMPLOYEES_FILE)
    employee = next((e for e in employees if e['employee_id'] == employee_id), None)
    
    if employee:
        employees = [e for e in employees if e['employee_id'] != employee_id]
        write_json_file(EMPLOYEES_FILE, employees)
        flash(f'Employee {employee["first_name"]} {employee["last_name"]} deleted successfully!', 'success')
    else:
        flash('Employee not found.', 'danger')
    
    return redirect(url_for('employees_list'))

@app.route('/employees/view/<int:employee_id>')
@login_required
def employee_view(employee_id):
    """View employee details"""
    employees = read_json_file(EMPLOYEES_FILE)
    employee = next((e for e in employees if e['employee_id'] == employee_id), None)
    
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees_list'))
    
    return render_template('employees/view.html', employee=employee)

# =============================================================================
# ROUTES - PAYROLL MANAGEMENT
# =============================================================================

@app.route('/payroll')
@role_required('Admin', 'HR Staff')
def payroll_list():
    """List all payroll records"""
    payrolls = read_json_file(PAYROLLS_FILE)
    employees = read_json_file(EMPLOYEES_FILE)
    
    # Create employee lookup dictionary
    employee_lookup = {emp['employee_id']: emp for emp in employees}
    
    # Add employee names to payroll records
    for payroll in payrolls:
        emp = employee_lookup.get(payroll['employee_id'])
        payroll['employee_name'] = f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown"
    
    return render_template('payroll/list.html', payrolls=payrolls)

@app.route('/payroll/generate', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def payroll_generate():
    """Generate payroll for a specific month/year"""
    if request.method == 'POST':
        month = request.form.get('month')
        year = int(request.form.get('year'))
        employee_id = request.form.get('employee_id')
        
        employees = read_json_file(EMPLOYEES_FILE)
        payrolls = read_json_file(PAYROLLS_FILE)
        
        # Filter employees if specific employee selected, otherwise generate for all active employees
        if employee_id:
            employees_to_process = [e for e in employees if e['employee_id'] == int(employee_id) and e['status'] == 'Active']
        else:
            employees_to_process = [e for e in employees if e['status'] == 'Active']
        
        generated_count = 0
        for employee in employees_to_process:
            # Check if payroll already exists for this employee, month, and year
            existing = next((p for p in payrolls if p['employee_id'] == employee['employee_id'] 
                           and p['month'] == month and p['year'] == year), None)
            
            if existing:
                continue  # Skip if already generated
            
            # Get salary and calculate payroll
            basic_salary = employee.get('salary', 0)
            allowances = float(request.form.get('allowances', 0))
            deductions = float(request.form.get('deductions', 0))
            net_salary = basic_salary + allowances - deductions
            
            new_payroll = {
                'payroll_id': max([p.get('payroll_id', 0) for p in payrolls], default=0) + 1,
                'employee_id': employee['employee_id'],
                'month': month,
                'year': year,
                'basic_salary': basic_salary,
                'allowances': allowances,
                'deductions': deductions,
                'net_salary': net_salary,
                'payment_date': request.form.get('payment_date'),
                'status': request.form.get('status', 'Pending'),
                'generated_by': session.get('user_id'),
                'generated_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            payrolls.append(new_payroll)
            generated_count += 1
        
        write_json_file(PAYROLLS_FILE, payrolls)
        
        if generated_count > 0:
            flash(f'Payroll generated successfully for {generated_count} employee(s)!', 'success')
        else:
            flash('No new payroll records generated. Records may already exist for this period.', 'warning')
        
        return redirect(url_for('payroll_list'))
    
    employees = read_json_file(EMPLOYEES_FILE)
    active_employees = [e for e in employees if e['status'] == 'Active']
    return render_template('payroll/generate.html', employees=active_employees)

@app.route('/payroll/view/<int:payroll_id>')
@login_required
def payroll_view(payroll_id):
    """View salary slip for a specific payroll entry"""
    payrolls = read_json_file(PAYROLLS_FILE)
    payroll = next((p for p in payrolls if p['payroll_id'] == payroll_id), None)
    
    if not payroll:
        flash('Payroll record not found.', 'danger')
        return redirect(url_for('index'))
    
    # Check permissions - employees can only view their own payroll
    current_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if current_role not in ['Admin', 'HR Staff'] and payroll['employee_id'] != current_employee_id:
        flash('You can only view your own payroll records.', 'danger')
        return redirect(url_for('index'))
    
    # Get employee details
    employees = read_json_file(EMPLOYEES_FILE)
    employee = next((e for e in employees if e['employee_id'] == payroll['employee_id']), None)
    
    return render_template('payroll/slip.html', payroll=payroll, employee=employee)

@app.route('/my-payroll')
@login_required
def my_payroll():
    """View own payroll records (for employees)"""
    current_role = session.get('role')
    current_employee_id = session.get('employee_id')
    
    if current_role != 'Employee':
        flash('This page is for employees only.', 'danger')
        return redirect(url_for('index'))
    
    payrolls = read_json_file(PAYROLLS_FILE)
    employees = read_json_file(EMPLOYEES_FILE)
    
    # Filter to only show employee's own payroll records
    employee_payrolls = [p for p in payrolls if p['employee_id'] == current_employee_id]
    
    # Create employee lookup dictionary
    employee_lookup = {emp['employee_id']: emp for emp in employees}
    
    # Add employee names to payroll records
    for payroll in employee_payrolls:
        emp = employee_lookup.get(payroll['employee_id'])
        payroll['employee_name'] = f"{emp['first_name']} {emp['last_name']}" if emp else "Unknown"
    
    return render_template('payroll/list.html', payrolls=employee_payrolls)

@app.route('/payroll/delete/<int:payroll_id>', methods=['POST'])
@role_required('Admin')
def payroll_delete(payroll_id):
    """Delete a payroll record (Admin only)"""
    payrolls = read_json_file(PAYROLLS_FILE)
    payroll = next((p for p in payrolls if p['payroll_id'] == payroll_id), None)
    
    if payroll:
        payrolls = [p for p in payrolls if p['payroll_id'] != payroll_id]
        write_json_file(PAYROLLS_FILE, payrolls)
        flash('Payroll record deleted successfully!', 'success')
    else:
        flash('Payroll record not found.', 'danger')
    
    return redirect(url_for('payroll_list'))

# =============================================================================
# ROUTES - RECRUITMENT (JOBS & APPLICANTS)
# =============================================================================

@app.route('/jobs')
@role_required('Admin', 'HR Staff')
def jobs_list():
    """List all job postings"""
    jobs = read_json_file(JOBS_FILE)
    departments = read_json_file(DEPARTMENTS_FILE)
    
    # Add department names to jobs (departments is a simple array of strings)
    for job in jobs:
        job['department_name'] = job.get('department', '')
    
    # Add applicant counts for HR Staff and Admin
    if session.get('role') in ['Admin', 'HR Staff']:
        applicants = read_json_file(APPLICANTS_FILE)
        for job in jobs:
            job['applicant_count'] = len([a for a in applicants if a['job_id'] == job['job_id']])
    
    return render_template('jobs/list.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def job_add():
    """Add a new job posting"""
    if request.method == 'POST':
        jobs = read_json_file(JOBS_FILE)
        
        new_job = {
            'job_id': max([j.get('job_id', 0) for j in jobs], default=0) + 1,
            'title': request.form.get('title'),
            'department': request.form.get('department'),
            'description': request.form.get('description'),
            'requirements': request.form.get('requirements'),
            'salary_range': request.form.get('salary_range'),
            'location': request.form.get('location'),
            'employment_type': request.form.get('employment_type'),
            'experience_level': request.form.get('experience_level'),
            'status': request.form.get('status', 'Active'),
            'posted_date': datetime.now().strftime('%Y-%m-%d'),
            'application_deadline': request.form.get('application_deadline'),
            'posted_by': session.get('user_id')
        }
        
        jobs.append(new_job)
        write_json_file(JOBS_FILE, jobs)
        
        flash(f'Job posting "{new_job["title"]}" added successfully!', 'success')
        return redirect(url_for('jobs_list'))
    
    departments = read_json_file(DEPARTMENTS_FILE)
    return render_template('jobs/form.html', job=None, departments=departments)

@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def job_edit(job_id):
    """Edit an existing job posting"""
    jobs = read_json_file(JOBS_FILE)
    job = next((j for j in jobs if j['job_id'] == job_id), None)
    
    if not job:
        flash('Job posting not found.', 'danger')
        return redirect(url_for('jobs_list'))
    
    if request.method == 'POST':
        job['title'] = request.form.get('title')
        job['department'] = request.form.get('department')
        job['description'] = request.form.get('description')
        job['requirements'] = request.form.get('requirements')
        job['salary_range'] = request.form.get('salary_range')
        job['location'] = request.form.get('location')
        job['employment_type'] = request.form.get('employment_type')
        job['experience_level'] = request.form.get('experience_level')
        job['status'] = request.form.get('status')
        job['application_deadline'] = request.form.get('application_deadline')
        
        write_json_file(JOBS_FILE, jobs)
        
        flash(f'Job posting "{job["title"]}" updated successfully!', 'success')
        return redirect(url_for('jobs_list'))
    
    departments = read_json_file(DEPARTMENTS_FILE)
    return render_template('jobs/form.html', job=job, departments=departments)

@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
@role_required('Admin', 'HR Staff')
def job_delete(job_id):
    """Delete a job posting"""
    jobs = read_json_file(JOBS_FILE)
    job = next((j for j in jobs if j['job_id'] == job_id), None)
    
    if job:
        jobs = [j for j in jobs if j['job_id'] != job_id]
        write_json_file(JOBS_FILE, jobs)
        flash(f'Job posting "{job["title"]}" deleted successfully!', 'success')
    else:
        flash('Job posting not found.', 'danger')
    
    return redirect(url_for('jobs_list'))

@app.route('/jobs/view/<int:job_id>')
def job_view(job_id):
    """View job details (public page for applicants)"""
    jobs = read_json_file(JOBS_FILE)
    job = next((j for j in jobs if j['job_id'] == job_id), None)
    
    if not job:
        flash('Job posting not found.', 'danger')
        return redirect(url_for('index'))
    
    # Get applicants for this job (only for HR Staff and Admin)
    applicants = []
    if session.get('role') in ['Admin', 'HR Staff']:
        all_applicants = read_json_file(APPLICANTS_FILE)
        applicants = [a for a in all_applicants if a['job_id'] == job_id]
    
    return render_template('jobs/view.html', job=job, applicants=applicants)

@app.route('/jobs/apply/<int:job_id>', methods=['GET', 'POST'])
def job_apply(job_id):
    """Apply for a job"""
    jobs = read_json_file(JOBS_FILE)
    job = next((j for j in jobs if j['job_id'] == job_id), None)
    
    if not job:
        flash('Job posting not found.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        applicants = read_json_file(APPLICANTS_FILE)
        
        # Handle file upload
        resume_file = request.files.get('resume')
        resume_filename = None
        if resume_file and resume_file.filename:
            resume_filename = save_uploaded_file(resume_file)
            if not resume_filename:
                flash('Invalid file type. Please upload PDF, DOC, or DOCX files only.', 'danger')
                return render_template('jobs/apply.html', job=job)
        
        new_applicant = {
            'applicant_id': max([a.get('applicant_id', 0) for a in applicants], default=0) + 1,
            'job_id': job_id,
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'contact': request.form.get('contact'),
            'cnic': request.form.get('cnic'),
            'experience_years': int(request.form.get('experience_years', 0)),
            'current_company': request.form.get('current_company', ''),
            'expected_salary': float(request.form.get('expected_salary', 0)),
            'cover_letter': request.form.get('cover_letter', ''),
            'resume_filename': resume_filename,
            'application_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'Applied',
            'reviewed_by': None,
            'review_date': None,
            'interview_date': None,
            'notes': None
        }
        
        applicants.append(new_applicant)
        write_json_file(APPLICANTS_FILE, applicants)
        
        flash('Your application has been submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('job_view', job_id=job_id))
    
    return render_template('jobs/apply.html', job=job)

# Applicant Management Routes

@app.route('/applicants')
@role_required('Admin', 'HR Staff')
def applicants_list():
    """List all applicants"""
    applicants = read_json_file(APPLICANTS_FILE)
    jobs = read_json_file(JOBS_FILE)
    
    # Filter by job_id if provided
    job_id = request.args.get('job_id')
    if job_id:
        applicants = [a for a in applicants if a['job_id'] == int(job_id)]
    
    # Add job titles to applicants
    job_lookup = {job['job_id']: job for job in jobs}
    for applicant in applicants:
        job = job_lookup.get(applicant['job_id'])
        applicant['job_title'] = job['title'] if job else 'Unknown'
    
    # Get current job info if filtering by job
    current_job = None
    if job_id:
        current_job = next((j for j in jobs if j['job_id'] == int(job_id)), None)
    
    return render_template('applicants/list.html', applicants=applicants, current_job=current_job)

@app.route('/applicants/view/<int:applicant_id>')
@role_required('Admin', 'HR Staff')
def applicant_view(applicant_id):
    """View applicant details"""
    applicants = read_json_file(APPLICANTS_FILE)
    applicant = next((a for a in applicants if a['applicant_id'] == applicant_id), None)
    
    if not applicant:
        flash('Applicant not found.', 'danger')
        return redirect(url_for('applicants_list'))
    
    jobs = read_json_file(JOBS_FILE)
    job = next((j for j in jobs if j['job_id'] == applicant['job_id']), None)
    
    return render_template('applicants/view.html', applicant=applicant, job=job)

@app.route('/applicants/update-status/<int:applicant_id>', methods=['POST'])
@role_required('Admin', 'HR Staff')
def applicant_update_status(applicant_id):
    """Update applicant status"""
    applicants = read_json_file(APPLICANTS_FILE)
    applicant = next((a for a in applicants if a['applicant_id'] == applicant_id), None)
    
    if applicant:
        applicant['status'] = request.form.get('status')
        applicant['reviewed_by'] = session.get('user_id')
        applicant['review_date'] = datetime.now().strftime('%Y-%m-%d')
        applicant['interview_date'] = request.form.get('interview_date') or None
        applicant['notes'] = request.form.get('notes', '')
        
        write_json_file(APPLICANTS_FILE, applicants)
        flash(f'Applicant status updated to {applicant["status"]}', 'success')
    else:
        flash('Applicant not found.', 'danger')
    
    return redirect(url_for('applicant_view', applicant_id=applicant_id))

@app.route('/applicants/onboard/<int:applicant_id>', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def applicant_onboard(applicant_id):
    """Onboard an applicant (convert to employee)"""
    applicants = read_json_file(APPLICANTS_FILE)
    applicant = next((a for a in applicants if a['applicant_id'] == applicant_id), None)
    
    if not applicant:
        flash('Applicant not found.', 'danger')
        return redirect(url_for('applicants_list'))
    
    if request.method == 'POST':
        employees = read_json_file(EMPLOYEES_FILE)
        
        # Create new employee from applicant data
        new_employee = {
            'employee_id': max([e['employee_id'] for e in employees], default=0) + 1,
            'first_name': applicant['first_name'],
            'last_name': applicant['last_name'],
            'cnic': applicant['cnic'],
            'email': applicant['email'],
            'contact': applicant['contact'],
            'department': request.form.get('department'),
            'designation': request.form.get('designation'),
            'join_date': request.form.get('join_date'),
            'status': 'Active',
            'salary': float(request.form.get('salary', 0))
        }
        
        employees.append(new_employee)
        write_json_file(EMPLOYEES_FILE, employees)
        
        # Update applicant status
        applicant['status'] = 'Hired'
        applicant['notes'] = f"Hired as {new_employee['designation']} in {new_employee['department']} department. Employee ID: {new_employee['employee_id']}"
        write_json_file(APPLICANTS_FILE, applicants)
        
        flash(f'Applicant {applicant["first_name"]} {applicant["last_name"]} has been successfully onboarded as Employee ID: {new_employee["employee_id"]}!', 'success')
        return redirect(url_for('applicants_list'))
    
    jobs = read_json_file(JOBS_FILE)
    job = next((j for j in jobs if j['job_id'] == applicant['job_id']), None)
    departments = read_json_file(DEPARTMENTS_FILE)
    
    return render_template('applicants/onboard.html', applicant=applicant, job=job, departments=departments)

@app.route('/applicants/download/<filename>')
@role_required('Admin', 'HR Staff')
def download_resume(filename):
    """Download applicant resume"""
    try:
        return send_from_directory(FILES_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        flash('Resume file not found.', 'danger')
        return redirect(url_for('applicants_list'))

@app.route('/applicants/delete/<int:applicant_id>', methods=['POST'])
@role_required('Admin')
def applicant_delete(applicant_id):
    """Delete an applicant (Admin only)"""
    applicants = read_json_file(APPLICANTS_FILE)
    applicant = next((a for a in applicants if a['applicant_id'] == applicant_id), None)
    
    if applicant:
        # Delete resume file if it exists
        if applicant.get('resume_filename'):
            try:
                os.remove(os.path.join(FILES_DIR, applicant['resume_filename']))
            except FileNotFoundError:
                pass  # File already deleted or doesn't exist
        
        applicants = [a for a in applicants if a['applicant_id'] != applicant_id]
        write_json_file(APPLICANTS_FILE, applicants)
        flash(f'Applicant {applicant["first_name"]} {applicant["last_name"]} deleted successfully!', 'success')
    else:
        flash('Applicant not found.', 'danger')
    
    return redirect(url_for('applicants_list'))

# =============================================================================
# ROUTES - SYSTEM SETTINGS
# =============================================================================

@app.route('/settings', methods=['GET', 'POST'])
@role_required('Admin', 'HR Staff')
def settings():
    """View and update system settings"""
    if request.method == 'POST':
        # Get current settings
        settings_data = read_json_file(SETTINGS_FILE)
        
        # Update company info
        settings_data['company_info']['company_name'] = request.form.get('company_name', '')
        settings_data['company_info']['company_email'] = request.form.get('company_email', '')
        settings_data['company_info']['company_phone'] = request.form.get('company_phone', '')
        settings_data['company_info']['company_address'] = request.form.get('company_address', '')
        
        # Update working hours
        settings_data['working_hours']['start_time'] = request.form.get('start_time', '09:00')
        settings_data['working_hours']['end_time'] = request.form.get('end_time', '18:00')
        settings_data['working_hours']['lunch_break_duration'] = int(request.form.get('lunch_break_duration', 60))
        
        # Update leave policies
        settings_data['leave_policies']['annual_leave_quota'] = int(request.form.get('annual_leave_quota', 15))
        settings_data['leave_policies']['sick_leave_quota'] = int(request.form.get('sick_leave_quota', 10))
        settings_data['leave_policies']['casual_leave_quota'] = int(request.form.get('casual_leave_quota', 5))
        settings_data['leave_policies']['carry_forward_allowed'] = request.form.get('carry_forward_allowed') == 'on'
        settings_data['leave_policies']['max_carry_forward_days'] = int(request.form.get('max_carry_forward_days', 5))
        
        # Update payroll settings
        settings_data['payroll_settings']['currency'] = request.form.get('currency', 'PKR')
        settings_data['payroll_settings']['pay_day'] = int(request.form.get('pay_day', 25))
        settings_data['payroll_settings']['tax_rate'] = float(request.form.get('tax_rate', 0.05))
        settings_data['payroll_settings']['provident_fund_rate'] = float(request.form.get('provident_fund_rate', 0.08))
        
        # Save settings
        write_json_file(SETTINGS_FILE, settings_data)
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    # GET request - display settings
    settings_data = read_json_file(SETTINGS_FILE)
    return render_template('settings.html', settings=settings_data)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        users = read_json_file(USERS_FILE)
        user = next((u for u in users if u['username'] == username), None)
        
        if user:
            # Find employee to get email
            employees = read_json_file(EMPLOYEES_FILE)
            employee = None
            if user.get('employee_id'):
                employee = next((e for e in employees if e['employee_id'] == user['employee_id']), None)
            
            # Verify email if employee exists
            if employee and employee.get('email') == email:
                # Generate temporary password
                import secrets
                temp_password = secrets.token_urlsafe(8)
                hashed = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update user password
                user['password_hash'] = hashed
                write_json_file(USERS_FILE, users)
                
                flash(f'Your password has been reset! Your temporary password is: {temp_password}. Please login and change it immediately.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username and email do not match our records.', 'danger')
        else:
            flash('Username not found.', 'danger')
    
    return render_template('forgot_password.html')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
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
            return redirect(url_for('index'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('change_password.html')

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Run Flask development server
    # - debug=True: Enable debug mode (shows detailed error pages)
    # - port=5002: Run on port 5002
    # - host='0.0.0.0': Make server accessible from network
    # - use_reloader=False: Disable auto-reload (prevents duplicate processes)
    app.run(debug=True, port=5002, host='0.0.0.0', use_reloader=False)

