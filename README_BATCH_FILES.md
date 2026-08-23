# Pillay Sir's ICSE Classes - Batch File Launchers

This document explains how to use the Windows batch files for launching the Django dashboard and WhatsApp reminder system.

## 📁 Available Batch Files

### 1. `start_dashboard_and_reminders.bat` (Main Launcher)
**Purpose**: Launches both Django dashboard and WhatsApp reminders together
**Features**:
- ✅ Starts Django development server
- ✅ Opens dashboard in browser automatically
- ✅ Runs WhatsApp reminder script
- ✅ Creates separate windows for each service
- ✅ Comprehensive error checking
- ✅ Automatic logging to `logs\reminder_log.txt`

### 2. `start_django_dashboard.bat` (Dashboard Only)
**Purpose**: Launches only the Django dashboard
**Features**:
- ✅ Starts Django development server
- ✅ Opens dashboard in browser
- ✅ Checks for database migrations
- ✅ Port conflict detection
- ✅ Displays all available URLs

### 3. `run_whatsapp_reminders.bat` (Reminders Only)
**Purpose**: Runs only the WhatsApp reminder script
**Features**:
- ✅ Runs WhatsApp reminder script once
- ✅ Logs output to file
- ✅ Opens log file after completion
- ✅ User confirmation before sending

## 🚀 How to Use

### Quick Start (Recommended)
1. **Double-click** `start_dashboard_and_reminders.bat`
2. Wait for the services to start
3. Dashboard will open automatically in your browser
4. WhatsApp reminders will run in a separate window

### Individual Services
- **Dashboard Only**: Double-click `start_django_dashboard.bat`
- **Reminders Only**: Double-click `run_whatsapp_reminders.bat`

## 📋 Prerequisites

### Required Software
- ✅ **Python 3.x** installed and in PATH
- ✅ **Django** and all project dependencies installed
- ✅ **WhatsApp Web** logged in (for reminders)

### Required Files
- ✅ `manage.py` (Django project file)
- ✅ `send_whatsapp_reminders.py` (WhatsApp script)
- ✅ Database properly configured

## 🔧 Configuration

### Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser  # If needed
```

### WhatsApp Setup
1. Open WhatsApp Web in your browser
2. Scan QR code to log in
3. Keep the browser tab open while running reminders

## 📊 Monitoring & Logs

### Log Files Location
- **WhatsApp Logs**: `logs\reminder_log.txt`
- **Django Logs**: Console output in Django server window

### Viewing Logs
- WhatsApp logs are automatically opened after reminder completion
- Django server logs appear in the server console window

## 🛠️ Troubleshooting

### Common Issues

#### "Python is not installed or not in PATH"
**Solution**: 
1. Install Python from python.org
2. Add Python to Windows PATH
3. Restart command prompt

#### "Port 8000 is already in use"
**Solution**:
1. Close existing Django server windows
2. Or use Task Manager to end Python processes
3. Run the batch file again

#### "manage.py not found"
**Solution**:
1. Make sure you're running the batch file from the project root
2. The batch file should be in the same folder as `manage.py`

#### WhatsApp reminders not sending
**Solution**:
1. Ensure WhatsApp Web is open and logged in
2. Check your internet connection
3. Verify phone numbers are in correct format (+91xxxxxxxxxx)
4. Check `logs\reminder_log.txt` for error details

### Error Checking
All batch files include comprehensive error checking:
- ✅ Python installation verification
- ✅ Required file existence checks
- ✅ Port availability checking
- ✅ Service startup verification

## 🕒 Windows Task Scheduler Integration

### Scheduling Automatic Reminders
1. Open **Task Scheduler**
2. Create **New Task**
3. Set **Trigger** (e.g., daily at 9:00 AM)
4. Set **Action**: Start Program
5. **Program**: `C:\path\to\run_whatsapp_reminders.bat`
6. **Start in**: `C:\path\to\fees_management_system\`

### Recommended Schedule
- **Daily reminders**: 9:00 AM
- **Dashboard startup**: On system startup (optional)

## 📱 URLs After Launch

Once the Django server starts, these URLs will be available:

- **Dashboard**: http://127.0.0.1:8000/dashboard/
- **Students List**: http://127.0.0.1:8000/students/
- **Reports**: http://127.0.0.1:8000/reports/
- **Analytics**: http://127.0.0.1:8000/analytics/
- **WhatsApp Panel**: http://127.0.0.1:8000/whatsapp-panel/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🎯 Best Practices

### For Daily Use
1. Use `start_dashboard_and_reminders.bat` for complete automation
2. Keep WhatsApp Web logged in
3. Check logs regularly for any issues

### For Development
1. Use `start_django_dashboard.bat` for development work
2. Use `run_whatsapp_reminders.bat` for testing reminders

### For Production
1. Consider using proper web server (not development server)
2. Set up proper logging and monitoring
3. Use Windows Services for background tasks

## 🆘 Support

If you encounter issues:
1. Check the error messages in the console
2. Review log files in the `logs\` directory
3. Ensure all prerequisites are met
4. Verify file paths and permissions

---

**Created for Pillay Sir's ICSE Classes Fees Management System**  
*Excellence in Education* 🎓
