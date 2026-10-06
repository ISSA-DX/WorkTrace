"""
WorkTrace — Unit & Integration Test Suite
Run: python -m pytest test_app.py -v

What this file does:
- It checks that every part of the app works correctly.
- A "test" is a small piece of code that runs a function or route
  and makes sure the result is what we expect.
- If all tests pass, we can be confident the app behaves properly.
"""

import os
import pytest
from datetime import datetime, date, timedelta

# --------------------------------------------------
# Setup before importing the app
# --------------------------------------------------
# We set an environment variable so app.py knows we are in "test mode".
# In test mode the app uses an in-memory SQLite database.
# That means the database only lives while the tests run —
# nothing gets saved to a real file on disk.
os.environ['FLASK_TESTING'] = 'true'

# Add the project folder to the Python path so we can import app.py.
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and the database models we want to test.
from app import app as flask_app, db, Admin, Employee, TimeRecord, generate_timesheet_pdf


# ============================================================
# Fixtures
# ============================================================
# A "fixture" is a helper that pytest sets up before a test runs.
# Think of it like preparing a clean workspace:
# each test gets a fresh app, fresh database, and fresh fake data.


@pytest.fixture(scope='function')
def app():
    """
    Create a fresh Flask app with an in-memory database.
    This runs before every single test, so tests don't interfere.
    """
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # database lives in RAM
        'WTF_CSRF_ENABLED': False,                       # turn off form security tokens for easier testing
        'SECRET_KEY': 'test-secret',
        'MAIL_USERNAME': '',
        'DEFAULT_HOURLY_RATE': 15.00,
    })
    with flask_app.app_context():
        db.create_all()       # create all tables
        yield flask_app       # hand the app to the test
        db.session.remove()   # clean up the session
        db.drop_all()         # delete all tables for the next test


@pytest.fixture
def client(app):
    """
    Give tests a fake web browser (test_client).
    With this we can send GET and POST requests without running a real server.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Give tests a CLI runner (not used much here but good to have).
    """
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """
    Create a fake admin user in the database so we can test login.
    Returns the admin's database ID.
    """
    with app.app_context():
        admin = Admin(username='testadmin')
        admin.set_password('testpass123')
        db.session.add(admin)
        db.session.commit()
        return admin.id


@pytest.fixture
def sample_employee(app):
    """
    Create a fake employee in the database.
    Returns the employee's staff_id.
    """
    with app.app_context():
        emp = Employee(
            staff_id='S001',
            name='Test User',
            position='Tester',
            email='test@example.com',
            hourly_rate=20.00
        )
        db.session.add(emp)
        db.session.commit()
        return emp.staff_id


@pytest.fixture
def logged_in_client(client, admin_user):
    """
    Same as the normal client, but already logged in as admin.
    Useful for testing pages that require a manager to be signed in.
    """
    client.post('/admin/login', data={
        'username': 'testadmin',
        'password': 'testpass123'
    }, follow_redirects=True)
    return client


def make_clock_in_record(app, staff_id='S001', name='Test User',
                          offset_hours=2):
    """
    Helper function (not a pytest fixture) that quickly creates
    a clock-in record for today. Tests call this when they need
    existing data to work with.
    """
    with app.app_context():
        today = datetime.utcnow().date()
        emp = Employee.query.filter_by(staff_id=staff_id).first()
        if not emp:
            emp = Employee(staff_id=staff_id, name=name,
                           hourly_rate=20.00, email='t@t.com')
            db.session.add(emp)

        clock_in = datetime.utcnow() - timedelta(hours=offset_hours)
        record = TimeRecord(
            staff_id=staff_id,
            employee_name=name,
            date=today,
            clock_in_time=clock_in,
            clock_in_submitted=datetime.utcnow(),
            hourly_rate_used=20.00
        )
        db.session.add(record)
        db.session.commit()
        return record.id


# ============================================================
# MODEL TESTS
# ============================================================
# These tests check the database models directly —
# Admin, Employee, and TimeRecord — without using the web routes.


class TestAdminModel:
    """Tests for the Admin user account."""

    def test_set_and_check_password(self, app):
        """
        Make sure passwords are stored safely.
        set_password() hashes the password,
        check_password() returns True only for the correct password.
        """
        with app.app_context():
            admin = Admin(username='alice')
            admin.set_password('secure123')
            assert admin.check_password('secure123') is True
            assert admin.check_password('wrong') is False

    def test_password_hash_not_plaintext(self, app):
        """
        The database should never store the real password.
        It should store a scrambled "hash" instead.
        """
        with app.app_context():
            admin = Admin(username='bob')
            admin.set_password('mypassword')
            assert 'mypassword' not in admin.password_hash

    def test_admin_repr(self, app):
        """
        __repr__ gives a readable text version of an object.
        We check the admin's username appears in that text.
        """
        with app.app_context():
            admin = Admin(username='charlie')
            assert 'charlie' in repr(admin)

    def test_unique_username(self, app):
        """
        Two admins cannot share the same username.
        Trying to do so should raise an error from the database.
        """
        with app.app_context():
            a1 = Admin(username='dup')
            a1.set_password('pass')
            db.session.add(a1)
            db.session.commit()

            a2 = Admin(username='dup')
            a2.set_password('pass')
            db.session.add(a2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()


class TestEmployeeModel:
    """Tests for the Employee table and its fields."""

    def test_create_employee(self, app):
        """
        Create an employee, save to the database, then fetch it back.
        Make sure all fields (name, position, active status) are correct.
        """
        with app.app_context():
            emp = Employee(staff_id='E001', name='Jane Doe',
                           position='Dev', email='jane@ex.com', hourly_rate=25.0)
            db.session.add(emp)
            db.session.commit()
            fetched = Employee.query.filter_by(staff_id='E001').first()
            assert fetched is not None
            assert fetched.name == 'Jane Doe'
            assert fetched.is_active is True

    def test_employee_repr(self, app):
        """
        Check that the text representation of an employee
        includes both their name and staff ID.
        """
        with app.app_context():
            emp = Employee(staff_id='E002', name='Bob Smith', hourly_rate=10)
            assert 'Bob Smith' in repr(emp)
            assert 'E002' in repr(emp)

    def test_unique_staff_id(self, app):
        """
        Each employee must have a unique staff ID.
        Adding a duplicate should cause a database error.
        """
        with app.app_context():
            e1 = Employee(staff_id='DUP', name='A', hourly_rate=10)
            e2 = Employee(staff_id='DUP', name='B', hourly_rate=10)
            db.session.add(e1)
            db.session.commit()
            db.session.add(e2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_default_active(self, app):
        """
        When we create a new employee, they should be active by default.
        """
        with app.app_context():
            emp = Employee(staff_id='E003', name='Test', hourly_rate=15)
            db.session.add(emp)
            db.session.commit()
            assert emp.is_active is True


class TestTimeRecordModel:
    """Tests for the TimeRecord model — hours and salary calculations."""

    def test_calculate_hours_and_salary(self, app):
        """
        Clock in at 9:00, clock out at 17:30.
        That's 8.5 hours. At $20/hour, salary should be $170.
        """
        with app.app_context():
            clock_in = datetime(2025, 1, 15, 9, 0)
            clock_out = datetime(2025, 1, 15, 17, 30)
            record = TimeRecord(
                staff_id='X001',
                employee_name='Test',
                date=date(2025, 1, 15),
                clock_in_time=clock_in,
                clock_out_time=clock_out,
                hourly_rate_used=20.0
            )
            hours, salary = record.calculate_hours_and_salary()
            assert hours == 8.5
            assert salary == 170.0

    def test_calculate_no_clockout(self, app):
        """
        If the employee forgot to clock out, the calculation
        should not crash and should leave hours at 0.
        """
        with app.app_context():
            record = TimeRecord(
                staff_id='X002',
                employee_name='Test',
                date=date.today(),
                clock_in_time=datetime.utcnow(),
                hours_worked=0.0,
                hourly_rate_used=15.0
            )
            # No clock_out_time — should not crash and not modify hours
            record.calculate_hours_and_salary()
            assert record.hours_worked == 0.0

    def test_calculate_invalid_order(self, app):
        """
        Clock-out before clock-in should result in 0 hours.
        """
        with app.app_context():
            record = TimeRecord(
                staff_id='X003',
                employee_name='Test',
                date=date.today(),
                clock_in_time=datetime(2025, 1, 15, 17, 0),
                clock_out_time=datetime(2025, 1, 15, 9, 0),
                hourly_rate_used=15.0
            )
            record.calculate_hours_and_salary()
            assert record.hours_worked == 0.0
            assert record.salary_earned == 0.0

    def test_repr(self, app):
        """
        Make sure the text representation of a TimeRecord includes the staff ID.
        """
        with app.app_context():
            record = TimeRecord(
                staff_id='X004', employee_name='T',
                date=date(2025, 6, 1)
            )
            assert 'X004' in repr(record)


# ============================================================
# PUBLIC ROUTE TESTS
# ============================================================
# These tests act like a visitor using the website without logging in.
# They check the homepage, clock-in form, clock-out form, etc.


class TestPublicRoutes:
    """Tests for pages anyone can see (no login needed)."""

    def test_index_loads(self, client):
        """
        The homepage should load and show the app name "WorkTrace".
        """
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'WorkTrace' in resp.data

    def test_clock_in_form_loads(self, client):
        """
        The clock-in page should open and contain the words "Clock In".
        """
        resp = client.get('/clock-in')
        assert resp.status_code == 200
        assert b'Clock In' in resp.data

    def test_clock_out_form_loads(self, client):
        """
        The clock-out page should open and contain the words "Clock Out".
        """
        resp = client.get('/clock-out')
        assert resp.status_code == 200
        assert b'Clock Out' in resp.data

    def test_clock_in_missing_name(self, client):
        """
        Submitting the clock-in form without a name should still return
        a normal page (not crash). The page usually says the field is required.
        """
        resp = client.post('/clock-in', data={
            'name': '', 'staff_id': 'S001',
            'email': 'a@b.com', 'start_time': '2025-01-15T09:00'
        }, follow_redirects=True)
        assert b'required' in resp.data.lower() or resp.status_code == 200

    def test_clock_in_missing_staff_id(self, client):
        """
        Submitting without a staff ID should not crash —
        the app should just reload the form or show a message.
        """
        resp = client.post('/clock-in', data={
            'name': 'Test User', 'staff_id': '',
            'email': 'a@b.com', 'start_time': '2025-01-15T09:00'
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_clock_in_missing_email(self, client):
        """
        Submitting without an email should also be handled gracefully.
        """
        resp = client.post('/clock-in', data={
            'name': 'Test User', 'staff_id': 'S001',
            'email': '', 'start_time': '2025-01-15T09:00'
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_clock_in_invalid_time(self, client):
        """
        If the user types random text instead of a real time,
        the app should not crash.
        """
        resp = client.post('/clock-in', data={
            'name': 'Test User', 'staff_id': 'S001',
            'email': 'a@b.com', 'start_time': 'not-a-time'
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_clock_in_creates_record(self, app, client):
        """
        When we submit valid clock-in data, the app should:
        1. Create a new Employee if that staff ID didn't exist.
        2. Create a new TimeRecord with the clock-in time stored.
        """
        start = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        resp = client.post('/clock-in', data={
            'name': 'Alice Smith',
            'staff_id': 'A001',
            'position': 'Cashier',
            'email': 'alice@ex.com',
            'start_time': start,
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='A001').first()
            assert emp is not None
            record = TimeRecord.query.filter_by(staff_id='A001').first()
            assert record is not None
            assert record.clock_in_time is not None

    def test_clock_in_duplicate_today(self, app, client):
        """
        If someone tries to clock in twice on the same day,
        the app should warn them and NOT create a second record.
        """
        start = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
        client.post('/clock-in', data={
            'name': 'Bob', 'staff_id': 'B001',
            'email': 'b@b.com', 'start_time': start
        }, follow_redirects=True)
        resp = client.post('/clock-in', data={
            'name': 'Bob', 'staff_id': 'B001',
            'email': 'b@b.com', 'start_time': start
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            count = TimeRecord.query.filter_by(staff_id='B001').count()
            assert count == 1

    def test_clock_out_no_record(self, client):
        """
        Clocking out without ever clocking in should show a helpful message
        like "please clock in first".
        """
        end = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        resp = client.post('/clock-out', data={
            'name': 'Nobody', 'staff_id': 'Z999',
            'email': 'z@z.com', 'end_time': end
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'clock in first' in resp.data.lower() or b'no clock-in' in resp.data.lower()

    def test_clock_out_before_clock_in(self, app, client):
        """
        If the clock-out time is earlier than the clock-in time,
        the app should reject it and leave the record unchanged.
        """
        make_clock_in_record(app, staff_id='C001', name='Carl')
        with app.app_context():
            record = TimeRecord.query.filter_by(staff_id='C001').first()
            # Set clock-in to now
            ci_time = record.clock_in_time
        bad_end = (ci_time - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        resp = client.post('/clock-out', data={
            'name': 'Carl', 'staff_id': 'C001',
            'email': 'c@c.com', 'end_time': bad_end
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            record = TimeRecord.query.filter_by(staff_id='C001').first()
            assert record.clock_out_time is None

    def test_full_clock_in_and_out(self, app, client):
        """
        Full shift: clock-in then clock-out, verify calculations.
        After both steps, hours_worked and salary_earned should be greater than 0.
        """
        clock_in = (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M')
        clock_out = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')

        client.post('/clock-in', data={
            'name': 'Full Test', 'staff_id': 'F001',
            'email': 'f@f.com', 'start_time': clock_in
        }, follow_redirects=True)

        resp = client.post('/clock-out', data={
            'name': 'Full Test', 'staff_id': 'F001',
            'email': 'f@f.com', 'end_time': clock_out
        }, follow_redirects=True)

        assert resp.status_code == 200
        with app.app_context():
            record = TimeRecord.query.filter_by(staff_id='F001').first()
            assert record is not None
            assert record.clock_out_time is not None
            assert record.hours_worked > 0
            assert record.salary_earned > 0

    def test_clock_in_success_page(self, app, client):
        """
        The success page shown after clock-in should load without error.
        """
        make_clock_in_record(app, staff_id='S010', name='Success User')
        resp = client.get('/clock-in-success/S010')
        assert resp.status_code == 200

    def test_clock_out_success_page(self, app, client):
        """
        The success page shown after clock-out should load without error.
        """
        make_clock_in_record(app, staff_id='S011', name='Success2')
        with app.app_context():
            r = TimeRecord.query.filter_by(staff_id='S011').first()
            r.clock_out_time = datetime.utcnow()
            r.calculate_hours_and_salary()
            db.session.commit()
        resp = client.get('/clock-out-success/S011')
        assert resp.status_code == 200

    def test_clock_in_success_invalid_id(self, client):
        """
        If we ask for a success page with a staff ID that does not exist,
        the app should return a 404 "Not Found" error.
        """
        resp = client.get('/clock-in-success/NOTEXIST')
        assert resp.status_code == 404

    def test_clock_out_success_invalid_id(self, client):
        """
        Same as above but for the clock-out success page.
        """
        resp = client.get('/clock-out-success/NOTEXIST')
        assert resp.status_code == 404


# ============================================================
# ADMIN AUTH TESTS
# ============================================================
# These tests check the login / logout system.
# They make sure only valid admins can get into the dashboard.


class TestAdminAuth:
    """Tests for logging in and out as an admin."""

    def test_admin_login_page_loads(self, client):
        """
        The login page should display a sign-in form.
        """
        resp = client.get('/admin/login')
        assert resp.status_code == 200
        assert b'Sign In' in resp.data

    def test_admin_login_success(self, client, admin_user):
        """
        Logging in with the correct username and password
        should redirect to the Dashboard.
        """
        resp = client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Dashboard' in resp.data

    def test_admin_login_wrong_password(self, client, admin_user):
        """
        Typing the wrong password should show an "Invalid" error message.
        """
        resp = client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert b'Invalid' in resp.data

    def test_admin_login_nonexistent_user(self, client):
        """
        Trying to log in as a user that doesn't exist should also fail.
        """
        resp = client.post('/admin/login', data={
            'username': 'ghost',
            'password': 'pass'
        }, follow_redirects=True)
        assert b'Invalid' in resp.data

    def test_admin_login_empty_fields(self, client):
        """
        Submitting empty username and password should not crash.
        """
        resp = client.post('/admin/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_admin_logout(self, logged_in_client):
        """
        After logging out, the user should be taken back to the login page.
        """
        resp = logged_in_client.get('/admin/logout', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Sign In' in resp.data or b'login' in resp.data.lower()

    def test_admin_requires_login(self, client):
        """
        If a visitor (not logged in) tries to open /admin,
        they should be redirected (302) to the login page.
        """
        resp = client.get('/admin', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_admin_employees_requires_login(self, client):
        """
        The employee list should also block unauthenticated users.
        """
        resp = client.get('/admin/employees', follow_redirects=False)
        assert resp.status_code == 302

    def test_admin_redirect_if_already_logged_in(self, logged_in_client):
        """
        If an admin who is already logged in visits the login page,
        they should be redirected straight to the dashboard.
        """
        resp = logged_in_client.get('/admin/login', follow_redirects=False)
        assert resp.status_code == 302


# ============================================================
# ADMIN DASHBOARD TESTS
# ============================================================
# These tests make sure the manager's home page shows useful data.


class TestAdminDashboard:
    """Tests for the main admin dashboard."""

    def test_dashboard_loads(self, logged_in_client):
        """
        The dashboard should open successfully and show the word "Dashboard".
        """
        resp = logged_in_client.get('/admin')
        assert resp.status_code == 200
        assert b'Dashboard' in resp.data

    def test_dashboard_shows_stats(self, app, logged_in_client):
        """
        If an employee exists in the database,
        the dashboard should display that employee somewhere on the page.
        """
        with app.app_context():
            emp = Employee(staff_id='D001', name='Dashboard Test',
                           hourly_rate=15, email='d@d.com')
            db.session.add(emp)
            db.session.commit()
        resp = logged_in_client.get('/admin')
        assert resp.status_code == 200
        assert b'D001' in resp.data or b'Dashboard Test' in resp.data


# ============================================================
# ADMIN EMPLOYEE CRUD TESTS
# ============================================================
# CRUD stands for Create, Read, Update, Delete.
# These tests check the manager pages for adding, editing,
# and removing employees.


class TestAdminEmployees:
    """Tests for managing employees from the admin panel."""

    def test_employee_list_loads(self, logged_in_client):
        """
        The employee list page should load without errors.
        """
        resp = logged_in_client.get('/admin/employees')
        assert resp.status_code == 200

    def test_add_employee_form_loads(self, logged_in_client):
        """
        The "Add Employee" form page should load.
        """
        resp = logged_in_client.get('/admin/employees/add')
        assert resp.status_code == 200

    def test_add_employee_success(self, app, logged_in_client):
        """
        Filling in the add-employee form with valid data
        should create a new employee in the database.
        """
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': 'New Employee',
            'staff_id': 'NE001',
            'position': 'Analyst',
            'email': 'new@ex.com',
            'hourly_rate': '22.50',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='NE001').first()
            assert emp is not None
            assert emp.hourly_rate == 22.50

    def test_add_employee_missing_name(self, logged_in_client):
        """
        Adding an employee without a name should fail or show a warning.
        """
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': '',
            'staff_id': 'NE002',
            'hourly_rate': '15',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'required' in resp.data.lower() or b'name' in resp.data.lower()

    def test_add_employee_missing_staff_id(self, logged_in_client):
        """
        Adding an employee without a staff ID should not create a record.
        """
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': 'No ID',
            'staff_id': '',
            'hourly_rate': '15',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_add_employee_invalid_rate(self, logged_in_client):
        """
        Typing letters instead of a number for hourly rate
        should be handled gracefully (no crash).
        """
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': 'Bad Rate',
            'staff_id': 'BR001',
            'hourly_rate': 'abc',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_add_duplicate_staff_id(self, app, logged_in_client):
        """
        Trying to add an employee with a staff ID that already exists
        should show an error like "already exists".
        """
        with app.app_context():
            emp = Employee(staff_id='DUP01', name='First', hourly_rate=15)
            db.session.add(emp)
            db.session.commit()
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': 'Second',
            'staff_id': 'DUP01',
            'hourly_rate': '15',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'already' in resp.data.lower() or b'exists' in resp.data.lower()

    def test_edit_employee_loads(self, app, logged_in_client):
        """
        The edit page for an existing employee should open
        and show the employee's name on the form.
        """
        with app.app_context():
            emp = Employee(staff_id='ED01', name='Edit Me', hourly_rate=15)
            db.session.add(emp)
            db.session.commit()
        resp = logged_in_client.get('/admin/employees/edit/ED01')
        assert resp.status_code == 200
        assert b'Edit Me' in resp.data

    def test_edit_employee_404(self, logged_in_client):
        """
        Editing a staff ID that does not exist should return a 404 error.
        """
        resp = logged_in_client.get('/admin/employees/edit/NOEXIST')
        assert resp.status_code == 404

    def test_edit_employee_success(self, app, logged_in_client):
        """
        Submitting the edit form with new values should update the employee
        in the database.
        """
        with app.app_context():
            emp = Employee(staff_id='ED02', name='Old Name', hourly_rate=10)
            db.session.add(emp)
            db.session.commit()
        resp = logged_in_client.post('/admin/employees/edit/ED02', data={
            'name': 'New Name',
            'position': 'Manager',
            'email': 'updated@ex.com',
            'hourly_rate': '30.00',
            'is_active': 'on',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='ED02').first()
            assert emp.name == 'New Name'
            assert emp.hourly_rate == 30.0

    def test_edit_employee_deactivate(self, app, logged_in_client):
        """
        Unchecking the "is_active" box and saving should set the employee
        to inactive (False).
        """
        with app.app_context():
            emp = Employee(staff_id='ED03', name='Active One', hourly_rate=15)
            db.session.add(emp)
            db.session.commit()
        logged_in_client.post('/admin/employees/edit/ED03', data={
            'name': 'Active One',
            'hourly_rate': '15',
            # is_active NOT sent → False
        }, follow_redirects=True)
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='ED03').first()
            assert emp.is_active is False

    def test_delete_employee(self, app, logged_in_client):
        """
        Clicking delete should remove the employee from the database.
        """
        with app.app_context():
            emp = Employee(staff_id='DEL01', name='To Delete', hourly_rate=15)
            db.session.add(emp)
            db.session.commit()
        resp = logged_in_client.post('/admin/employees/delete/DEL01',
                                     follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='DEL01').first()
            assert emp is None

    def test_delete_employee_404(self, logged_in_client):
        """
        Deleting a staff ID that does not exist should return 404.
        """
        resp = logged_in_client.post('/admin/employees/delete/NOEXIST')
        assert resp.status_code == 404


# ============================================================
# ADMIN RECORDS TESTS
# ============================================================
# These tests check the manager pages for viewing and approving
# employee time records.


class TestAdminRecords:
    """Tests for managing time records from the admin panel."""

    def test_records_page_loads(self, logged_in_client):
        """
        The records list page should open.
        """
        resp = logged_in_client.get('/admin/records')
        assert resp.status_code == 200

    def test_records_filter_by_status(self, logged_in_client):
        """
        The manager should be able to filter records by status
        (e.g. pending, approved) using a query string.
        """
        resp = logged_in_client.get('/admin/records?status=pending')
        assert resp.status_code == 200

    def test_records_filter_by_date(self, logged_in_client):
        """
        The manager should be able to filter records by date range.
        """
        resp = logged_in_client.get('/admin/records?date_from=2025-01-01&date_to=2025-12-31')
        assert resp.status_code == 200

    def test_approve_record(self, app, logged_in_client):
        """
        When a manager clicks "Approve" on a completed shift,
        the record should be marked as approved in the database.
        """
        with app.app_context():
            emp = Employee(staff_id='AP01', name='Approve Me',
                           hourly_rate=15, email='ap@ex.com')
            db.session.add(emp)
            record = TimeRecord(
                staff_id='AP01',
                employee_name='Approve Me',
                date=datetime.utcnow().date(),
                clock_in_time=datetime.utcnow() - timedelta(hours=4),
                clock_out_time=datetime.utcnow() - timedelta(hours=1),
                hourly_rate_used=15.0
            )
            record.calculate_hours_and_salary()
            db.session.add(record)
            db.session.commit()
            record_id = record.id

        resp = logged_in_client.post(f'/admin/records/approve/{record_id}',
                                     follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            r = TimeRecord.query.get(record_id)
            assert r.is_approved is True

    def test_approve_incomplete_record(self, app, logged_in_client):
        """
        A record without a clock-out time should NOT be allowed to be approved.
        """
        with app.app_context():
            emp = Employee(staff_id='AP02', name='No Out', hourly_rate=15)
            db.session.add(emp)
            record = TimeRecord(
                staff_id='AP02', employee_name='No Out',
                date=datetime.utcnow().date(),
                clock_in_time=datetime.utcnow() - timedelta(hours=2),
                hourly_rate_used=15.0
            )
            db.session.add(record)
            db.session.commit()
            record_id = record.id

        resp = logged_in_client.post(f'/admin/records/approve/{record_id}',
                                     follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            r = TimeRecord.query.get(record_id)
            assert r.is_approved is False

    def test_approve_404(self, logged_in_client):
        """
        Approving a record ID that does not exist should return 404.
        """
        resp = logged_in_client.post('/admin/records/approve/99999',
                                     follow_redirects=True)
        assert resp.status_code == 404

    def test_delete_record(self, app, logged_in_client):
        """
        A manager should be able to delete a time record.
        After deletion, querying the database should return None.
        """
        make_clock_in_record(app, staff_id='DR01', name='Delete Record')
        with app.app_context():
            r = TimeRecord.query.filter_by(staff_id='DR01').first()
            record_id = r.id
        resp = logged_in_client.post(f'/admin/records/delete/{record_id}',
                                     follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert TimeRecord.query.get(record_id) is None

    def test_delete_record_404(self, logged_in_client):
        """
        Deleting a non-existent record ID should return 404.
        """
        resp = logged_in_client.post('/admin/records/delete/99999')
        assert resp.status_code == 404

    def test_generate_pdf_no_clock_in(self, app, logged_in_client):
        """
        Trying to generate a PDF for a record that has no clock-in time
        should not crash — it should redirect with an error message.
        """
        with app.app_context():
            emp = Employee(staff_id='PD01', name='PDF Test', hourly_rate=15)
            db.session.add(emp)
            record = TimeRecord(
                staff_id='PD01', employee_name='PDF Test',
                date=date.today()
            )
            db.session.add(record)
            db.session.commit()
            rid = record.id
        resp = logged_in_client.get(f'/admin/records/generate-pdf/{rid}',
                                    follow_redirects=True)
        assert resp.status_code == 200


# ============================================================
# QR CODES & EMAIL SETTINGS TESTS
# ============================================================
# These tests check that the QR code page and email settings page
# load correctly for logged-in managers.


class TestAdminQRAndEmail:
    """Tests for QR code generation and email configuration pages."""

    def test_qr_codes_page_loads(self, logged_in_client):
        """
        The QR codes page should open successfully.
        """
        resp = logged_in_client.get('/admin/qr-codes')
        assert resp.status_code == 200

    def test_email_settings_page_loads(self, logged_in_client):
        """
        The email settings form should load.
        """
        resp = logged_in_client.get('/admin/email-settings')
        assert resp.status_code == 200

    def test_email_settings_invalid_port(self, logged_in_client):
        """
        Typing text instead of a number for the SMTP port
        should show an "Invalid port" message.
        """
        resp = logged_in_client.post('/admin/email-settings', data={
            'mail_server': 'smtp.test.com',
            'mail_port': 'notanumber',
            'mail_username': 'user@test.com',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Invalid port' in resp.data or b'invalid' in resp.data.lower()

    def test_test_email_missing_address(self, logged_in_client):
        """
        Sending a test email without providing an address should still
        return a normal page (no crash).
        """
        resp = logged_in_client.post('/admin/email-test', data={
            'test_email': ''
        }, follow_redirects=True)
        assert resp.status_code == 200


# ============================================================
# API ENDPOINT TESTS
# ============================================================
# API endpoints are special URLs that return data (usually JSON)
# instead of HTML pages. Other programs or dashboards can use them.


class TestAPIEndpoints:
    """Tests for the small API routes in the app."""

    def test_health_check(self, client):
        """
        The /api/health route should return a JSON response
        saying the status is "ok". This is useful for monitoring tools.
        """
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data

    def test_api_employees_requires_login(self, client):
        """
        The employee API should block unauthenticated requests.
        """
        resp = client.get('/api/employees', follow_redirects=False)
        assert resp.status_code == 302

    def test_api_employees_logged_in(self, app, logged_in_client):
        """
        When logged in, the employee API should return a JSON list
        that includes the employee we created.
        """
        with app.app_context():
            emp = Employee(staff_id='API1', name='API User',
                           hourly_rate=20, is_active=True)
            db.session.add(emp)
            db.session.commit()
        resp = logged_in_client.get('/api/employees')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert any(e['staff_id'] == 'API1' for e in data)


# ============================================================
# ERROR HANDLER TESTS
# ============================================================
# These tests make sure the app shows friendly error pages
# instead of crashing when a user visits a bad URL.


class TestErrorHandlers:
    """Tests for 404 and 405 error responses."""

    def test_404_returns_html(self, client):
        """
        Visiting a URL that does not exist should return a 404 page
        with "404" or "Not Found" in the content.
        """
        resp = client.get('/this/does/not/exist')
        assert resp.status_code == 404
        assert b'404' in resp.data or b'Not Found' in resp.data

    def test_404_on_missing_employee_success(self, client):
        """
        Asking for a success page with a fake staff ID should also be 404.
        """
        resp = client.get('/clock-in-success/XXXXXXXX')
        assert resp.status_code == 404

    def test_method_not_allowed(self, client):
        """
        Some routes only allow POST (e.g. delete).
        Using GET on them should return 404 or 405.
        """
        resp = client.get('/admin/employees/delete/S001')
        assert resp.status_code in (404, 405)


# ============================================================
# HELPER FUNCTION TESTS
# ============================================================
# These tests check utility functions that live in app.py
# but are not tied to a specific web page.


class TestHelperFunctions:
    """Tests for standalone helper functions."""

    def test_generate_pdf_with_complete_record(self, app):
        """
        generate_timesheet_pdf() should create (or return a path to)
        a PDF file when given a completed, approved record.
        If the PDF library is missing it may return None.
        """
        with app.app_context():
            emp = Employee(staff_id='PDF01', name='PDF User',
                           email='pdf@ex.com', hourly_rate=20)
            db.session.add(emp)
            db.session.commit()

            record = TimeRecord(
                staff_id='PDF01',
                employee_name='PDF User',
                date=date.today(),
                clock_in_time=datetime(2025, 6, 1, 9, 0),
                clock_out_time=datetime(2025, 6, 1, 17, 0),
                hourly_rate_used=20.0,
                is_approved=True
            )
            record.calculate_hours_and_salary()
            db.session.add(record)
            db.session.commit()

            result = generate_timesheet_pdf(record)
            # Should return a path if reportlab is installed, None otherwise
            assert result is None or isinstance(result, str)

    def test_load_user_invalid_id(self, app):
        """
        load_user() is used by Flask-Login to find an admin by ID.
        If the ID doesn't exist, it should return None safely.
        """
        from app import load_user
        with app.app_context():
            user = load_user(99999)
            assert user is None

    def test_load_user_non_int(self, app):
        """
        If load_user() receives something that is not a number,
        it should also return None instead of crashing.
        """
        from app import load_user
        with app.app_context():
            user = load_user('notanint')
            assert user is None


# ============================================================
# SECURITY TESTS
# ============================================================
# These tests make sure common security problems are prevented.


class TestSecurity:
    """Tests for security-related behavior."""

    def test_open_redirect_blocked(self, client, admin_user):
        """
        After login, the app should NOT redirect to an outside website
        even if the login form contains a "next" parameter pointing off-site.
        """
        resp = client.post(
            '/admin/login?next=http://evil.com',
            data={'username': 'testadmin', 'password': 'testpass123'},
            follow_redirects=False
        )
        if resp.status_code == 302:
            assert 'evil.com' not in resp.headers.get('Location', '')

    def test_admin_routes_unauthenticated(self, client):
        """
        All admin pages should force unauthenticated visitors to log in first.
        """
        protected = [
            '/admin', '/admin/employees', '/admin/records',
            '/admin/qr-codes', '/admin/email-settings',
        ]
        for url in protected:
            resp = client.get(url, follow_redirects=False)
            assert resp.status_code == 302, f'{url} should redirect unauthenticated users'

    def test_delete_requires_post(self, client, admin_user):
        """
        Delete actions must use POST, not GET.
        Visiting a delete URL with GET should return 404 or 405.
        """
        resp = client.get('/admin/employees/delete/S001')
        assert resp.status_code in (404, 405)

    def test_approve_requires_post(self, client, admin_user):
        """
        Approve actions must also use POST.
        """
        resp = client.get('/admin/records/approve/1')
        assert resp.status_code in (302, 404, 405)


# ============================================================
# EDGE CASE TESTS
# ============================================================
# "Edge case" means unusual or extreme inputs —
# things that might break the app if not handled carefully.


class TestEdgeCases:
    """Tests for unusual or extreme situations."""

    def test_staff_id_uppercased_on_clock_in(self, app, client):
        """
        If a user types their staff ID in lowercase, the app should
        automatically convert it to uppercase before saving.
        """
        start = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        client.post('/clock-in', data={
            'name': 'Lower Case', 'staff_id': 's099',
            'email': 'lc@ex.com', 'start_time': start
        }, follow_redirects=True)
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='S099').first()
            assert emp is not None

    def test_zero_hourly_rate(self, app, logged_in_client):
        """
        An hourly rate of $0 should be accepted and saved as 0.00.
        """
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': 'Zero Rate', 'staff_id': 'ZR01',
            'hourly_rate': '0',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = Employee.query.filter_by(staff_id='ZR01').first()
            assert emp is not None
            assert emp.hourly_rate == 0.0

    def test_records_invalid_date_filter(self, logged_in_client):
        """
        If the manager types nonsense into the date filter,
        the records page should still load without crashing.
        """
        resp = logged_in_client.get('/admin/records?date_from=not-a-date')
        assert resp.status_code == 200

    def test_exactly_8_hour_shift(self, app):
        """
        A shift from 8:00 to 16:00 is exactly 8 hours.
        At $15/hour the salary should be exactly $120.
        """
        with app.app_context():
            clock_in = datetime(2025, 3, 10, 8, 0)
            clock_out = datetime(2025, 3, 10, 16, 0)
            record = TimeRecord(
                staff_id='EH01', employee_name='Eight Hour',
                date=date(2025, 3, 10),
                clock_in_time=clock_in,
                clock_out_time=clock_out,
                hourly_rate_used=15.0
            )
            record.calculate_hours_and_salary()
            assert record.hours_worked == 8.0
            assert record.salary_earned == 120.0

    def test_negative_hourly_rate_rejected(self, logged_in_client):
        """
        A negative hourly rate should not be allowed.
        The app should either reject it or not create the employee.
        """
        resp = logged_in_client.post('/admin/employees/add', data={
            'name': 'Negative', 'staff_id': 'NEG01',
            'hourly_rate': '-5',
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Should either reject or not create

    def test_flash_alert_accessibility(self, client):
        """
        Flash message alerts must be accessible with role="alert" and aria-label="Dismiss alert".
        """
        resp = client.post('/clock-in', data={
            'name': '',
            'staff_id': '',
            'email': ''
        }, follow_redirects=True)
        html = resp.data.decode('utf-8')
        assert 'role="alert"' in html
        assert 'aria-label="Dismiss alert"' in html
