from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from backend import db, User, ServiceProvider, Report, AidRequest, VerificationRecord
import os

app = Flask(__name__)
app.template_folder = 'frontend/templates'
app.static_folder = 'frontend/static'
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safenet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register_provider.html')

@app.route('/register_provider', methods=['GET', 'POST'])
def register_provider():
    if request.method == 'POST':
        org_name = request.form.get('org_name')
        category = request.form.get('category')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')
        description = request.form.get('description')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register_provider'))

        # Create service provider organization
        provider = ServiceProvider(
            name=org_name,
            category=category,
            address=address,
            contact_phone=phone,
            contact_email=email,
            description=description,
            is_verified=False  # Requires admin verification
        )
        db.session.add(provider)
        db.session.commit()

        # Create admin user for the organization
        user = User(
            username=username,
            email=email,
            role='provider',
            organization_id=provider.id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration submitted successfully. Your organization will be verified by administrators within 24-48 hours.')
        return redirect(url_for('login'))

    return render_template('register_provider.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        reports = Report.query.order_by(Report.submission_date.desc()).limit(10).all()
        providers = ServiceProvider.query.all()
        total_reports = Report.query.count()
        pending_reports = Report.query.filter_by(status='Pending').count()
        verified_providers = ServiceProvider.query.filter_by(is_verified=True).count()
        return render_template('admin_dashboard.html', reports=reports, providers=providers,
                             total_reports=total_reports, pending_reports=pending_reports,
                             verified_providers=verified_providers)
    elif current_user.role == 'provider':
        assigned_reports = Report.query.filter_by(assigned_provider_id=current_user.organization_id).all() if current_user.organization_id else []
        pending_reports = [r for r in assigned_reports if r.status in ['Assigned', 'In Progress']]
        resolved_reports = [r for r in assigned_reports if r.status == 'Resolved']
        aid_requests = AidRequest.query.filter(AidRequest.report_id.in_([r.id for r in assigned_reports])).all()
        total_aid_requests = len(aid_requests)
        return render_template('provider_dashboard.html', assigned_reports=assigned_reports,
                             pending_reports=pending_reports, resolved_reports=resolved_reports,
                             aid_requests=aid_requests, total_aid_requests=total_aid_requests)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        category = request.form.get('category')
        description = request.form.get('description')
        location = request.form.get('location')
        incident_date = request.form.get('incident_date')
        report = Report(category=category, description=description, location=location, incident_date=incident_date)
        db.session.add(report)
        db.session.commit()
        flash('Report submitted successfully')
        return redirect(url_for('index'))
    return render_template('report.html')

@app.route('/directory')
def directory():
    providers = ServiceProvider.query.filter_by(is_verified=True).all()
    return render_template('directory.html', providers=providers)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
