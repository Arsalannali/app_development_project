# Employee Login Guide

## 🔐 User Account Structure

The HR Management System now has **27 total user accounts**:
- **2 Admin/HR accounts** (full access)
- **25 Employee accounts** (restricted access - own data only)

---

## 📝 Login Credentials

### Admin & HR Staff
| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `arsi` | Admin | Full system access |
| `hr_staff` | `arsi` | HR Staff | Full HR management access |

### Employees
All employees use the format: `emp[ID]` where ID is their employee number.

| Username | Password | Employee | Department |
|----------|----------|----------|------------|
| `emp1` | `arsi` | Ismail Hashmi | Finance |
| `emp2` | `arsi` | Ali Butt | Sales |
| `emp3` | `arsi` | Madiha Khan | Operations |
| `emp4` | `arsi` | Sara Khan | Marketing |
| `emp5` | `arsi` | Hina Mirza | HR |
| `emp6` | `arsi` | Zain Sheikh | Operations |
| `emp7` | `arsi` | Hamza Ali | HR |
| `emp8` | `arsi` | Hira Ahmed | HR |
| `emp9` | `arsi` | Zainab Rashid | IT |
| `emp10` | `arsi` | Kamran Butt | Finance |
| `emp11` | `arsi` | Ayesha Baig | Marketing |
| `emp12` | `arsi` | Bilal Malik | Operations |
| `emp13` | `arsi` | Ahmed Hussain | HR |
| `emp14` | `arsi` | Ali Malik | Finance |
| `emp15` | `arsi` | Hassan Butt | Finance |
| `emp16` | `arsi` | Faisal Hassan | Marketing |
| `emp17` | `arsi` | Hira Raza | Finance |
| `emp18` | `arsi` | Sara Iqbal | Finance |
| `emp19` | `arsi` | Zain Hassan | Sales |
| `emp20` | `arsi` | Rabia Ali | Operations |
| `emp21` | `arsi` | Adnan Ali | HR |
| `emp22` | `arsi` | Maryam Hassan | Finance |
| `emp23` | `arsi` | Bilal Hassan | Sales |
| `emp24` | `arsi` | Rabia Ali | Finance |
| `emp25` | `arsi` | Fatima Hussain | Operations |

---

## 🔒 Employee Access Restrictions

When employees log in, they can **ONLY** see and manage their own:
- ✅ **Attendance Records** - View and mark their own attendance
- ✅ **Leave Applications** - Apply for and view their own leaves
- ✅ **Payroll Information** - View their own salary slips
- ✅ **Personal Profile** - View their employment details

Employees **CANNOT**:
- ❌ View other employees' data
- ❌ Access admin/HR management features
- ❌ Approve/reject leaves
- ❌ Generate payroll for others
- ❌ Manage recruitment or system settings

---

## 🎯 How Employees Use the System

### 1. **Login**
- Go to: `http://localhost:5002`
- Username: `emp[your employee ID]` (e.g., `emp1`, `emp5`, `emp15`)
- Password: `arsi`

### 2. **Mark Attendance**
- Navigate to: **Attendance** → **Mark Attendance**
- Select the date (can backdate for testing)
- Choose action: Check In or Check Out
- Add optional notes
- System automatically records timestamp

### 3. **Apply for Leave**
- Navigate to: **Leave Management** → **Apply for Leave**
- Select leave type (Annual, Sick, Personal, etc.)
- Choose start and end dates
- Provide reason
- Submit for approval

### 4. **View Payroll**
- Navigate to: **My Payroll**
- See all salary slips
- View breakdown: Basic salary, allowances, deductions, net salary
- Check payment status

### 5. **View Personal Data**
- Dashboard shows quick overview
- Attendance history for last 10 days
- Leave request status
- Recent payroll information

---

## 🚀 Real-Time Data Updates

The system provides **instant data visibility**:
- ✅ When an employee marks attendance → immediately visible in their records
- ✅ When HR approves/rejects leave → status updates instantly
- ✅ When payroll is generated → appears in employee's payroll view
- ✅ All changes are saved to JSON files and reflected immediately

---

## 💡 Testing Tips

1. **Test Employee Login**: Try logging in as different employees (emp1, emp5, emp10, etc.)
2. **Verify Data Isolation**: Confirm each employee only sees their own data
3. **Test Attendance**: Mark attendance for different dates to build history
4. **Test Leave Flow**:
   - Employee applies for leave
   - Admin/HR approves or rejects
   - Employee sees updated status
5. **Cross-Check Admin View**: Login as admin to see all employees' data

---

## 📊 Quick Reference

**Total System Users:** 27
- Admins/HR: 2
- Employees: 25

**Total Employees in Database:** 25
- Active: 22
- Inactive: 3

**Test Data Available:**
- Attendance records: Last 10 days for all employees
- Leave applications: 21 requests across various employees
- Payroll records: 3 months (July, August, September 2025)

---

## 🔧 System Access

- **URL**: http://localhost:5002
- **All Passwords**: `arsi`
- **Data Storage**: JSON files in `/data` directory
- **Updates**: Real-time, no caching

---

**Last Updated:** October 3, 2025

