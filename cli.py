#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkTrace CLI
QR-based Employee Time Tracking System — Command Line Interface

Run: python cli.py
"""

import os
import sys
from datetime import datetime, timedelta

# Force UTF-8 on Windows terminals so Rich and emojis render correctly
if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ------------------------------------------------------------------
# Import the existing Flask app, models, and helpers
# ------------------------------------------------------------------
import app as app_module
from app import (
    app, db, init_db, Admin, Employee, TimeRecord,
    generate_qr_code, generate_timesheet_pdf, send_timesheet_email,
    NETWORK_URL, get_local_ip, _safe_qr_folder, _safe_pdf_folder,
    QR_AVAILABLE, PDF_AVAILABLE, logger
)
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------------------------------------------
# Rich for beautiful terminal UI
# ------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, FloatPrompt
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

if RICH_AVAILABLE:
    console = Console()
else:
    # Minimal fallback console that mimics rich API
    class FallbackConsole:
        def print(self, text, **kwargs):
            print(text)
        def rule(self, title=""):
            print(f"\n{'=' * 40}\n{title}\n{'=' * 40}")
        def input(self, prompt_text, **kwargs):
            return input(prompt_text + " ")
    console = FallbackConsole()


def clear():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    """Wait for user to press Enter."""
    if RICH_AVAILABLE:
        console.input("\n[dim]Press Enter to continue...[/dim]")
    else:
        input("\nPress Enter to continue...")


def print_header(title):
    """Print a styled header."""
    if RICH_AVAILABLE:
        console.rule(f"[bold cyan]{title}[/bold cyan]")
    else:
        console.rule(title)


def print_success(msg):
    """Print a success message."""
    if RICH_AVAILABLE:
        console.print(f"[bold green]✓[/bold green] {msg}")
    else:
        print(f"✓ {msg}")


def print_error(msg):
    """Print an error message."""
    if RICH_AVAILABLE:
        console.print(f"[bold red]✗[/bold red] {msg}")
    else:
        print(f"✗ {msg}")


def print_warning(msg):
    """Print a warning message."""
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠[/bold yellow] {msg}")
    else:
        print(f"⚠ {msg}")


def print_info(msg):
    """Print an info message."""
    if RICH_AVAILABLE:
        console.print(f"[dim]ℹ {msg}[/dim]")
    else:
        print(f"ℹ {msg}")


def get_input(prompt_text, default=None):
    """Prompt for text input with optional default."""
    if RICH_AVAILABLE:
        val = console.input(f"[bold]{prompt_text}[/bold] ")
    else:
        val = input(f"{prompt_text} ")
    return val.strip() if val.strip() else default


def get_int_input(prompt_text, default=0):
    """Prompt for integer input."""
    if RICH_AVAILABLE:
        try:
            return IntPrompt.ask(f"[bold]{prompt_text}[/bold]", default=default)
        except Exception:
            return default
    else:
        try:
            return int(input(f"{prompt_text} ") or default)
        except ValueError:
            return default


def get_float_input(prompt_text, default=0.0):
    """Prompt for float input."""
    if RICH_AVAILABLE:
        try:
            return FloatPrompt.ask(f"[bold]{prompt_text}[/bold]", default=default)
        except Exception:
            return default
    else:
        try:
            return float(input(f"{prompt_text} ") or default)
        except ValueError:
            return default


def get_confirm(prompt_text):
    """Prompt for yes/no confirmation."""
    val = get_input(f"{prompt_text} (y/n):").lower()
    return val in ('y', 'yes')


def print_ascii_qr(url):
    """Print a QR code as ASCII art in the terminal."""
    if not QR_AVAILABLE:
        print_warning("qrcode library not installed. Install it to see QR codes.")
        print_info(f"URL: {url}")
        return
    import qrcode
    qr = qrcode.QRCode(version=3, box_size=1, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    if RICH_AVAILABLE:
        console.print("\n[bold]Scan this QR code with your phone:[/bold]")
    else:
        print("\nScan this QR code with your phone:")
    qr.print_ascii(invert=True)
    print_info(f"URL encoded: {url}")


def generate_qr_image(url, filename):
    """Generate a QR code image file and return its path."""
    if not QR_AVAILABLE:
        return None
    folder = _safe_qr_folder()
    filepath = os.path.join(folder, filename)
    import qrcode
    qr = qrcode.QRCode(version=3, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(filepath)
    return filepath


# =====================================================================
# EMPLOYEE FUNCTIONS
# =====================================================================

def clock_in():
    """Handle employee clock-in via CLI."""
    print_header("CLOCK IN")

    staff_id = get_input("Staff ID (e.g. S001):").upper()
    if not staff_id:
        print_error("Staff ID is required.")
        return

    with app.app_context():
        employee = Employee.query.filter_by(staff_id=staff_id).first()

        if not employee:
            print_warning(f"No employee found with Staff ID {staff_id}.")
            if not get_confirm("Register as a new employee?"):
                return
            name = get_input("Full Name:")
            position = get_input("Position (optional):") or None
            email = get_input("Email Address:")
            hourly_rate = get_float_input("Hourly Rate ($)", default=app.config.get('DEFAULT_HOURLY_RATE', 15.00))
            if not name or not email:
                print_error("Name and email are required.")
                return
            employee = Employee(
                staff_id=staff_id, name=name, position=position,
                email=email, hourly_rate=hourly_rate
            )
            db.session.add(employee)
            db.session.commit()
            print_success(f"Employee {name} registered.")

        today = datetime.utcnow().date()
        existing = TimeRecord.query.filter_by(staff_id=staff_id, date=today).first()
        if existing and existing.clock_in_time:
            print_warning(
                f"{employee.name}, you already clocked in today at "
                f"{existing.clock_in_time.strftime('%I:%M %p')}."
            )
            return

        # Default to current time, allow override
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M')
        start_time_str = get_input(f"Start Time [default: {now_str}]:")
        if not start_time_str:
            start_time_str = now_str

        try:
            clock_in_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            print_error("Invalid time format. Use YYYY-MM-DDTHH:MM")
            return

        record = TimeRecord(
            staff_id=staff_id,
            employee_name=employee.name,
            position=employee.position,
            date=today,
            clock_in_time=clock_in_time,
            clock_in_submitted=datetime.utcnow(),
            hourly_rate_used=employee.hourly_rate
        )
        db.session.add(record)
        db.session.commit()

    print_success(
        f"{employee.name} clocked in at {clock_in_time.strftime('%I:%M %p')}!"
    )


def clock_out():
    """Handle employee clock-out via CLI."""
    print_header("CLOCK OUT")

    staff_id = get_input("Staff ID (e.g. S001):").upper()
    if not staff_id:
        print_error("Staff ID is required.")
        return

    with app.app_context():
        today = datetime.utcnow().date()
        record = TimeRecord.query.filter_by(staff_id=staff_id, date=today).first()

        if not record or not record.clock_in_time:
            print_error("No clock-in record found for today. Please clock in first.")
            return

        if record.clock_out_time:
            print_warning(
                f"You already clocked out today at "
                f"{record.clock_out_time.strftime('%I:%M %p')}."
            )
            return

        employee = Employee.query.filter_by(staff_id=staff_id).first()

        # Default to current time
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M')
        end_time_str = get_input(f"End Time [default: {now_str}]:")
        if not end_time_str:
            end_time_str = now_str

        try:
            clock_out_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            print_error("Invalid time format. Use YYYY-MM-DDTHH:MM")
            return

        if clock_out_time <= record.clock_in_time:
            print_error("Clock-out time must be after clock-in time.")
            return

        rest_minutes = get_float_input("Rest / Break Time (minutes) [default: 0]:", default=0.0)
        if rest_minutes < 0:
            print_error("Rest time cannot be negative.")
            return

        record.clock_out_time = clock_out_time
        record.clock_out_submitted = datetime.utcnow()
        record.rest_minutes = rest_minutes
        record.calculate_hours_and_salary()
        db.session.commit()

    print_success(
        f"Clocked out at {clock_out_time.strftime('%I:%M %p')}. "
        f"Hours: {record.hours_worked:.2f} | Earned: ${record.salary_earned:.2f}"
    )
    if rest_minutes > 0:
        print_info(f"Rest time deducted: {rest_minutes:.0f} minutes")


def view_my_records():
    """View personal time records."""
    print_header("MY RECORDS")

    staff_id = get_input("Staff ID:").upper()
    if not staff_id:
        print_error("Staff ID is required.")
        return

    with app.app_context():
        records = TimeRecord.query.filter_by(staff_id=staff_id).order_by(TimeRecord.date.desc()).limit(20).all()

    if not records:
        print_info("No records found.")
        return

    if RICH_AVAILABLE:
        table = Table(title=f"Time Records for {staff_id}", box=box.SIMPLE_HEAVY)
        table.add_column("Date", style="cyan")
        table.add_column("Clock In", style="green")
        table.add_column("Clock Out", style="red")
        table.add_column("Rest", style="yellow")
        table.add_column("Hours", style="magenta")
        table.add_column("Salary", style="bold green")
        table.add_column("Status", style="blue")

        for r in records:
            status = "Approved" if r.is_approved else ("Pending" if r.clock_out_time else "In Progress")
            table.add_row(
                r.date.strftime('%b %d, %Y'),
                r.clock_in_time.strftime('%I:%M %p') if r.clock_in_time else '—',
                r.clock_out_time.strftime('%I:%M %p') if r.clock_out_time else '—',
                f"{r.rest_minutes:.0f} min" if r.rest_minutes else '—',
                f"{r.hours_worked:.2f}" if r.clock_out_time else '—',
                f"${r.salary_earned:.2f}" if r.clock_out_time else '—',
                status
            )
        console.print(table)
    else:
        print(f"{'Date':<12} {'In':<10} {'Out':<10} {'Rest':<8} {'Hours':<8} {'Salary':<10} {'Status':<12}")
        print("-" * 70)
        for r in records:
            status = "Approved" if r.is_approved else ("Pending" if r.clock_out_time else "In Progress")
            print(
                f"{r.date.strftime('%b %d, %Y'):<12} "
                f"{r.clock_in_time.strftime('%I:%M %p') if r.clock_in_time else '—':<10} "
                f"{r.clock_out_time.strftime('%I:%M %p') if r.clock_out_time else '—':<10} "
                f"{(f'{r.rest_minutes:.0f} min' if r.rest_minutes else '—'):<8} "
                f"{(f'{r.hours_worked:.2f}' if r.clock_out_time else '—'):<8} "
                f"{(f'${r.salary_earned:.2f}' if r.clock_out_time else '—'):<10} "
                f"{status:<12}"
            )


# =====================================================================
# ADMIN FUNCTIONS
# =====================================================================

def admin_login():
    """Authenticate admin and return admin object or None."""
    print_header("ADMIN LOGIN")
    username = get_input("Username:")
    password = get_input("Password:")

    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            print_success(f"Welcome, {admin.username}!")
            return admin
    print_error("Invalid username or password.")
    return None


def admin_dashboard(admin):
    """Show admin dashboard with stats."""
    print_header("ADMIN DASHBOARD")

    with app.app_context():
        today = datetime.utcnow().date()
        total_employees = Employee.query.filter_by(is_active=True).count()
        today_records = TimeRecord.query.filter_by(date=today).all()
        clocked_in = sum(1 for r in today_records if r.clock_in_time and not r.clock_out_time)
        completed = sum(1 for r in today_records if r.clock_out_time)
        pending = sum(1 for r in today_records if r.clock_out_time and not r.is_approved)

    if RICH_AVAILABLE:
        console.print(Panel(
            f"[bold]Active Employees:[/bold] {total_employees}\n"
            f"[bold green]Clocked In Today:[/bold green] {clocked_in}\n"
            f"[bold blue]Completed Today:[/bold blue] {completed}\n"
            f"[bold yellow]Pending Approval:[/bold yellow] {pending}",
            title="Today's Overview", border_style="cyan"
        ))
    else:
        print(f"Active Employees: {total_employees}")
        print(f"Clocked In Today: {clocked_in}")
        print(f"Completed Today: {completed}")
        print(f"Pending Approval: {pending}")


def admin_view_records(admin):
    """View and filter all time records."""
    print_header("ALL TIME RECORDS")

    staff_id = get_input("Filter by Staff ID (or leave blank for all):").upper() or None
    status_filter = get_input("Filter by status (pending/approved/all) [default: all]:").lower() or "all"

    with app.app_context():
        query = TimeRecord.query
        if staff_id:
            query = query.filter_by(staff_id=staff_id)
        if status_filter == "pending":
            query = query.filter_by(is_approved=False)
        elif status_filter == "approved":
            query = query.filter_by(is_approved=True)
        records = query.order_by(TimeRecord.date.desc()).limit(50).all()

    if not records:
        print_info("No records found.")
        return

    if RICH_AVAILABLE:
        table = Table(title="Time Records", box=box.SIMPLE_HEAVY)
        table.add_column("ID", style="dim", width=4)
        table.add_column("Date", style="cyan")
        table.add_column("Employee", style="bold")
        table.add_column("Staff ID", style="dim")
        table.add_column("Clock In", style="green")
        table.add_column("Clock Out", style="red")
        table.add_column("Rest", style="yellow")
        table.add_column("Hours", style="magenta")
        table.add_column("Salary", style="bold green")
        table.add_column("Status", style="blue")

        for r in records:
            status = "Approved" if r.is_approved else ("Pending" if r.clock_out_time else "In Progress")
            table.add_row(
                str(r.id),
                r.date.strftime('%b %d, %Y'),
                r.employee_name,
                r.staff_id,
                r.clock_in_time.strftime('%I:%M %p') if r.clock_in_time else '—',
                r.clock_out_time.strftime('%I:%M %p') if r.clock_out_time else '—',
                f"{r.rest_minutes:.0f} min" if r.rest_minutes else '—',
                f"{r.hours_worked:.2f}" if r.clock_out_time else '—',
                f"${r.salary_earned:.2f}" if r.clock_out_time else '—',
                status
            )
        console.print(table)
    else:
        print(f"{'ID':<4} {'Date':<12} {'Employee':<15} {'Staff':<8} {'In':<10} {'Out':<10} {'Rest':<8} {'Hours':<8} {'Salary':<10} {'Status':<12}")
        print("-" * 100)
        for r in records:
            status = "Approved" if r.is_approved else ("Pending" if r.clock_out_time else "In Progress")
            print(
                f"{r.id:<4} "
                f"{r.date.strftime('%b %d, %Y'):<12} "
                f"{r.employee_name:<15} "
                f"{r.staff_id:<8} "
                f"{r.clock_in_time.strftime('%I:%M %p') if r.clock_in_time else '—':<10} "
                f"{r.clock_out_time.strftime('%I:%M %p') if r.clock_out_time else '—':<10} "
                f"{(f'{r.rest_minutes:.0f} min' if r.rest_minutes else '—'):<8} "
                f"{(f'{r.hours_worked:.2f}' if r.clock_out_time else '—'):<8} "
                f"{(f'${r.salary_earned:.2f}' if r.clock_out_time else '—'):<10} "
                f"{status:<12}"
            )


def admin_approve_record(admin):
    """Approve a pending record and optionally send email."""
    print_header("APPROVE RECORD")

    record_id = get_int_input("Enter Record ID to approve:")
    if not record_id:
        return

    with app.app_context():
        record = TimeRecord.query.get(record_id)
        if not record:
            print_error("Record not found.")
            return
        if not record.clock_out_time:
            print_error("Cannot approve a record without a clock-out time.")
            return
        if record.is_approved:
            print_warning("Record is already approved.")
            return

        # Preview record
        if RICH_AVAILABLE:
            console.print(Panel(
                f"Employee: [bold]{record.employee_name}[/bold] ({record.staff_id})\n"
                f"Date: {record.date.strftime('%B %d, %Y')}\n"
                f"Clock In: {record.clock_in_time.strftime('%I:%M %p') if record.clock_in_time else 'N/A'}\n"
                f"Clock Out: {record.clock_out_time.strftime('%I:%M %p') if record.clock_out_time else 'N/A'}\n"
                f"Rest: {record.rest_minutes or 0:.0f} min\n"
                f"Hours: {record.hours_worked:.2f}\n"
                f"Salary: ${record.salary_earned:.2f}",
                title=f"Record #{record.id}", border_style="cyan"
            ))
        else:
            print(f"Employee: {record.employee_name} ({record.staff_id})")
            print(f"Date: {record.date.strftime('%B %d, %Y')}")
            print(f"Hours: {record.hours_worked:.2f} | Salary: ${record.salary_earned:.2f}")

        if not get_confirm("Approve this record?"):
            return

        pdf_path = generate_timesheet_pdf(record)
        record.is_approved = True
        record.approved_by = admin.id
        record.approved_at = datetime.utcnow()
        if pdf_path:
            record.pdf_generated = True
        db.session.commit()

        print_success("Record approved!")

        if pdf_path:
            print_info(f"PDF saved to: {pdf_path}")
            if get_confirm("Send timesheet PDF via email to employee?"):
                sent, msg = send_timesheet_email(record, pdf_path)
                if sent:
                    print_success("Email sent successfully!")
                else:
                    print_warning(f"Email failed: {msg}")
        else:
            print_warning("PDF generation unavailable.")


def admin_manage_employees(admin):
    """Add, edit, list, or delete employees."""
    while True:
        print_header("MANAGE EMPLOYEES")
        print("1. List All Employees")
        print("2. Add New Employee")
        print("3. Edit Employee")
        print("4. Delete Employee")
        print("0. Back")

        choice = get_input("Choice:")

        if choice == "1":
            with app.app_context():
                employees = Employee.query.order_by(Employee.name).all()
            if RICH_AVAILABLE:
                table = Table(title="Employees", box=box.SIMPLE_HEAVY)
                table.add_column("Staff ID", style="cyan")
                table.add_column("Name", style="bold")
                table.add_column("Position", style="dim")
                table.add_column("Email", style="dim")
                table.add_column("Rate", style="green")
                table.add_column("Active", style="blue")
                for e in employees:
                    table.add_row(e.staff_id, e.name, e.position or '—', e.email or '—', f"${e.hourly_rate:.2f}", "Yes" if e.is_active else "No")
                console.print(table)
            else:
                print(f"{'Staff ID':<10} {'Name':<20} {'Position':<15} {'Email':<25} {'Rate':<8} {'Active':<8}")
                print("-" * 90)
                for e in employees:
                    print(f"{e.staff_id:<10} {e.name:<20} {(e.position or '—'):<15} {(e.email or '—'):<25} ${e.hourly_rate:<7.2f} {'Yes' if e.is_active else 'No':<8}")

        elif choice == "2":
            print_header("ADD EMPLOYEE")
            staff_id = get_input("Staff ID:").upper()
            name = get_input("Full Name:")
            position = get_input("Position (optional):") or None
            email = get_input("Email (optional):") or None
            hourly_rate = get_float_input("Hourly Rate ($)", default=app.config.get('DEFAULT_HOURLY_RATE', 15.00))

            if not staff_id or not name:
                print_error("Staff ID and Name are required.")
                continue

            with app.app_context():
                if Employee.query.filter_by(staff_id=staff_id).first():
                    print_error(f"Staff ID {staff_id} already exists.")
                    continue
                if email and Employee.query.filter_by(email=email).first():
                    print_error("An employee with that email already exists.")
                    continue
                emp = Employee(staff_id=staff_id, name=name, position=position, email=email, hourly_rate=hourly_rate)
                db.session.add(emp)
                db.session.commit()
            print_success(f"Employee {name} added!")

        elif choice == "3":
            print_header("EDIT EMPLOYEE")
            staff_id = get_input("Enter Staff ID to edit:").upper()
            with app.app_context():
                emp = Employee.query.filter_by(staff_id=staff_id).first()
                if not emp:
                    print_error("Employee not found.")
                    continue
                print_info(f"Editing: {emp.name}")
                emp.name = get_input(f"Name [{emp.name}]:") or emp.name
                emp.position = get_input(f"Position [{emp.position or ''}]:") or emp.position
                emp.email = get_input(f"Email [{emp.email or ''}]:") or emp.email
                new_rate = get_input(f"Hourly Rate [${emp.hourly_rate:.2f}]:")
                if new_rate:
                    try:
                        emp.hourly_rate = float(new_rate)
                    except ValueError:
                        print_error("Invalid rate.")
                emp.is_active = get_confirm("Is employee active?")
                db.session.commit()
            print_success("Employee updated.")

        elif choice == "4":
            print_header("DELETE EMPLOYEE")
            staff_id = get_input("Enter Staff ID to delete:").upper()
            with app.app_context():
                emp = Employee.query.filter_by(staff_id=staff_id).first()
                if not emp:
                    print_error("Employee not found.")
                    continue
                if not get_confirm(f"Delete {emp.name}? This cannot be undone."):
                    continue
                db.session.delete(emp)
                db.session.commit()
            print_success("Employee deleted.")

        elif choice == "0":
            break
        else:
            print_error("Invalid choice.")


def generate_qr_codes():
    """Generate and display QR codes for clock in/out."""
    print_header("GENERATE QR CODES")

    if not QR_AVAILABLE:
        print_error("qrcode library not installed. Run: pip install qrcode[pil]")
        return

    detected_ip = get_local_ip()
    current_url = NETWORK_URL

    print_info(f"Detected local IP: {detected_ip}")
    print_info(f"Current network URL: {current_url}")

    custom = get_input("Enter custom URL (or press Enter to use current):")
    base_url = custom.strip() if custom.strip() else current_url

    clock_in_url = f"{base_url}/clock-in"
    clock_out_url = f"{base_url}/clock-out"

    today = datetime.now().strftime('%Y%m%d')
    clock_in_file = f"clock_in_{today}.png"
    clock_out_file = f"clock_out_{today}.png"

    generate_qr_image(clock_in_url, clock_in_file)
    generate_qr_image(clock_out_url, clock_out_file)

    print_success("QR code images saved to static/qr_codes/")
    print("")
    print_info("=== CLOCK IN QR ===")
    print_ascii_qr(clock_in_url)
    print("")
    print_info("=== CLOCK OUT QR ===")
    print_ascii_qr(clock_out_url)


def admin_email_test():
    """Send a test email to verify configuration."""
    print_header("EMAIL TEST")

    test_email = get_input("Enter test email address:")
    if not test_email:
        print_error("Email address required.")
        return

    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

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
        print_success(f"Test email sent to {test_email}!")
    except Exception as e:
        print_error(f"Email test failed: {e}")


def settings_menu():
    """Configure email and network settings."""
    while True:
        print_header("SETTINGS")
        print("1. View Current Email Settings")
        print("2. Update Email Settings")
        print("3. View Network Settings")
        print("4. Update Network URL")
        print("0. Back")

        choice = get_input("Choice:")

        if choice == "1":
            print_info(f"Mail Server: {app.config['MAIL_SERVER']}")
            print_info(f"Mail Port: {app.config['MAIL_PORT']}")
            print_info(f"TLS: {app.config['MAIL_USE_TLS']}")
            print_info(f"Username: {app.config['MAIL_USERNAME'] or '(not set)'}")
            print_info(f"Default Sender: {app.config['MAIL_DEFAULT_SENDER'] or '(not set)'}")

        elif choice == "2":
            app.config['MAIL_SERVER'] = get_input(f"Mail Server [{app.config['MAIL_SERVER']}]:").strip() or app.config['MAIL_SERVER']
            try:
                port = int(get_input(f"Mail Port [{app.config['MAIL_PORT']}]:").strip() or app.config['MAIL_PORT'])
                app.config['MAIL_PORT'] = port
            except ValueError:
                print_error("Invalid port.")
            app.config['MAIL_USE_TLS'] = get_confirm("Use TLS?")
            app.config['MAIL_USERNAME'] = get_input(f"Username [{app.config['MAIL_USERNAME']}]:").strip() or app.config['MAIL_USERNAME']
            app.config['MAIL_PASSWORD'] = get_input("Password:").strip() or app.config['MAIL_PASSWORD']
            app.config['MAIL_DEFAULT_SENDER'] = get_input(f"Default Sender [{app.config['MAIL_DEFAULT_SENDER']}]:").strip() or app.config['MAIL_DEFAULT_SENDER']
            print_success("Email settings updated.")

        elif choice == "3":
            print_info(f"Current Network URL: {app_module.NETWORK_URL}")
            print_info(f"Detected Local IP: {get_local_ip()}")

        elif choice == "4":
            new_url = get_input(f"Network URL [{app_module.NETWORK_URL}]:").strip()
            if new_url:
                app_module.NETWORK_URL = new_url
                print_success(f"Network URL set to: {app_module.NETWORK_URL}")
                print_info("Regenerate QR codes for the change to take effect.")

        elif choice == "0":
            break
        else:
            print_error("Invalid choice.")


# =====================================================================
# MAIN MENU
# =====================================================================

def main():
    """Main entry point for the CLI."""
    # Ensure database and default admin exist
    with app.app_context():
        init_db()

    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold cyan]WorkTrace[/bold cyan] — QR-Based Employee Time Tracking\n"
            "[dim]Digitizing attendance for transparency and efficiency[/dim]",
            border_style="cyan"
        ))
    else:
        print("=" * 50)
        print("WorkTrace — QR-Based Employee Time Tracking")
        print("Digitizing attendance for transparency and efficiency")
        print("=" * 50)

    admin_user = None

    while True:
        print("")
        print_header("MAIN MENU")
        print("1. Clock In")
        print("2. Clock Out")
        print("3. View My Records")
        print("4. Generate QR Codes")
        print("5. Admin Login")
        if admin_user:
            print("6. Admin Dashboard")
            print("7. View All Records")
            print("8. Approve Record")
            print("9. Manage Employees")
            print("10. Email Test")
            print("11. Admin Logout")
        print("12. Settings")
        print("0. Exit")

        choice = get_input("Choice:")

        if choice == "1":
            clock_in()
            pause()
        elif choice == "2":
            clock_out()
            pause()
        elif choice == "3":
            view_my_records()
            pause()
        elif choice == "4":
            generate_qr_codes()
            pause()
        elif choice == "5":
            admin_user = admin_login()
            pause()
        elif choice == "6" and admin_user:
            admin_dashboard(admin_user)
            pause()
        elif choice == "7" and admin_user:
            admin_view_records(admin_user)
            pause()
        elif choice == "8" and admin_user:
            admin_approve_record(admin_user)
            pause()
        elif choice == "9" and admin_user:
            admin_manage_employees(admin_user)
        elif choice == "10" and admin_user:
            admin_email_test()
            pause()
        elif choice == "11":
            admin_user = None
            print_info("Logged out.")
            pause()
        elif choice == "12":
            settings_menu()
        elif choice == "0":
            if RICH_AVAILABLE:
                console.print("\n[bold cyan]Goodbye![/bold cyan]")
            else:
                print("\nGoodbye!")
            break
        else:
            print_error("Invalid choice.")
            pause()


if __name__ == '__main__':
    main()
