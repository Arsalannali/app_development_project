
## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Create Virtual Environment

```bash
cd app_development_proj
python3 -m venv venv
```

### Step 2: Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5001`

**Note:** We use port 5001 instead of 5000 because macOS uses port 5000 for AirPlay Receiver.

## Default User Accounts

The system comes with three pre-configured test accounts:

| Username   | Password | Role      | Description                                    |
|------------|----------|-----------|------------------------------------------------|
| `admin`    | `arsi`   | Admin     | Full access to all features                    |
| `hr_staff` | `arsi`   | HR Staff  | Can manage employees, attendance, and leaves   |
| `employee` | `arsi`   | Employee  | Limited access, can view own information       |

**⚠️ Important**: Change these passwords in production!

## Usage Guide

### Logging In
1. Open your browser and go to `http://localhost:5001`
2. Click "Login" in the navigation bar
3. Use one of the test accounts listed above
4. You'll be redirected to the home page

### Managing Employees

**Adding an Employee** (Admin/HR Staff only):
1. Click "Employees" in the navigation bar
2. Click "Add New Employee" button
3. Fill in all required fields:
   - First Name, Last Name
   - CNIC (format: xxxxx-xxxxxxx-x)
   - Email Address
   - Contact Number
   - Department (select from dropdown)
   - Designation
   - Join Date
   - Salary
   - Status
4. Click "Add Employee"

**Viewing Employees**:
- Click "Employees" in the navigation bar to see the full directory
- Click the eye icon (👁️) to view detailed employee information

**Editing an Employee** (Admin/HR Staff only):
- Click the pencil icon (✏️) next to an employee
- Update the information
- Click "Update Employee"

**Deleting an Employee** (Admin/HR Staff only):
- Click the trash icon (🗑️) next to an employee
- Confirm the deletion

## Data Storage

All data is stored as JSON files in the `data/` folder:

### Employee Data Format (`data/employees.json`)
```json
[
  {
    "employee_id": 1,
    "first_name": "Aisha",
    "last_name": "Khan",
    "cnic": "12345-1234567-1",
    "email": "aisha@example.com",
    "contact": "0300-1234567",
    "department": "HR",
    "designation": "HR Officer",
    "join_date": "2025-09-01",
    "status": "Active",
    "salary": 80000
  }
]
```

### User Data Format (`data/users.json`)
```json
[
  {
    "user_id": 1,
    "username": "admin",
    "password_hash": "$2b$12$...",
    "role": "Admin",
    "employee_id": null,
    "active": true
  }
]
```

## Role-Based Access Control

| Feature                | Admin | HR Staff | Employee |
|------------------------|-------|----------|----------|
| View Employees         | ✅    | ✅       | ✅       |
| Add Employee           | ✅    | ✅       | ❌       |
| Edit Employee          | ✅    | ✅       | ❌       |
| Delete Employee        | ✅    | ✅       | ❌       |
| View Own Profile       | ✅    | ✅       | ✅       |

## Complete Feature Set

The system now includes all planned features across 4 phases:

| Module | Features | Access Level |
|--------|----------|--------------|
| **Authentication** | Login/Logout, Session Management | All Users |
| **Employees** | CRUD operations, Employee directory | View: All, Manage: Admin/HR Staff |
| **Attendance** | Check-in/out, Reports, History | View: All, Mark: All, Manage: Admin/HR Staff |
| **Leaves** | Apply, Approve/Reject, Edit, Delete | Apply: All, Approve: Admin/HR Staff |
| **Payroll** | Generate, View salary slips | View Own: Employees, Manage: Admin/HR Staff |
| **Jobs** | Post jobs, Manage listings | View: All, Manage: Admin/HR Staff |
| **Applicants** | Apply, Track, Onboard | Apply: Public, Manage: Admin/HR Staff |

## Quick Navigation

Once logged in, you can access different modules from the navigation menu:

- **Home** - Dashboard overview
- **Employees** - Manage employee records
- **Attendance** - Mark attendance and view reports
- **Leaves** - Apply for leaves and manage requests
- **Payroll** - Generate and view salary slips
- **Jobs** - Manage job postings
- **Applicants** - Review and onboard candidates

## Troubleshooting

### Port Already in Use
If port 5001 is already in use, you can change it in `app.py`:
```python
app.run(debug=True, port=5002, host='127.0.0.1')  # Change to another port
```

### Module Not Found Error
Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Data File Not Found
The application automatically creates empty JSON files if they don't exist. If you encounter issues, ensure the `data/` directory exists and is writable.

## Development Notes

- **Debug Mode**: The application runs in debug mode by default. Disable this in production by setting `debug=False` in `app.py`.
- **Secret Key**: Change the `app.secret_key` in `app.py` for production use.
- **Passwords**: All default passwords should be changed before deployment.
- **Backup**: Regularly backup the `data/` folder as it contains all your records.

## Data Management

### Backup Your Data

All your HR data is stored in the `data/` folder as JSON files. To backup:

```bash
# Simple backup (copy the entire data folder)
cp -r data/ data_backup_$(date +%Y%m%d)/

# Or use the provided export script (coming in Phase 5 tools)
python data_export.py
```

### Data Files Structure

- `data/employees.json` - Employee records
- `data/departments.json` - Department list
- `data/users.json` - User accounts (hashed passwords)
- `data/attendance.json` - Attendance records
- `data/leaves.json` - Leave applications
- `data/payrolls.json` - Payroll records
- `data/jobs.json` - Job postings
- `data/applicants.json` - Job applicants
- `data/files/` - Uploaded files (resumes, documents)

### Export/Import Tools

Phase 5 includes utility scripts for data management:
- `data_export.py` - Export all JSON data to a timestamped backup
- `data_import.py` - Restore data from a backup
- See `MIGRATION_GUIDE.md` for database migration instructions

## Production Considerations

⚠️ **This is a prototype/development version. Before deploying to production:**

1. **Change Security Settings**:
   - Update `app.secret_key` in `app.py`
   - Change all default user passwords
   - Disable debug mode (`debug=False`)

2. **Use a Production Server**:
   - Don't use Flask's built-in server in production
   - Use Gunicorn, uWSGI, or similar WSGI server

3. **Migrate to a Database**:
   - JSON files are not suitable for production
   - Migrate to PostgreSQL, MySQL, or similar
   - See `MIGRATION_GUIDE.md` for details

4. **Add Security Features**:
   - Implement HTTPS
   - Add CSRF protection
   - Implement rate limiting
   - Add input validation and sanitization

5. **Setup Backups**:
   - Automate regular backups
   - Store backups off-site
   - Test restore procedures

## Support

For issues or questions, contact:
- **Developer**: Codecraft Studios Pakistan (CSP)
- **Project**: Bareera Intl. MIS Modernization - HR Module (Alpha Team)
- **Date**: October 2025

---

**Last Updated**: October 1, 2025  
**Version**: 2.0 (All Phases Complete - Phase 1-5)  
**Status**: Ready for Demo and Handoff

