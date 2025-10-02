# Settings and Security Features

**Bareera Intl. HR Module - New Features**  
**Date**: October 2, 2025

---

## Overview

This document describes the newly added settings, preferences, and security features to the HR Module.

---

## Features Added

### 1. ✅ System Settings Page

**Access**: Admin and HR Staff only

**Location**: User menu → Settings

**Features**:
- **Company Information**
  - Company name, email, phone, address
  
- **Working Hours Configuration**
  - Start time and end time
  - Lunch break duration
  - Working days
  
- **Leave Policies**
  - Annual leave quota
  - Sick leave quota
  - Casual leave quota
  - Carry forward settings
  - Maximum carry forward days
  
- **Payroll Settings**
  - Currency selection (PKR, USD, EUR)
  - Pay day (day of month)
  - Tax rate
  - Provident fund rate

**How to Access**:
1. Login as Admin or HR Staff
2. Click on your username in the top-right
3. Select "Settings" from the dropdown
4. Update any settings
5. Click "Save Settings"

**Data Storage**: `/data/settings.json`

---

### 2. ✅ Forgot Password Feature

**Access**: Public (available on login page)

**Location**: Login page → "Forgot Password?" link

**How it Works**:
1. Click "Forgot Password?" on the login page
2. Enter your username and registered email address
3. System verifies the email matches your employee profile
4. A temporary password is generated and displayed on screen
5. Login with the temporary password
6. **Important**: Change your password immediately after logging in

**Security Notes**:
- Email must match the email in employee profile
- Temporary passwords are randomly generated (8 characters)
- Passwords are stored as bcrypt hashes (never in plain text)

**Limitations** (Current Version):
- Temporary password is shown on screen (not emailed)
- For production, integrate with SMTP server for email delivery

---

### 3. ✅ Change Password Feature

**Access**: All users (after login)

**Location**: User menu → Change Password

**Features**:
- Change your own password
- Requires current password verification
- New password must be at least 6 characters
- Confirm password validation

**How to Use**:
1. Click on your username in top-right
2. Select "Change Password"
3. Enter your current password
4. Enter new password (minimum 6 characters)
5. Confirm new password
6. Click "Change Password"

**Security Requirements**:
- Must know current password
- Minimum password length: 6 characters
- Password confirmation must match
- All passwords are bcrypt hashed

---

### 4. ✅ Salary Information Hidden from Employees

**What Changed**:
- Regular employees can no longer see salary information
- Salary field hidden in employee detail view
- Employee payroll list restricted to own records

**Who Can See Salary Information**:
- ✅ **Admin**: Can see all salaries
- ✅ **HR Staff**: Can see all salaries
- ❌ **Employees**: Cannot see any salary information (except their own payroll slips)

**Affected Pages**:
- **Employee Detail View**: Salary field only visible to Admin/HR Staff
- **Employee Add/Edit Forms**: Already protected (only Admin/HR Staff can access)
- **Payroll**: Employees can only view their own payroll slips
- **Applicant Details**: Salary expectations only visible to Admin/HR Staff

**Backend Protection**:
- All employee management routes protected with `@role_required('Admin', 'HR Staff')`
- Payroll view route checks role and employee_id match
- Session-based role validation on every request

---

## Updated Navigation

### User Dropdown Menu

**All Users See**:
- Change Password
- Logout

**Admin & HR Staff Also See**:
- Settings (at the top)

---

## Security Improvements

### 1. Role-Based Access Control (Enhanced)

**Role Hierarchy**:
```
Admin
  ├─ Full access to all features
  ├─ Can manage system settings
  ├─ Can view all salary information
  └─ Can modify all records

HR Staff
  ├─ Can manage employees, attendance, leaves, payroll
  ├─ Can manage job postings and applicants
  ├─ Can view all salary information
  └─ Can modify system settings

Employee
  ├─ Can view employee directory (without salaries)
  ├─ Can mark own attendance
  ├─ Can apply for leaves
  ├─ Can view own payroll slips
  └─ Cannot see salary information
```

### 2. Password Security

- ✅ Bcrypt hashing with salt
- ✅ Minimum 6 characters requirement
- ✅ Password reset with verification
- ✅ Current password required for changes

### 3. Session Management

- ✅ Session-based authentication
- ✅ Role stored in session
- ✅ Login required for protected routes
- ✅ Role verification on sensitive operations

---

## Configuration Files

### settings.json

Located at: `/data/settings.json`

**Structure**:
```json
{
  "company_info": {
    "company_name": "Bareera International",
    "company_email": "hr@bareera.com",
    "company_phone": "+92-300-1234567",
    "company_address": "Karachi, Pakistan"
  },
  "working_hours": {
    "start_time": "09:00",
    "end_time": "18:00",
    "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "lunch_break_duration": 60
  },
  "leave_policies": {
    "annual_leave_quota": 15,
    "sick_leave_quota": 10,
    "casual_leave_quota": 5,
    "carry_forward_allowed": true,
    "max_carry_forward_days": 5
  },
  "payroll_settings": {
    "currency": "PKR",
    "pay_day": 25,
    "tax_rate": 0.05,
    "provident_fund_rate": 0.08
  },
  "security_settings": {
    "session_timeout_minutes": 60,
    "password_reset_enabled": true,
    "min_password_length": 6
  }
}
```

**Note**: Modify these settings via the Settings page in the UI, or edit the JSON file directly.

---

## Testing Checklist

### ✅ All Features Tested

- [x] Settings page loads for Admin
- [x] Settings page loads for HR Staff
- [x] Settings page redirects Employee to login
- [x] Company info can be updated
- [x] Working hours can be modified
- [x] Leave policies can be configured
- [x] Payroll settings can be adjusted
- [x] Forgot password link appears on login page
- [x] Forgot password validates username and email
- [x] Temporary password is generated
- [x] Change password page loads
- [x] Change password validates current password
- [x] Change password validates minimum length
- [x] Change password validates password match
- [x] Employee cannot see salary in detail view
- [x] Employee can only see own payroll
- [x] Admin can see all salaries
- [x] HR Staff can see all salaries
- [x] Navigation shows correct options per role

---

## API Routes Added

### Settings Routes

```python
GET/POST  /settings              # View/Update system settings (Admin/HR Staff)
GET/POST  /forgot-password       # Password reset request (Public)
GET/POST  /change-password       # Change user password (Authenticated)
```

---

## User Guide

### For Administrators

**Initial Setup**:
1. Login as Admin
2. Go to Settings (User menu → Settings)
3. Update company information
4. Configure working hours
5. Set leave policies
6. Configure payroll settings
7. Save settings

**Managing User Passwords**:
- Users can reset their own passwords via "Forgot Password"
- Users can change passwords via "Change Password"
- For security, passwords are never shown or emailed

### For HR Staff

**Settings Access**:
- Same as Admin - can view and modify all system settings
- Can see all employee salary information
- Can manage all HR functions

### For Employees

**Password Management**:
1. **Forgot Password**: Use the link on login page if you forget your password
2. **Change Password**: After logging in, go to User menu → Change Password

**Privacy**:
- You cannot see other employees' salaries
- You can only view your own payroll slips
- All your personal information is visible to HR and Admin

---

## Future Enhancements

### Planned for Production

1. **Email Integration**
   - Send password reset links via email
   - Email temporary passwords instead of showing on screen
   - Send notifications for settings changes

2. **Advanced Settings**
   - User permission customization
   - Department-specific settings
   - Holiday calendar management
   - Automated backup schedule

3. **Audit Logging**
   - Track settings changes
   - Log password resets
   - Monitor access to sensitive information

4. **Enhanced Security**
   - Two-factor authentication (2FA)
   - Password complexity requirements
   - Password expiration policies
   - Login attempt limits

---

## Troubleshooting

### Settings Page Not Loading

**Issue**: Getting 403 Forbidden or redirected to login

**Solution**: 
- Make sure you're logged in as Admin or HR Staff
- Employee role cannot access settings

### Forgot Password Not Working

**Issue**: "Username and email do not match"

**Solution**:
- Verify the email matches your employee profile email
- Contact HR if your employee profile email is incorrect
- Only users linked to employee profiles can reset passwords

### Cannot Change Password

**Issue**: "Current password is incorrect"

**Solution**:
- Double-check your current password
- Use "Forgot Password" if you don't remember it

### Salary Still Visible to Employees

**Issue**: Employee role can still see salaries

**Solution**:
- Clear browser cache
- Restart the Flask application
- Verify the user is logged in as "Employee" role

---

## Security Best Practices

### For Administrators

1. **Change Default Passwords**: Update all default test account passwords
2. **Regular Audits**: Review user access and permissions regularly
3. **Settings Backup**: Export settings regularly using data export script
4. **Access Control**: Only grant Admin/HR Staff roles to trusted personnel

### For All Users

1. **Strong Passwords**: Use complex passwords with mix of characters
2. **Don't Share**: Never share your password with anyone
3. **Regular Changes**: Change password periodically
4. **Secure Login**: Always logout when finished

---

## Support

For questions or issues with these features:
- **Developer**: Codecraft Studios Pakistan (CSP)
- **Project**: Bareera Intl. HR Module
- **Date**: October 2025

---

**Last Updated**: October 2, 2025  
**Version**: 2.1 (Settings & Security Features)  
**Status**: Complete and Tested

