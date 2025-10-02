# HR Management System - Project Structure

## 📁 Complete Directory Structure

```
app_development_proj/
│
├── app.py                          # Main Flask application (1,297 lines, fully commented)
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview and setup guide
│
├── data/                           # JSON data storage (database)
│   ├── employees.json              # 25 employee records
│   ├── users.json                  # 27 user accounts (2 admin/HR + 25 employees)
│   ├── departments.json            # 6 departments
│   ├── attendance.json             # 223 attendance records (last 10 days)
│   ├── leaves.json                 # 21 leave applications
│   ├── payrolls.json              # 67 payroll records (3 months)
│   ├── jobs.json                   # Job postings
│   ├── applicants.json            # Job applicants
│   ├── settings.json              # System settings
│   └── files/                      # Uploaded resumes and documents
│       ├── sample_resume_1.txt
│       └── sample_resume_2.txt
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base template (navigation, layout)
│   ├── index.html                  # Dashboard/home page
│   ├── login.html                  # Login page
│   ├── change_password.html        # Password change form
│   ├── forgot_password.html        # Password reset form
│   ├── settings.html               # System settings
│   │
│   ├── employees/                  # Employee management templates
│   │   ├── list.html               # List all employees
│   │   ├── form.html               # Add/edit employee form
│   │   └── view.html               # View employee details
│   │
│   ├── attendance/                 # Attendance tracking templates
│   │   ├── list.html               # List attendance records
│   │   ├── mark.html               # Mark attendance (check-in/out)
│   │   ├── edit.html               # Edit attendance record
│   │   └── reports.html            # Attendance reports
│   │
│   ├── leaves/                     # Leave management templates
│   │   ├── list.html               # List leave requests
│   │   ├── apply.html              # Apply for leave
│   │   └── edit.html               # Edit leave request
│   │
│   ├── payroll/                    # Payroll management templates
│   │   ├── list.html               # List payroll records
│   │   ├── generate.html           # Generate payroll
│   │   └── slip.html               # View salary slip
│   │
│   ├── jobs/                       # Recruitment templates
│   │   ├── list.html               # List job postings
│   │   ├── form.html               # Add/edit job posting
│   │   ├── view.html               # View job details
│   │   └── apply.html              # Job application form
│   │
│   └── applicants/                 # Applicant management templates
│       ├── list.html               # List applicants
│       ├── view.html               # View applicant details
│       └── onboard.html            # Onboard applicant as employee
│
├── venv/                           # Python virtual environment
│   ├── bin/                        # Executables (python, flask, pip)
│   ├── lib/                        # Installed packages
│   └── pyvenv.cfg                  # Virtual environment configuration
│
├── data_export.py                  # Backup utility (export data)
├── data_import.py                  # Restore utility (import data)
│
└── Documentation/
    ├── DEPLOYMENT_GUIDE.md         # Production deployment instructions
    ├── EMPLOYEE_LOGIN_GUIDE.md     # Employee login credentials & guide
    ├── SETTINGS_AND_SECURITY_FEATURES.md  # Security features documentation
    └── project_specs.md            # Original project specifications

```

---

## 🎯 File Descriptions

### Core Application Files

| File | Purpose | Lines | Fully Commented |
|------|---------|-------|-----------------|
| `app.py` | Main Flask application with all routes and business logic | 1,297 | ✅ Yes |
| `requirements.txt` | Python package dependencies | 4 | - |
| `README.md` | Project documentation and setup guide | 364 | - |

### Data Files (JSON Database)

All data is stored in JSON format for simplicity and portability:

| File | Contains | Current Records |
|------|----------|-----------------|
| `employees.json` | Employee master data | 25 employees |
| `users.json` | Login credentials (bcrypt hashed) | 27 users |
| `departments.json` | Department list | 6 departments |
| `attendance.json` | Attendance records | 223 records |
| `leaves.json` | Leave applications | 21 applications |
| `payrolls.json` | Salary records | 67 records |
| `jobs.json` | Job postings | Sample jobs |
| `applicants.json` | Job applicants | Sample applicants |
| `settings.json` | System configuration | Settings data |

### Utility Scripts

| Script | Purpose | Commented |
|--------|---------|-----------|
| `data_export.py` | Backup all data to timestamped folder or ZIP | ✅ Yes |
| `data_import.py` | Restore data from backup | ✅ Yes |

### Templates (Frontend)

27 Jinja2 HTML templates organized by feature:
- **Base**: Layout, navigation, common elements
- **Auth**: Login, password reset, change password
- **Employees**: CRUD operations for employees
- **Attendance**: Mark, view, edit attendance
- **Leaves**: Apply, approve, manage leaves
- **Payroll**: Generate, view salary slips
- **Recruitment**: Job postings and applicants
- **Settings**: System configuration

---

## 🔧 Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Authentication**: bcrypt for password hashing
- **Session Management**: Flask sessions
- **File Uploads**: Werkzeug secure filename handling

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JS for dynamic features

### Data Storage
- **Database**: JSON files (file-based)
- **File Storage**: Local filesystem for uploads

### Python Packages
```
Flask==3.0.0
bcrypt==5.0.0
passlib==1.7.4
werkzeug==3.0.0
```

---

## 📊 Code Statistics

### Main Application (`app.py`)
- **Total Lines**: 1,297
- **Import Section**: 58 lines
- **Helper Functions**: 70 lines
- **Authentication**: 42 lines
- **Routes**:
  - Main Pages: 12 lines
  - Authentication: 94 lines
  - Attendance: 177 lines
  - Leave Management: 185 lines
  - Employee Management**: 105 lines
  - Payroll: 142 lines
  - Recruitment: 314 lines
  - Settings: 82 lines

### Documentation
- **README.md**: 364 lines
- **DEPLOYMENT_GUIDE.md**: 794 lines
- **EMPLOYEE_LOGIN_GUIDE.md**: 155 lines
- **SETTINGS_AND_SECURITY_FEATURES.md**: 407 lines

### Templates
- **Total Templates**: 27 files
- **Average Size**: ~100-150 lines per template

---

## 🎨 Code Organization

### app.py Structure

```python
# 1. File Header & Imports (Lines 1-58)
   - Module docstring
   - Import statements
   - Application initialization

# 2. Configuration (Lines 59-57)
   - Data file paths
   - Upload configuration
   - Constants

# 3. Helper Functions (Lines 59-127)
   - JSON file operations
   - File upload handlers
   - Utility functions

# 4. Authentication Decorators (Lines 128-170)
   - @login_required
   - @role_required

# 5. Routes - Main Pages (Lines 171-186)
   - Home/Dashboard

# 6. Routes - Authentication (Lines 187-229)
   - Login, Logout
   - Password reset, Change password

# 7. Routes - Attendance (Lines 230-403)
   - List, Mark, Edit, Delete attendance
   - Reports

# 8. Routes - Leave Management (Lines 404-595)
   - Apply, View, Approve/Reject leaves
   - Edit, Delete

# 9. Routes - Employee Management (Lines 596-700)
   - List, Add, Edit, View, Delete employees

# 10. Routes - Payroll (Lines 701-853)
   - List, Generate, View payroll
   - My Payroll (for employees)

# 11. Routes - Recruitment (Lines 854-1167)
   - Jobs: List, Add, Edit, View, Delete
   - Applicants: List, View, Apply, Onboard, Delete

# 12. Routes - Settings (Lines 1168-1286)
   - System settings
   - Password management

# 13. Application Entry Point (Lines 1287-1297)
   - Run server configuration
```

---

## 🔐 Security Features

1. **Password Hashing**: bcrypt with salt
2. **Session Management**: Flask secure sessions
3. **Role-Based Access Control**: 3 user roles
4. **Input Validation**: Form validation on all inputs
5. **Secure File Uploads**: Filename sanitization, type checking
6. **CSRF Protection**: Built into Flask forms

---

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python app.py

# 4. Access application
http://localhost:5002
```

---

## 📦 Backup & Restore

### Create Backup
```bash
python data_export.py --zip
```

### Restore from Backup
```bash
python data_import.py /path/to/backup
```

### List Available Backups
```bash
python data_import.py --list
```

---

## 👥 User Roles & Access

### Admin (1 user)
- Username: `admin`
- Full system access
- Manage all modules

### HR Staff (1 user)
- Username: `hr_staff`
- HR management access
- Cannot modify system settings

### Employees (25 users)
- Username: `emp1` to `emp25`
- Personal data access only
- Cannot see other employees' data

**All passwords**: `arsi`

---

## 📈 Data Overview

### Current Test Data
- **Employees**: 25 (22 active, 3 inactive)
- **Departments**: HR, IT, Finance, Operations, Marketing, Sales
- **Attendance**: Last 10 days for all employees
- **Leaves**: 21 applications (Approved, Rejected, Pending)
- **Payroll**: 3 months (July, August, September 2025)

### Sample Employee Distribution
- **HR**: 5 employees
- **IT**: 1 employee
- **Finance**: 8 employees
- **Operations**: 5 employees
- **Marketing**: 3 employees
- **Sales**: 3 employees

---

## 🎯 Key Features

✅ Employee Management  
✅ Attendance Tracking (with calendar date picker)  
✅ Leave Management (apply, approve/reject)  
✅ Payroll Generation  
✅ Recruitment (jobs & applicants)  
✅ Role-Based Access Control  
✅ Data Export/Import  
✅ Password Management  
✅ System Settings  
✅ Real-time Data Updates  

---

**Last Updated**: October 3, 2025  
**Version**: 2.0  
**Status**: Production Ready ✨

