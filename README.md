# WorkTrace — QR-Based Employee Time Tracking System

## Overview

WorkTrace is a full-stack Flask web application that lets employees clock in and out by scanning QR codes with their phones. Managers log into an admin dashboard to review, approve, and export timesheets. Once a shift is approved, the employee receives an email confirmation with a PDF receipt summarizing hours worked, rest time, and salary earned.

---

## Features

- **QR Code Clock-In / Clock-Out** — Employees scan a QR code on their phone, which opens a responsive form to submit their shift details.
- **Admin Dashboard** — Secure login-protected panel to manage employees, view time records, approve shifts, and configure settings.
- **Approval Workflow** — Records stay *Pending* until an admin approves them. Approval triggers automatic PDF generation and email delivery.
- **PDF Receipts** — Generated with `reportlab`; includes employee info, clock-in/out times, rest/break duration, hours worked, and salary.
- **Email Notifications** — Uses Python's built-in `smtplib` to send approved timesheets as PDF attachments.
- **Network Auto-Detection** — Automatically detects the machine's LAN IP so QR codes work across phones on the same Wi-Fi.
- **Rest / Break Time Tracking** — Employees declare break minutes on clock-out; the system subtracts it from total duration before calculating pay.
- **SQLite Database** — Lightweight, file-based relational storage with SQLAlchemy ORM.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | SQLite + Flask-SQLAlchemy |
| Authentication | Flask-Login + Werkzeug password hashing |
| PDF Generation | ReportLab |
| QR Codes | `qrcode[pil]` |
| Email | `smtplib` + `email.mime` (standard library) |
| Frontend | HTML5, CSS3, Jinja2 templates |
| Environment | `python-dotenv` for `.env` configuration |

---

## Python Concepts Used

This project demonstrates many important Python programming concepts, from the standard library to third-party frameworks. Below is a breakdown of what each part teaches.

### 1. Web Framework: Flask

**File:** `app.py`

Flask is a micro web framework. In this project it handles routing, request/response cycles, template rendering, and session management.

```python
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
```

**Concepts demonstrated:**
- **Decorator pattern** — `@app.route()` is a function decorator that registers a URL pattern.
- **Request/Response cycle** — `request.form` reads POST data; `render_template()` returns HTML.
- **URL building** — `url_for('index')` generates URLs dynamically by endpoint name.
- **Flash messaging** — One-time session messages shown to the user after redirects.

### 2. Object-Relational Mapping (ORM) with SQLAlchemy

**File:** `app.py` (Models: `Admin`, `Employee`, `TimeRecord`)

SQLAlchemy lets you define database tables as Python classes. This eliminates raw SQL for most operations.

```python
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, default=15.00)

    time_records = db.relationship('TimeRecord', backref='employee', lazy=True)
```

**Concepts demonstrated:**
- **Class-based modeling** — Each table is a class inheriting from `db.Model`.
- **Column types and constraints** — `primary_key`, `unique`, `nullable`, `default`.
- **Relationships** — `db.relationship()` links `Employee` to `TimeRecord`; `backref` creates the reverse pointer automatically.
- **Lazy loading** — Records are fetched from the DB only when accessed.
- **Query API** — `Employee.query.filter_by(staff_id='S001').first()` uses method chaining.

### 3. Database Migrations (Lightweight)

**File:** `app.py` — `_migrate_db()` function

Because SQLite doesn't have a built-in migration tool like Alembic, the app includes a lightweight migration function that checks existing columns and alters the schema if new fields (like `rest_minutes`) are missing.

```python
def _migrate_db():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    cols = [c['name'] for c in inspector.get_columns('time_record')]
    if 'rest_minutes' not in cols:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE time_record ADD COLUMN rest_minutes FLOAT DEFAULT 0.0"))
            conn.commit()
```

**Concepts demonstrated:**
- **Schema introspection** — Reading the database structure at runtime.
- **Conditional DDL execution** — Only running `ALTER TABLE` when needed.
- **Context managers** — `with db.engine.connect() as conn` ensures the connection closes cleanly.

### 4. User Authentication with Flask-Login

**File:** `app.py`

Flask-Login manages user sessions without you having to write session-handling code.

```python
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

class Admin(UserMixin, db.Model):
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

**Concepts demonstrated:**
- **Multiple inheritance** — `Admin` inherits from both `UserMixin` (Flask-Login helpers) and `db.Model`.
- **Password hashing** — `werkzeug.security.generate_password_hash` uses PBKDF2 with SHA-256.
- **Session management** — `login_user(admin)` creates a secure session cookie.
- **Access control** — `@login_required` decorator blocks unauthenticated users.
- **Global user state** — `current_user` is available in any request context.

### 5. Decorators and Higher-Order Functions

**File:** `app.py`

Decorators are used everywhere in Flask. The project also includes custom error handler decorators.

```python
@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('error.html', code=500, message='Internal Server Error'), 500
```

**Concepts demonstrated:**
- **Function decorators** — `@app.route`, `@login_required`, `@app.errorhandler` all wrap functions.
- **Higher-order functions** — Decorators take a function and return a modified function.
- **Error handling as functions** — HTTP errors are mapped to Python functions dynamically.

### 6. Standard Library: `datetime` and `timedelta`

**File:** `app.py`

Time arithmetic is central to calculating hours worked.

```python
from datetime import datetime, timedelta

time_diff = clock_out_time - clock_in_time
hours_worked = round(time_diff.total_seconds() / 3600, 2)
```

**Concepts demonstrated:**
- **Date/time objects** — `datetime` stores both date and time.
- **Time deltas** — `timedelta` represents the difference between two datetimes.
- **Arithmetic on timestamps** — Subtraction yields a `timedelta`; `.total_seconds()` converts it to a float.

### 7. Standard Library: `socket` (Network Programming)

**File:** `app.py`

To make QR codes scannable from phones on the same network, the app detects the machine's local IP address.

```python
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
```

**Concepts demonstrated:**
- **Socket creation** — `socket.socket()` with `AF_INET` (IPv4) and `SOCK_DGRAM` (UDP).
- **Network probing** — Connecting to a public DNS server (`8.8.8.8`) forces the OS to reveal the local routing IP.
- **Resource cleanup** — Explicit `s.close()` (though a context manager would also work).

### 8. Standard Library: `smtplib` and `email.mime`

**File:** `app.py` — `send_timesheet_email()` function

Python's standard library includes a full email client. No third-party email service is required.

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = employee.email
msg['Subject'] = 'Timesheet - May 24, 2026'
msg.attach(MIMEText(body, 'plain'))

with open(pdf_path, 'rb') as f:
    part = MIMEBase('application', 'pdf')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="timesheet.pdf"')
    msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(username, password)
server.send_message(msg)
server.quit()
```

**Concepts demonstrated:**
- **MIME multipart messages** — Combining plain text and binary attachments in one email.
- **Base64 encoding** — `encoders.encode_base64(part)` encodes the PDF for email transport.
- **SMTP protocol** — `smtplib.SMTP` handles the conversation with the mail server.
- **TLS encryption** — `starttls()` upgrades the connection to encrypted.
- **Exception taxonomy** — Catching `SMTPAuthenticationError`, `SMTPConnectError`, and generic `Exception` separately.

### 9. Optional Import Pattern (Graceful Degradation)

**File:** `app.py`

The app tries to import optional libraries and falls back gracefully if they are missing.

```python
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
```

**Concepts demonstrated:**
- **Exception handling (`try/except`)** — Catching `ImportError` at runtime.
- **Feature flags** — `QR_AVAILABLE` and `PDF_AVAILABLE` booleans control behavior later in the code.
- **Defensive programming** — The app starts even if some libraries aren't installed; it just warns the user.

### 10. String Formatting with f-Strings

**File:** throughout `app.py`

Python f-strings (formatted string literals) make dynamic text generation readable and fast.

```python
today = datetime.now().strftime('%Y%m%d')
clock_in_url = f'{NETWORK_URL}/clock-in'
flash(f'{name}, you clocked in at {clock_in_datetime.strftime("%I:%M %p")}!')
```

**Concepts demonstrated:**
- **f-string interpolation** — Embedding expressions directly inside strings with `{}`.
- **Date formatting** — `strftime()` with format codes like `%I:%M %p`.

### 11. File System Operations

**File:** `app.py` — `_safe_qr_folder()`, `_safe_pdf_folder()`

```python
def _safe_qr_folder():
    folder = app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    return folder
```

**Concepts demonstrated:**
- **Path manipulation** — `os.path.join()`, `os.path.dirname()`, `os.path.abspath()`.
- **Directory creation** — `os.makedirs(..., exist_ok=True)` creates nested folders safely.
- **Binary file I/O** — Writing QR images and reading PDF attachments in `'rb'` mode.

### 12. Environment Configuration with `os.environ` and `python-dotenv`

**File:** `app.py`

```python
from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
```

**Concepts demonstrated:**
- **Environment variables** — Storing secrets outside the source code.
- **Default values** — `os.environ.get('KEY', 'default')` falls back if the variable is missing.
- **Cryptographically secure randomness** — `secrets.token_hex(32)` generates a 64-character hex key.

### 13. Logging

**File:** `app.py`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

logger.info('WorkTrace starting on http://0.0.0.0:5000')
logger.error(f'Clock-in error: {e}', exc_info=True)
```

**Concepts demonstrated:**
- **The `logging` module** — Python's standard, configurable logging system.
- **Named loggers** — `getLogger(__name__)` creates a logger per module.
- **Log levels** — `INFO` for normal events, `ERROR` for problems.
- **Exception traces** — `exc_info=True` includes the full traceback.

### 14. Instance Methods and Encapsulation

**File:** `app.py` — `TimeRecord.calculate_hours_and_salary()`

```python
class TimeRecord(db.Model):
    def calculate_hours_and_salary(self):
        if self.clock_in_time and self.clock_out_time:
            time_diff = self.clock_out_time - self.clock_in_time
            raw_hours = time_diff.total_seconds() / 3600
            rest_hours = (self.rest_minutes or 0) / 60
            self.hours_worked = round(max(0, raw_hours - rest_hours), 2)
            self.salary_earned = round(self.hours_worked * self.hourly_rate_used, 2)
        return self.hours_worked, self.salary_earned
```

**Concepts demonstrated:**
- **Instance methods** — `self` gives access to the object's own attributes.
- **Business logic inside the model** — Calculations live with the data they operate on.
- **Tuple return** — Returning multiple values as a tuple.
- **`max()` for bounds checking** — Ensures hours never go negative.

### 15. Global Variables and State Management

**File:** `app.py`

The network URL is stored in module-level globals and updated at runtime.

```python
NETWORK_IP = os.environ.get('NETWORK_IP', get_local_ip())
NETWORK_URL = os.environ.get('NETWORK_URL', f'http://{NETWORK_IP}:5000')
```

In the admin settings route:
```python
@app.route('/admin/network-settings', methods=['POST'])
def admin_network_settings():
    global NETWORK_URL, NETWORK_IP
    NETWORK_URL = request.form.get('network_url')
    NETWORK_IP = NETWORK_URL.replace('http://', '').split(':')[0]
    # persist to .env ...
```

**Concepts demonstrated:**
- **Global state** — Module-level variables shared across the application.
- **`global` keyword** — Required to reassign a global variable inside a function.
- **Runtime configuration** — Changing behavior without restarting the server.

### 16. Template Rendering with Jinja2

**Files:** `templates/*.html`

Jinja2 is Flask's default templating engine. It separates HTML from Python logic.

```html
<!-- index.html -->
{% if clock_in_qr %}
  <img src="{{ url_for('static', filename='qr_codes/' + clock_in_qr) }}" />
{% else %}
  <div class="qr-placeholder">QR unavailable</div>
{% endif %}
```

**Concepts demonstrated:**
- **Template inheritance** — `{% extends "base.html" %}` and `{% block content %}`.
- **Control structures** — `{% if %}`, `{% for %}`, `{% with %}`.
- **Expression interpolation** — `{{ variable }}` renders Python values safely.
- **URL generation in templates** — `url_for('clock_in_form')` keeps links valid when routes change.
- **Auto-escaping** — Jinja2 escapes HTML by default to prevent XSS attacks.

### 17. Error Handling and Rollback

**File:** `app.py`

Database operations are wrapped in try/except blocks with explicit rollback on failure.

```python
try:
    db.session.add(record)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    logger.error(f'Clock-in error: {e}')
    flash('An error occurred. Please try again.', 'error')
```

**Concepts demonstrated:**
- **Transaction safety** — `commit()` saves changes; `rollback()` reverts them on failure.
- **Graceful degradation** — Users see a friendly message instead of a crash.
- **Logging failures** — Errors are captured in the server log for debugging.

### 18. List Comprehensions and Generator Expressions

**File:** `app.py`

```python
# List comprehension — builds a full list in memory
records_dict = {r.staff_id: r for r in today_records}

# Generator expression — lazy evaluation
clocked_in = sum(1 for r in today_records if r.clock_in_time and not r.clock_out_time)
```

**Concepts demonstrated:**
- **Dictionary comprehensions** — `{key: value for ...}` maps records by staff ID.
- **Generator expressions** — `sum(1 for ...)` counts without building a list.
- **Lazy evaluation** — Generators are memory-efficient for large datasets.

### 19. JSON API Endpoints

**File:** `app.py`

```python
@app.route('/api/employees')
@login_required
def api_employees():
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    return jsonify([{
        'staff_id': e.staff_id,
        'name': e.name,
        'position': e.position,
        'hourly_rate': e.hourly_rate,
    } for e in employees])
```

**Concepts demonstrated:**
- **JSON serialization** — `jsonify()` converts Python dicts/lists to JSON.
- **List comprehension in API responses** — Transforming ORM objects to plain dictionaries.
- **RESTful patterns** — Returning data structures rather than HTML pages.

---

## Project Structure

```
worktrace/
├── cli.py                  # Command-line interface (main entry point)
├── app.py                  # Flask web app: routes, models, helpers
├── requirements.txt        # Python dependencies
├── test_app.py             # pytest test suite
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── clock_in.html
│   ├── clock_out.html
│   ├── clock_in_success.html
│   ├── clock_out_success.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_employees.html
│   ├── admin_records.html
│   ├── admin_employee_form.html
│   ├── admin_qr_codes.html
│   ├── admin_email_settings.html
│   ├── admin_network_settings.html
│   └── error.html
├── static/
│   ├── css/style.css       # Custom CSS (no frameworks)
│   ├── js/main.js
│   └── qr_codes/           # Generated QR images
├── pdfs/                   # Generated PDF timesheets
├── instance/
│   └── worktrace.db        # SQLite database
└── .env                    # Environment variables (optional)
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2a. Run the CLI Version (Recommended for Demo)

```bash
python cli.py
```

This opens an interactive menu in your terminal:
- **Clock In / Clock Out** — Employees enter their Staff ID and shift details via prompts.
- **View My Records** — Shows a formatted table of past shifts, hours, and salary.
- **Generate QR Codes** — Prints ASCII QR codes directly in the terminal and saves image files.
- **Admin Dashboard** — Login to view all records, approve shifts, manage employees, and send email confirmations.
- **Settings** — Configure email SMTP and network URL for QR codes.

**Default admin credentials:**
- Username: `admin`
- Password: `admin123`

### 2b. Run the Web Version (Optional)

```bash
python app.py
```

The Flask server starts on `http://0.0.0.0:5000`. Employees can scan QR codes with their phones to access the clock-in/out forms.

| Page | URL |
|------|-----|
| Homepage / QR Codes | `http://127.0.0.1:5000/` |
| Clock In | `http://127.0.0.1:5000/clock-in` |
| Clock Out | `http://127.0.0.1:5000/clock-out` |
| Admin Login | `http://127.0.0.1:5000/admin/login` |

### 4. Configure Email (Optional)

Go to **Admin → Email Settings** and enter your SMTP details, or create a `.env` file:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

### 5. Configure Network URL for QR Codes

The app auto-detects your LAN IP, but if it guesses wrong, go to **Admin → Network Settings** and set the correct URL (e.g., `http://192.168.1.50:5000`).

---

## Database Schema

```
admin
├── id (PK)
├── username (unique)
├── password_hash
└── created_at

employee
├── id (PK)
├── staff_id (unique)
├── name
├── position
├── email (unique)
├── hourly_rate
├── is_active
└── created_at

time_record
├── id (PK)
├── staff_id (FK → employee.staff_id)
├── date
├── employee_name
├── position
├── clock_in_time
├── clock_in_submitted
├── clock_out_time
├── clock_out_submitted
├── rest_minutes
├── hours_worked
├── salary_earned
├── hourly_rate_used
├── is_approved
├── approved_by (FK → admin.id)
├── approved_at
├── pdf_generated
└── notes
```

---

## Testing

Run the test suite with pytest:

```bash
python -m pytest test_app.py -v
```

Tests cover:
- Model creation and relationships
- Password hashing
- Clock-in/out form validation and business rules
- Admin authentication and authorization
- Record approval and PDF generation
- API endpoints

---

## Security Considerations

- **Passwords** are hashed with PBKDF2-SHA256 via Werkzeug.
- **Sessions** are protected by a `SECRET_KEY` (generate a random one in production).
- **CSRF protection** is implicit for POST forms via session validation.
- **Open redirects** are blocked in the login flow.
- **File uploads** are limited to 16MB.
- **SQL injection** is prevented by the SQLAlchemy ORM.
- **XSS** is mitigated by Jinja2's auto-escaping.

---

## License

This project is provided for educational and demonstration purposes.
