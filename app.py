"""
WorkTrace Web Application
QR-based Employee Time Tracking System

This file is the main Python code that runs the whole web app.
It handles:
  - The web server (Flask)
  - The database (SQLite with SQLAlchemy)
  - User login (Flask-Login)
  - QR code creation
  - PDF receipt creation
  - Sending emails
  - All the web pages (routes)
"""

# ------------------------------------------------------------------
# SECTION 1: IMPORTS
# We bring in built-in Python tools and outside libraries we installed.
# ------------------------------------------------------------------

import os          # Lets us work with files and folders
import secrets     # Creates safe random passwords / keys
import logging     # Writes messages to a log file so we can see errors
import socket      # Helps us find the computer's IP address
from datetime import datetime, timedelta  # Work with dates and times
from functools import wraps               # A helper for making decorators

# Try to load secret settings from a .env file (if it exists)
try:
    from dotenv import load_dotenv
    load_dotenv()      # This reads the .env file into memory
except ImportError:
    pass               # If dotenv is not installed, just skip it

# Flask is the web framework.  It turns Python functions into web pages.
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_file, abort, jsonify
)

# smtplib is Python's built-in tool for sending emails
import smtplib
from email.mime.multipart import MIMEMultipart   # Lets us attach files to emails
from email.mime.base import MIMEBase
from email.mime.text import MIMEText             # The plain-text body of the email
from email import encoders                        # Turns files into email-safe format

# Flask-SQLAlchemy is an add-on that lets us use a database
# without writing raw SQL.  We write Python classes instead.
from flask_sqlalchemy import SQLAlchemy

# Flask-Login handles "who is logged in?" for the admin dashboard.
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)

# Werkzeug gives us password hashing (so we never store plain passwords)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException

# QR codes are optional.  If the library is missing we just show a warning.
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# PDF creation is optional too.  ReportLab builds PDF files from code.
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ------------------------------------------------------------------
# SECTION 2: LOGGING
# We set up a simple logger so we can write info / error messages.
# ------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)   # __name__ is just the current file name

# ------------------------------------------------------------------
# SECTION 3: CREATE THE FLASK APP
# This is the heart of the program.  app is our web server object.
# ------------------------------------------------------------------

app = Flask(__name__)   # __name__ tells Flask where to find templates and static files

# SECRET_KEY is used to keep user sessions safe.  We grab it from an
# environment variable, or make a random one if nothing is set.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# SQLALCHEMY_DATABASE_URI tells SQLAlchemy where to store the database.
# 'sqlite:///worktrace.db' means a local file called worktrace.db.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///worktrace.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off a feature we don't need

# UPLOAD_FOLDER is where QR code images are saved
app.config['UPLOAD_FOLDER'] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static', 'qr_codes'
)

# PDF_FOLDER is where receipt PDFs are saved
app.config['PDF_FOLDER'] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'pdfs'
)

# MAX_CONTENT_LENGTH limits how big an uploaded file can be (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ------------------------------------------------------------------
# SECTION 4: NETWORK SETTINGS
# We need the computer's IP address so phones on the same Wi-Fi
# can scan the QR code and reach the website.
# ------------------------------------------------------------------

def get_local_ip():
    """Find the computer's local network IP (e.g. 192.168.1.5)."""
    try:
        # We open a fake connection to the internet.  The computer tells us
        # which local IP it would use.  We don't actually send any data.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass
    # Fallback: ask the computer its own name
    try:
        hostname = socket.gethostname()
        ip = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
        if not ip.startswith('127.'):
            return ip
    except Exception:
        pass
    return '127.0.0.1'   # If everything fails, use localhost


# NETWORK_URL is the address encoded inside the QR codes.
# We read it from an environment variable, or build it from the local IP.
NETWORK_IP = os.environ.get('NETWORK_IP', get_local_ip())
NETWORK_URL = os.environ.get('NETWORK_URL', f'http://{NETWORK_IP}:5000')

# ------------------------------------------------------------------
# SECTION 5: EMAIL SETTINGS
# These settings tell the program how to send emails (e.g. Gmail).
# They can be stored in a .env file so passwords are not in the code.
# ------------------------------------------------------------------

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')
app.config['DEFAULT_HOURLY_RATE'] = float(os.environ.get('DEFAULT_HOURLY_RATE', 15.00))

# ------------------------------------------------------------------
# SECTION 6: CREATE DATABASE AND LOGIN MANAGER
# db is our database object.  login_manager handles admin sessions.
# ------------------------------------------------------------------

db = SQLAlchemy(app)                     # Link SQLAlchemy to our Flask app
login_manager = LoginManager(app)          # Link Flask-Login to our app
login_manager.login_view = 'admin_login' # Where to send users who are not logged in
login_manager.login_message = 'Please log in to access the admin dashboard.'
login_manager.login_message_category = 'warning'

# ------------------------------------------------------------------
# SECTION 7: DATABASE MODELS
# Models are Python classes that become tables in the SQLite database.
# Each class = one table.  Each variable inside = one column.
# ------------------------------------------------------------------

# --- Admin table ---
# Stores the username and hashed password for managers.
class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)          # Auto-increment ID
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Turn a plain password into a scrambled hash we can store safely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the password the user typed matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


# --- Employee table ---
# Stores each worker's details (name, ID, pay rate, email, etc.)
class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    hourly_rate = db.Column(
        db.Float,
        default=lambda: app.config.get('DEFAULT_HOURLY_RATE', 15.00),
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # This line creates a link between Employee and TimeRecord.
    # It means: "One employee can have many time records."
    time_records = db.relationship(
        'TimeRecord', backref='employee', lazy=True,
        cascade='all, delete-orphan',
        order_by='TimeRecord.date.desc()'
    )

    def __repr__(self):
        return f'<Employee {self.name} ({self.staff_id})>'


# --- TimeRecord table ---
# Stores each shift (clock-in time, clock-out time, hours worked, salary).
class TimeRecord(db.Model):
    __tablename__ = 'time_record'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(
        db.String(20),
        db.ForeignKey('employee.staff_id', ondelete='CASCADE'),
        nullable=False
    )
    date = db.Column(db.Date, nullable=False, index=True)

    employee_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=True)

    clock_in_time = db.Column(db.DateTime, nullable=True)
    clock_in_submitted = db.Column(db.DateTime, nullable=True)

    clock_out_time = db.Column(db.DateTime, nullable=True)
    clock_out_submitted = db.Column(db.DateTime, nullable=True)

    hours_worked = db.Column(db.Float, default=0.0)
    rest_minutes = db.Column(db.Float, default=0.0)   # Break time in minutes
    salary_earned = db.Column(db.Float, default=0.0)
    hourly_rate_used = db.Column(db.Float, default=15.00)

    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    pdf_generated = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<TimeRecord {self.staff_id} on {self.date}>'

    def calculate_hours_and_salary(self):
        """
        Figure out how many hours were worked and how much money was earned.
        We take (Clock Out - Clock In) and subtract the break time.
        """
        if self.clock_in_time and self.clock_out_time:
            if self.clock_out_time > self.clock_in_time:
                time_diff = self.clock_out_time - self.clock_in_time
                raw_hours = time_diff.total_seconds() / 3600   # Convert seconds to hours
                rest_hours = (self.rest_minutes or 0) / 60       # Convert minutes to hours
                self.hours_worked = round(max(0, raw_hours - rest_hours), 2)
                self.salary_earned = round(
                    self.hours_worked * self.hourly_rate_used, 2
                )
            else:
                self.hours_worked = 0.0
                self.salary_earned = 0.0
        return self.hours_worked, self.salary_earned


# This function tells Flask-Login how to find an admin by their ID.
@login_manager.user_loader
def load_user(user_id):
    try:
        return Admin.query.get(int(user_id))
    except Exception:
        return None


# ------------------------------------------------------------------
# SECTION 8: ERROR HANDLERS
# These functions show friendly error pages when something goes wrong.
# ------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400,
                           message='Bad Request',
                           detail=str(e)), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html', code=401,
                           message='Unauthorized',
                           detail='Please log in to continue.'), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403,
                           message='Forbidden',
                           detail='You do not have permission to access this page.'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404,
                           message='Page Not Found',
                           detail='The page you are looking for does not exist.'), 404

@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('error.html', code=413,
                           message='File Too Large',
                           detail='The uploaded file is too large.'), 413

@app.errorhandler(500)
def internal_error(e):
    # If something breaks, undo any half-finished database changes
    db.session.rollback()
    logger.error(f'Server Error: {e}')
    return render_template('error.html', code=500,
                           message='Internal Server Error',
                           detail='Something went wrong. Please try again.'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Catch any unexpected error, log it, and show a friendly page
    if isinstance(e, HTTPException):
        return e
    db.session.rollback()
    logger.error(f'Unhandled Exception: {e}', exc_info=True)
    return render_template('error.html', code=500,
                           message='Unexpected Error',
                           detail=str(e)), 500


# ------------------------------------------------------------------
# SECTION 9: HELPER FUNCTIONS
# Small reusable pieces of code used by multiple routes.
# ------------------------------------------------------------------

def _safe_qr_folder():
    """Make sure the folder for QR images exists, then return its path."""
    folder = app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)   # exist_ok=True means don't crash if it already exists
    return folder


def _safe_pdf_folder():
    """Make sure the folder for PDF receipts exists, then return its path."""
    folder = app.config['PDF_FOLDER']
    os.makedirs(folder, exist_ok=True)
    return folder


def generate_qr_code(url: str, filename: str) -> bool:
    """Create a QR code image file from a URL.  Return True if it worked."""
    if not QR_AVAILABLE:
        logger.warning('qrcode library not available')
        return False
    try:
        folder = _safe_qr_folder()
        filepath = os.path.join(folder, filename)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)       # Put the web address inside the QR code
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        img.save(filepath)     # Save as a PNG file
        return True
    except Exception as e:
        logger.error(f'QR generation failed: {e}')
        return False


def generate_timesheet_pdf(record: 'TimeRecord') -> str | None:
    """Build a PDF receipt for one shift.  Return the file path or None."""
    if not PDF_AVAILABLE:
        logger.warning('reportlab library not available')
        return None
    try:
        folder = _safe_pdf_folder()
        filename = f"timesheet_{record.staff_id}_{record.date}.pdf"
        filepath = os.path.join(folder, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Big title at the top of the page
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=24, spaceAfter=30, alignment=1
        )
        elements.append(Paragraph('WorkTrace Timesheet', title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Look up the employee so we can add their email
        employee = Employee.query.filter_by(staff_id=record.staff_id).first()
        employee_email = employee.email if employee else 'N/A'

        # Employee info table
        info_data = [
            ['Staff ID:', record.staff_id],
            ['Employee Name:', record.employee_name],
            ['Email:', employee_email],
            ['Position:', record.position or 'N/A'],
            ['Date:', record.date.strftime('%B %d, %Y')],
            ['Status:', 'Approved' if record.is_approved else 'Pending'],
        ]
        info_table = Table(info_data, colWidths=[2 * inch, 3.5 * inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Work out the raw duration before subtracting rest time
        raw_diff = (record.clock_out_time - record.clock_in_time) if (record.clock_out_time and record.clock_in_time) else None
        raw_hours = round(raw_diff.total_seconds() / 3600, 2) if raw_diff else 0.0
        rest_hours = round((record.rest_minutes or 0) / 60, 2)

        # Time and money table
        time_data = [
            ['Clock In Time',
             record.clock_in_time.strftime('%I:%M %p') if record.clock_in_time else 'N/A'],
            ['Clock Out Time',
             record.clock_out_time.strftime('%I:%M %p') if record.clock_out_time else 'N/A'],
            ['Total Duration', f'{raw_hours:.2f} hours'],
            ['Rest / Break', f'{rest_hours:.2f} hours ({record.rest_minutes or 0:.0f} min)'],
            ['Hours Worked', f'{record.hours_worked:.2f} hours'],
            ['Hourly Rate', f'${record.hourly_rate_used:.2f}'],
            ['Total Salary', f'${record.salary_earned:.2f}'],
        ]
        time_table = Table(time_data, colWidths=[2.5 * inch, 2.5 * inch])
        time_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 4), (0, 4), colors.lightblue),
            ('BACKGROUND', (1, 4), (1, 4), colors.lightgreen),
            ('TEXTCOLOR', (1, 4), (1, 4), colors.darkgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(time_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Footer with generation date
        footer_style = ParagraphStyle(
            'Footer', parent=styles['Normal'], fontSize=10, alignment=1
        )
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            footer_style
        ))
        doc.build(elements)
        return filepath
    except Exception as e:
        logger.error(f'PDF generation error: {e}')
        return None


def send_timesheet_email(record: 'TimeRecord', pdf_path: str):
    """Send an email to the employee with the PDF attached."""
    try:
        # If email settings are missing, stop early
        if not app.config.get('MAIL_USERNAME'):
            return False, 'Email not configured'

        employee = Employee.query.filter_by(staff_id=record.staff_id).first()
        if not employee or not employee.email:
            return False, 'No email address for employee'

        # Build the email message
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
        msg['To'] = employee.email
        msg['Subject'] = f'Timesheet - {record.date.strftime("%B %d, %Y")}'

        rest_hours = round((record.rest_minutes or 0) / 60, 2)
        body = (
            f'Dear {employee.name},\n\n'
            f'Your timesheet for {record.date.strftime("%B %d, %Y")} has been approved.\n\n'
            f'Details:\n'
            f'- Clock In:  {record.clock_in_time.strftime("%I:%M %p") if record.clock_in_time else "N/A"}\n'
            f'- Clock Out: {record.clock_out_time.strftime("%I:%M %p") if record.clock_out_time else "N/A"}\n'
            f'- Rest / Break: {rest_hours:.2f} hours ({record.rest_minutes or 0:.0f} minutes)\n'
            f'- Hours Worked: {record.hours_worked:.2f}\n'
            f'- Salary Earned: ${record.salary_earned:.2f}\n\n'
            'Best regards,\nWorkTrace Management\n'
        )
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF file
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                part = MIMEBase('application', 'pdf')
                part.set_payload(f.read())
                encoders.encode_base64(part)   # Convert to base64 so email can carry it
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="timesheet_{record.staff_id}_{record.date}.pdf"'
                )
                msg.attach(part)

        # Connect to the mail server and send
        server = smtplib.SMTP(
            app.config['MAIL_SERVER'], app.config['MAIL_PORT'], timeout=10
        )
        if app.config['MAIL_USE_TLS']:
            server.starttls()                # Encrypt the connection
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True, 'Email sent successfully'
    except smtplib.SMTPAuthenticationError:
        return False, 'SMTP authentication failed – check credentials'
    except smtplib.SMTPConnectError:
        return False, 'Could not connect to mail server'
    except Exception as e:
        logger.error(f'Email send error: {e}')
        return False, str(e)


# ------------------------------------------------------------------
# SECTION 10: PUBLIC ROUTES
# These are the pages anyone can visit (no login needed).
# ------------------------------------------------------------------

@app.route('/')
def index():
    """The home page.  Shows QR codes for clock-in and clock-out."""
    today = datetime.now().strftime('%Y%m%d')
    clock_in_url = f'{NETWORK_URL}/clock-in'
    clock_out_url = f'{NETWORK_URL}/clock-out'
    clock_in_filename = f'clock_in_{today}.png'
    clock_out_filename = f'clock_out_{today}.png'

    generate_qr_code(clock_in_url, clock_in_filename)
    generate_qr_code(clock_out_url, clock_out_filename)

    # Pass the image filenames to the template so it can show them
    return render_template(
        'index.html',
        clock_in_qr=clock_in_filename,
        clock_out_qr=clock_out_filename,
        clock_in_url=clock_in_url,
        clock_out_url=clock_out_url
    )


@app.route('/clock-in', methods=['GET', 'POST'])
def clock_in_form():
    """Page where employees fill in their details to start a shift."""
    if request.method == 'POST':
        # Read the data the user typed into the form
        name = request.form.get('name', '').strip()
        staff_id = request.form.get('staff_id', '').strip().upper()
        position = request.form.get('position', '').strip()
        email = request.form.get('email', '').strip().lower()
        start_time = request.form.get('start_time', '').strip()

        # Check for missing required fields
        errors = []
        if not name:
            errors.append('Full name is required.')
        if not staff_id:
            errors.append('Staff ID is required.')
        if not email:
            errors.append('Email address is required.')
        if not start_time:
            errors.append('Start time is required.')

        if errors:
            for e in errors:
                flash(e, 'error')   # flash shows a one-time message on the next page
            return render_template('clock_in.html', now=datetime.now(),
                                   form_data=request.form)

        # Try to turn the text into a proper date+time object
        try:
            clock_in_datetime = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid time format. Please use the datetime picker.', 'error')
            return render_template('clock_in.html', now=datetime.now(),
                                   form_data=request.form)

        # Don't allow clocking in more than 15 minutes into the future
        if clock_in_datetime > datetime.now() + timedelta(minutes=15):
            flash('Clock-in time cannot be more than 15 minutes in the future.', 'error')
            return render_template('clock_in.html', now=datetime.now(),
                                   form_data=request.form)

        try:
            # Find the employee by Staff ID, or create a new one if not found
            employee = Employee.query.filter_by(staff_id=staff_id).first()
            if not employee:
                employee = Employee(
                    staff_id=staff_id, name=name,
                    position=position, email=email,
                    hourly_rate=app.config['DEFAULT_HOURLY_RATE']
                )
                db.session.add(employee)
            else:
                # Update existing employee info
                employee.name = name
                if position:
                    employee.position = position
                if email:
                    employee.email = email

            today = datetime.utcnow().date()
            existing = TimeRecord.query.filter_by(
                staff_id=staff_id, date=today
            ).first()

            # Stop if they already clocked in today
            if existing and existing.clock_in_time:
                flash(
                    f'{name}, you already clocked in today at '
                    f'{existing.clock_in_time.strftime("%I:%M %p")}.',
                    'warning'
                )
                return redirect(url_for('index'))

            # Save the new clock-in record
            record = TimeRecord(
                staff_id=staff_id,
                employee_name=name,
                position=position,
                date=today,
                clock_in_time=clock_in_datetime,
                clock_in_submitted=datetime.utcnow(),
                hourly_rate_used=employee.hourly_rate
            )
            db.session.add(record)
            db.session.commit()   # Actually write to the database
            flash(
                f'{name}, you clocked in at {clock_in_datetime.strftime("%I:%M %p")}!',
                'success'
            )
            return redirect(url_for('clock_in_success', staff_id=staff_id))

        except Exception as e:
            db.session.rollback()   # Undo anything that was half-written
            logger.error(f'Clock-in error: {e}')
            flash('An error occurred. Please try again.', 'error')
            return render_template('clock_in.html', now=datetime.now(),
                                   form_data=request.form)

    # GET request: just show the empty form
    return render_template('clock_in.html', now=datetime.now(), form_data={})


@app.route('/clock-in-success/<staff_id>')
def clock_in_success(staff_id):
    """Thank-you page after clocking in."""
    employee = Employee.query.filter_by(staff_id=staff_id).first()
    if not employee:
        abort(404)   # If the employee doesn't exist, show a 404 error page
    today = datetime.utcnow().date()
    record = TimeRecord.query.filter_by(staff_id=staff_id, date=today).first()
    return render_template('clock_in_success.html', employee=employee, record=record)


@app.route('/clock-out', methods=['GET', 'POST'])
def clock_out_form():
    """Page where employees fill in their details to end a shift."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        staff_id = request.form.get('staff_id', '').strip().upper()
        position = request.form.get('position', '').strip()
        email = request.form.get('email', '').strip().lower()
        end_time = request.form.get('end_time', '').strip()
        rest_minutes_str = request.form.get('rest_minutes', '0').strip()

        # Basic validation
        errors = []
        if not name:
            errors.append('Full name is required.')
        if not staff_id:
            errors.append('Staff ID is required.')
        if not email:
            errors.append('Email address is required.')
        if not end_time:
            errors.append('End time is required.')

        rest_minutes = 0.0
        if rest_minutes_str:
            try:
                rest_minutes = float(rest_minutes_str)
                if rest_minutes < 0:
                    errors.append('Rest time cannot be negative.')
            except ValueError:
                errors.append('Rest time must be a number (minutes).')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('clock_out.html', now=datetime.now(),
                                   form_data=request.form)

        try:
            clock_out_datetime = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid time format. Please use the datetime picker.', 'error')
            return render_template('clock_out.html', now=datetime.now(),
                                   form_data=request.form)

        try:
            today = datetime.utcnow().date()
            record = TimeRecord.query.filter_by(
                staff_id=staff_id, date=today
            ).first()

            # Must have clocked in first
            if not record or not record.clock_in_time:
                flash(
                    f'{name}, no clock-in record found for today. Please clock in first.',
                    'error'
                )
                return redirect(url_for('clock_out_form'))

            # Can't clock out twice
            if record.clock_out_time:
                flash(
                    f'{name}, you already clocked out today at '
                    f'{record.clock_out_time.strftime("%I:%M %p")}.',
                    'warning'
                )
                return redirect(url_for('index'))

            # Clock-out must be after clock-in
            if clock_out_datetime <= record.clock_in_time:
                flash('Clock-out time must be after clock-in time.', 'error')
                return render_template('clock_out.html', now=datetime.now(),
                                       form_data=request.form)

            # Save clock-out data
            record.clock_out_time = clock_out_datetime
            record.clock_out_submitted = datetime.utcnow()
            record.rest_minutes = rest_minutes
            record.employee_name = name
            if position:
                record.position = position

            # Update or create employee record
            employee = Employee.query.filter_by(staff_id=staff_id).first()
            if not employee:
                employee = Employee(
                    staff_id=staff_id, name=name,
                    position=position, email=email,
                    hourly_rate=app.config['DEFAULT_HOURLY_RATE']
                )
                db.session.add(employee)
            else:
                employee.name = name
                if position:
                    employee.position = position
                if email:
                    employee.email = email

            record.hourly_rate_used = employee.hourly_rate
            record.calculate_hours_and_salary()   # Do the math
            db.session.commit()

            flash(
                f'{name}, clocked out at {clock_out_datetime.strftime("%I:%M %p")}. '
                f'Hours: {record.hours_worked:.2f} | Earned: ${record.salary_earned:.2f}',
                'success'
            )
            return redirect(url_for('clock_out_success', staff_id=staff_id))

        except Exception as e:
            db.session.rollback()
            logger.error(f'Clock-out error: {e}')
            flash('An error occurred. Please try again.', 'error')
            return render_template('clock_out.html', now=datetime.now(),
                                   form_data=request.form)

    return render_template('clock_out.html', now=datetime.now(), form_data={})


@app.route('/clock-out-success/<staff_id>')
def clock_out_success(staff_id):
    """Thank-you page after clocking out."""
    employee = Employee.query.filter_by(staff_id=staff_id).first()
    if not employee:
        abort(404)
    today = datetime.utcnow().date()
    record = TimeRecord.query.filter_by(staff_id=staff_id, date=today).first()
    return render_template('clock_out_success.html', employee=employee, record=record)


# ------------------------------------------------------------------
# SECTION 11: ADMIN ROUTES
# These pages are only for managers.  @login_required blocks strangers.
# ------------------------------------------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Page where managers log in."""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('admin_login.html')

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)   # Tell Flask-Login "this person is logged in"
            next_page = request.args.get('next')
            # Prevent open-redirect attacks
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('admin_login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Log the manager out and send them back to the login page."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    """Main admin page showing today's stats."""
    today = datetime.utcnow().date()
    employees = Employee.query.filter_by(is_active=True).all()
    today_records = TimeRecord.query.filter_by(date=today).all()
    records_dict = {r.staff_id: r for r in today_records}

    total_employees = len(employees)
    clocked_in = sum(
        1 for r in today_records if r.clock_in_time and not r.clock_out_time
    )
    completed = sum(1 for r in today_records if r.clock_out_time)
    total_hours = sum(r.hours_worked or 0 for r in today_records if r.clock_out_time)
    total_salary = sum(r.salary_earned or 0 for r in today_records if r.clock_out_time)

    return render_template(
        'admin_dashboard.html',
        employees=employees,
        records=records_dict,
        today=today,
        total_employees=total_employees,
        clocked_in=clocked_in,
        completed=completed,
        total_hours=round(total_hours, 2),
        total_salary=round(total_salary, 2)
    )


@app.route('/admin/employees')
@login_required
def admin_employees():
    """List all employees."""
    employees = Employee.query.order_by(Employee.name).all()
    return render_template('admin_employees.html', employees=employees)


@app.route('/admin/employees/add', methods=['GET', 'POST'])
@login_required
def admin_add_employee():
    """Form to add a new employee to the system."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        staff_id = request.form.get('staff_id', '').strip().upper()
        position = request.form.get('position', '').strip()
        email = request.form.get('email', '').strip().lower() or None
        hourly_rate_str = request.form.get('hourly_rate', '15.00')

        errors = []
        if not name:
            errors.append('Employee name is required.')
        if not staff_id:
            errors.append('Staff ID is required.')

        try:
            hourly_rate = float(hourly_rate_str)
            if hourly_rate < 0:
                errors.append('Hourly rate must be non-negative.')
        except ValueError:
            errors.append('Invalid hourly rate.')
            hourly_rate = 15.00

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template(
                'admin_employee_form.html',
                employee=None,
                next_id=staff_id,
                form_data=request.form
            )

        # Make sure Staff ID and email are not already used
        if Employee.query.filter_by(staff_id=staff_id).first():
            flash(f'Staff ID {staff_id} already exists.', 'error')
            return render_template(
                'admin_employee_form.html',
                employee=None,
                next_id=staff_id,
                form_data=request.form
            )

        if email and Employee.query.filter_by(email=email).first():
            flash('An employee with that email already exists.', 'error')
            return render_template(
                'admin_employee_form.html',
                employee=None,
                next_id=staff_id,
                form_data=request.form
            )

        try:
            employee = Employee(
                staff_id=staff_id, name=name, position=position,
                email=email, hourly_rate=hourly_rate
            )
            db.session.add(employee)
            db.session.commit()
            flash(f'Employee {name} added successfully!', 'success')
            return redirect(url_for('admin_employees'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Add employee error: {e}')
            flash('Failed to add employee. Please try again.', 'error')
            return render_template(
                'admin_employee_form.html',
                employee=None,
                next_id=staff_id,
                form_data=request.form
            )

    # Suggest the next Staff ID automatically (e.g. S001, S002...)
    last = Employee.query.order_by(Employee.id.desc()).first()
    if last:
        try:
            num = int(''.join(filter(str.isdigit, last.staff_id)))
            next_id = f'S{num + 1:03d}'
        except (ValueError, TypeError):
            next_id = 'S001'
    else:
        next_id = 'S001'

    return render_template(
        'admin_employee_form.html',
        employee=None,
        next_id=next_id,
        form_data={}
    )


@app.route('/admin/employees/edit/<staff_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_employee(staff_id):
    """Form to change an existing employee's details."""
    employee = Employee.query.filter_by(staff_id=staff_id).first_or_404()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        position = request.form.get('position', '').strip()
        email = request.form.get('email', '').strip().lower() or None
        hourly_rate_str = request.form.get('hourly_rate', str(employee.hourly_rate))
        is_active = request.form.get('is_active') == 'on'

        errors = []
        if not name:
            errors.append('Employee name is required.')
        try:
            hourly_rate = float(hourly_rate_str)
            if hourly_rate < 0:
                errors.append('Hourly rate must be non-negative.')
        except ValueError:
            errors.append('Invalid hourly rate.')
            hourly_rate = employee.hourly_rate

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template(
                'admin_employee_form.html',
                employee=employee,
                next_id=None,
                form_data=request.form
            )

        # Make sure we don't accidentally steal someone else's email
        if email:
            conflict = Employee.query.filter_by(email=email).first()
            if conflict and conflict.staff_id != staff_id:
                flash('Another employee already uses that email.', 'error')
                return render_template(
                    'admin_employee_form.html',
                    employee=employee,
                    next_id=None,
                    form_data=request.form
                )

        try:
            employee.name = name
            employee.position = position
            employee.email = email
            employee.hourly_rate = hourly_rate
            employee.is_active = is_active
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('admin_employees'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Edit employee error: {e}')
            flash('Failed to update employee.', 'error')

    return render_template(
        'admin_employee_form.html',
        employee=employee,
        next_id=None,
        form_data={}
    )


@app.route('/admin/employees/delete/<staff_id>', methods=['POST'])
@login_required
def admin_delete_employee(staff_id):
    """Remove an employee from the system."""
    employee = Employee.query.filter_by(staff_id=staff_id).first_or_404()
    try:
        name = employee.name
        db.session.delete(employee)
        db.session.commit()
        flash(f'Employee {name} deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Delete employee error: {e}')
        flash('Failed to delete employee.', 'error')
    return redirect(url_for('admin_employees'))


@app.route('/admin/records')
@login_required
def admin_records():
    """Show a table of all time records, with filters."""
    staff_id = request.args.get('staff_id', '').strip() or None
    status = request.args.get('status', '').strip() or None
    date_from_str = request.args.get('date_from', '').strip() or None
    date_to_str = request.args.get('date_to', '').strip() or None

    query = TimeRecord.query

    if staff_id:
        query = query.filter_by(staff_id=staff_id)
    if status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'approved':
        query = query.filter_by(is_approved=True)

    date_from = None
    date_to = None

    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            query = query.filter(TimeRecord.date >= date_from)
        except ValueError:
            flash('Invalid "from" date format.', 'warning')

    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            query = query.filter(TimeRecord.date <= date_to)
        except ValueError:
            flash('Invalid "to" date format.', 'warning')

    records = query.order_by(TimeRecord.date.desc()).limit(200).all()
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()

    return render_template(
        'admin_records.html',
        records=records,
        employees=employees,
        selected_staff_id=staff_id,
        selected_status=status,
        date_from=date_from_str,
        date_to=date_to_str
    )


@app.route('/admin/records/approve/<int:record_id>', methods=['POST'])
@login_required
def admin_approve_record(record_id):
    """Approve a finished shift and send the PDF email to the employee."""
    record = TimeRecord.query.get_or_404(record_id)

    if not record.clock_out_time:
        flash('Cannot approve a record without a clock-out time.', 'error')
        return redirect(url_for('admin_records'))

    try:
        pdf_path = generate_timesheet_pdf(record)
        record.is_approved = True
        record.approved_by = current_user.id
        record.approved_at = datetime.utcnow()
        if pdf_path:
            record.pdf_generated = True

        db.session.commit()

        if pdf_path:
            email_sent, email_msg = send_timesheet_email(record, pdf_path)
            if email_sent:
                flash('Record approved and timesheet emailed!', 'success')
            else:
                flash(f'Approved, but email failed: {email_msg}', 'warning')
        else:
            flash('Record approved (PDF generation unavailable).', 'warning')

    except Exception as e:
        db.session.rollback()
        logger.error(f'Approve record error: {e}')
        flash('Failed to approve record.', 'error')

    return redirect(url_for('admin_records'))


@app.route('/admin/records/generate-pdf/<int:record_id>')
@login_required
def admin_generate_pdf(record_id):
    """Download a PDF receipt for any record (even if not approved yet)."""
    record = TimeRecord.query.get_or_404(record_id)

    if not record.clock_in_time:
        flash('Record has no clock-in time.', 'error')
        return redirect(url_for('admin_records'))

    pdf_path = generate_timesheet_pdf(record)
    if pdf_path and os.path.exists(pdf_path):
        record.pdf_generated = True
        db.session.commit()
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'timesheet_{record.staff_id}_{record.date}.pdf'
        )
    else:
        flash('Failed to generate PDF. Check server logs.', 'error')
        return redirect(url_for('admin_records'))


@app.route('/admin/records/delete/<int:record_id>', methods=['POST'])
@login_required
def admin_delete_record(record_id):
    """Remove a time record from the database."""
    record = TimeRecord.query.get_or_404(record_id)
    try:
        db.session.delete(record)
        db.session.commit()
        flash('Record deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Delete record error: {e}')
        flash('Failed to delete record.', 'error')
    return redirect(url_for('admin_records'))


@app.route('/admin/qr-codes')
@login_required
def admin_qr_codes():
    """Page that shows the QR codes and lets admin regenerate them."""
    clock_in_url = f'{NETWORK_URL}/clock-in'
    clock_out_url = f'{NETWORK_URL}/clock-out'
    today = datetime.now().strftime('%Y%m%d')
    clock_in_filename = f'clock_in_{today}.png'
    clock_out_filename = f'clock_out_{today}.png'

    ok_in = generate_qr_code(clock_in_url, clock_in_filename)
    ok_out = generate_qr_code(clock_out_url, clock_out_filename)

    if not ok_in or not ok_out:
        flash('QR code generation unavailable (qrcode library missing).', 'warning')

    return render_template(
        'admin_qr_codes.html',
        clock_in_qr=clock_in_filename,
        clock_out_qr=clock_out_filename,
        clock_in_url=clock_in_url,
        clock_out_url=clock_out_url,
        today=datetime.now().date()
    )


@app.route('/admin/email-settings', methods=['GET', 'POST'])
@login_required
def admin_email_settings():
    """Page where admin can change the email server settings."""
    if request.method == 'POST':
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        try:
            mail_port = int(request.form.get('mail_port', 587))
        except ValueError:
            flash('Invalid port number.', 'error')
            return redirect(url_for('admin_email_settings'))

        # Gather all the new settings into a dictionary
        settings = {
            'MAIL_SERVER': request.form.get('mail_server', 'smtp.gmail.com'),
            'MAIL_PORT': str(mail_port),
            'MAIL_USE_TLS': 'true' if request.form.get('mail_use_tls') else 'false',
            'MAIL_USE_SSL': 'true' if request.form.get('mail_use_ssl') else 'false',
            'MAIL_USERNAME': request.form.get('mail_username', ''),
            'MAIL_PASSWORD': request.form.get('mail_password', ''),
            'MAIL_DEFAULT_SENDER': request.form.get('mail_default_sender', ''),
        }
        try:
            with open(env_path, 'w') as f:
                for key, value in settings.items():
                    f.write(f'{key}={value}\n')
            # Update the running app with the new values
            app.config['MAIL_SERVER'] = settings['MAIL_SERVER']
            app.config['MAIL_PORT'] = mail_port
            app.config['MAIL_USE_TLS'] = settings['MAIL_USE_TLS'] == 'true'
            app.config['MAIL_USE_SSL'] = settings['MAIL_USE_SSL'] == 'true'
            app.config['MAIL_USERNAME'] = settings['MAIL_USERNAME']
            app.config['MAIL_PASSWORD'] = settings['MAIL_PASSWORD']
            app.config['MAIL_DEFAULT_SENDER'] = settings['MAIL_DEFAULT_SENDER']
            flash('Email settings saved!', 'success')
        except OSError as e:
            logger.error(f'Save email settings error: {e}')
            flash('Could not save settings to .env file.', 'error')

        return redirect(url_for('admin_email_settings'))

    current_settings = {
        'mail_server': app.config['MAIL_SERVER'],
        'mail_port': app.config['MAIL_PORT'],
        'mail_use_tls': app.config['MAIL_USE_TLS'],
        'mail_use_ssl': app.config['MAIL_USE_SSL'],
        'mail_username': app.config['MAIL_USERNAME'],
        'mail_default_sender': app.config['MAIL_DEFAULT_SENDER'],
    }
    return render_template('admin_email_settings.html', settings=current_settings)


@app.route('/admin/email-test', methods=['POST'])
@login_required
def admin_test_email():
    """Send a test email to make sure the settings are correct."""
    test_email = request.form.get('test_email', '').strip()
    if not test_email:
        flash('Please enter a test email address.', 'error')
        return redirect(url_for('admin_email_settings'))

    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
        msg['To'] = test_email
        msg['Subject'] = 'WorkTrace Email Test'
        msg.attach(MIMEText(
            'This is a test email from WorkTrace. Configuration is working!',
            'plain'
        ))

        server = smtplib.SMTP(
            app.config['MAIL_SERVER'], app.config['MAIL_PORT'], timeout=10
        )
        if app.config['MAIL_USE_TLS']:
            server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        flash(f'Test email sent to {test_email}!', 'success')
    except Exception as e:
        flash(f'Email test failed: {str(e)}', 'error')

    return redirect(url_for('admin_email_settings'))


@app.route('/admin/network-settings', methods=['GET', 'POST'])
@login_required
def admin_network_settings():
    """Page where admin can change the URL used in QR codes."""
    global NETWORK_URL, NETWORK_IP
    if request.method == 'POST':
        custom_url = request.form.get('network_url', '').strip()
        if custom_url:
            NETWORK_URL = custom_url
            NETWORK_IP = custom_url.replace('http://', '').replace('https://', '').split(':')[0]
            # Persist to .env file so it survives restarts
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            updated = False
            with open(env_path, 'w') as f:
                for line in env_lines:
                    if line.startswith('NETWORK_URL='):
                        f.write(f'NETWORK_URL={NETWORK_URL}\n')
                        updated = True
                    else:
                        f.write(line)
                if not updated:
                    f.write(f'NETWORK_URL={NETWORK_URL}\n')
            flash('Network URL updated! Regenerate QR codes for changes to take effect.', 'success')
        else:
            flash('Please provide a valid URL.', 'error')
        return redirect(url_for('admin_network_settings'))

    # Auto-detect current local IP for display
    detected_ip = get_local_ip()
    return render_template(
        'admin_network_settings.html',
        network_url=NETWORK_URL,
        network_ip=NETWORK_IP,
        detected_ip=detected_ip,
        host_urls=[
            f'http://127.0.0.1:5000',
            f'http://{detected_ip}:5000',
        ]
    )


# ------------------------------------------------------------------
# SECTION 12: API ENDPOINTS
# Simple JSON data endpoints, useful for testing or future apps.
# ------------------------------------------------------------------

@app.route('/api/health')
def health_check():
    """A quick check to see if the server is alive."""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/employees')
@login_required
def api_employees():
    """Return a JSON list of active employees."""
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    return jsonify([{
        'staff_id': e.staff_id,
        'name': e.name,
        'position': e.position,
        'hourly_rate': e.hourly_rate,
    } for e in employees])


# ------------------------------------------------------------------
# SECTION 13: DATABASE INITIALIZATION
# This runs once when the app starts to create tables and sample data.
# ------------------------------------------------------------------

def _migrate_db():
    """Apply lightweight schema migrations for SQLite.
    We check if a new column (rest_minutes) exists, and add it if missing."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    cols = [c['name'] for c in inspector.get_columns('time_record')]
    if 'rest_minutes' not in cols:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE time_record ADD COLUMN rest_minutes FLOAT DEFAULT 0.0"))
            conn.commit()
            logger.info("Migration: added rest_minutes column to time_record")


def init_db():
    """Create all tables and insert default data if the database is empty."""
    with app.app_context():
        db.create_all()          # Make the tables
        _migrate_db()            # Add any missing columns from older versions

        # Create a default admin account if there isn't one
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin created.")

        # Add some fake employees so the system isn't empty
        if Employee.query.count() == 0:
            samples = [
                Employee(staff_id='S001', name='John Smith',
                         position='Cashier', email='john@example.com', hourly_rate=15.00),
                Employee(staff_id='S002', name='Emily Davis',
                         position='Supervisor', email='emily@example.com', hourly_rate=18.00),
                Employee(staff_id='S003', name='Michael Brown',
                         position='Stock Clerk', email='michael@example.com', hourly_rate=16.50),
                Employee(staff_id='S004', name='Lisa Wilson',
                         position='Manager', email='lisa@example.com', hourly_rate=20.00),
            ]
            for emp in samples:
                db.session.add(emp)
            db.session.commit()
            logger.info("Sample employees created.")


# ------------------------------------------------------------------
# SECTION 14: START THE SERVER
# When we run "python app.py" directly, this block starts everything.
# ------------------------------------------------------------------

if __name__ == '__main__':
    # Make sure the folders for QR codes and PDFs exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)
    init_db()   # Create tables and default data

    logger.info('WorkTrace starting on http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
