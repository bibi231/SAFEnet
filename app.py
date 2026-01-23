import os
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from backend import db, User, ServiceProvider, Report, AidRequest, VerificationRecord, ReportUpdate, SystemLog
import secrets

# Initialize Flask app
app = Flask(__name__)
app.template_folder = 'frontend/templates'
app.static_folder = 'frontend/static'

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///safenet.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
app.config['SESSION_COOKIE_SECURE'] = True  # Enable in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions
def hash_ip(ip_address):
    """Hash IP address for privacy-preserving abuse prevention"""
    return hashlib.sha256(ip_address.encode()).hexdigest()

def log_event(event_type, details=None, user_id=None):
    """Log system events for auditing"""
    try:
        ip_hash = hash_ip(request.remote_addr) if request.remote_addr else None
        log = SystemLog(
            event_type=event_type,
            user_id=user_id or (current_user.id if current_user.is_authenticated else None),
            ip_hash=ip_hash,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Failed to log event: {e}")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html', description=str(e.description)), 429

# Routes
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/login')
def login():
    """Redirect old login to provider login"""
    return redirect(url_for('provider_login'))

@app.route('/admin-login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    """Admin-specific login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('admin_login.html')
        
        user = User.query.filter_by(username=username, role='admin').first()
        
        if user and user.is_active and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_event('admin_login', f'Admin {username} logged in', user.id)
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            log_event('failed_admin_login', f'Failed admin login: {username}')
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin_login.html')

@app.route('/provider-login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def provider_login():
    """Provider-specific login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('provider_login.html')
        
        user = User.query.filter_by(username=username, role='provider').first()
        
        if user and user.is_active and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_event('provider_login', f'Provider {username} logged in', user.id)
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            log_event('failed_provider_login', f'Failed provider login: {username}')
            flash('Invalid provider credentials.', 'error')
    
    return render_template('provider_login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    log_event('user_logout', f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/register_provider', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register_provider():
    """Service provider registration"""
    if request.method == 'POST':
        # Get form data
        org_name = request.form.get('org_name', '').strip()
        category = request.form.get('category', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        description = request.form.get('description', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([org_name, category, address, phone, email, username, password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register_provider.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register_provider.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register_provider.html')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register_provider.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register_provider.html')

        try:
            # Create service provider organization
            provider = ServiceProvider(
                name=org_name,
                category=category,
                address=address,
                contact_phone=phone,
                contact_email=email,
                description=description,
                is_verified=False
            )
            db.session.add(provider)
            db.session.flush()  # Get provider.id

            # Create user account for the organization
            user = User(
                username=username,
                email=email,
                role='provider',
                organization_id=provider.id
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            log_event('provider_registration', f'New provider registered: {org_name}')
            flash('Registration submitted successfully! Your organization will be verified within 24-48 hours.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('register_provider.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard for authenticated users"""
    if current_user.role == 'admin':
        # Admin dashboard
        reports = Report.query.order_by(Report.submission_date.desc()).limit(20).all()
        providers = ServiceProvider.query.all()
        
        stats = {
            'total_reports': Report.query.count(),
            'pending_reports': Report.query.filter_by(status='Pending').count(),
            'active_reports': Report.query.filter(Report.status.in_(['Assigned', 'In Progress'])).count(),
            'resolved_reports': Report.query.filter_by(status='Resolved').count(),
            'total_providers': ServiceProvider.query.count(),
            'verified_providers': ServiceProvider.query.filter_by(is_verified=True).count(),
            'pending_verifications': ServiceProvider.query.filter_by(is_verified=False).count(),
        }
        
        return render_template('admin_dashboard.html', reports=reports, providers=providers, stats=stats)
    
    elif current_user.role == 'provider':
        # Provider dashboard
        if not current_user.organization_id:
            flash('Your account is not associated with an organization.', 'warning')
            return redirect(url_for('index'))
        
        organization = ServiceProvider.query.get(current_user.organization_id)
        assigned_reports = Report.query.filter_by(assigned_provider_id=current_user.organization_id).all()
        
        stats = {
            'total_assigned': len(assigned_reports),
            'pending': len([r for r in assigned_reports if r.status in ['Assigned', 'Pending']]),
            'in_progress': len([r for r in assigned_reports if r.status == 'In Progress']),
            'resolved': len([r for r in assigned_reports if r.status == 'Resolved']),
        }
        
        aid_requests = AidRequest.query.filter(
            AidRequest.report_id.in_([r.id for r in assigned_reports])
        ).all()
        
        return render_template('provider_dashboard.html',
                             organization=organization,
                             assigned_reports=assigned_reports,
                             stats=stats,
                             aid_requests=aid_requests)
    
    return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def report():
    """Anonymous incident reporting"""
    if request.method == 'POST':
        # Get form data
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        incident_date_str = request.form.get('incident_date', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Helper for allowed file extensions
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'pdf'}

        # Validation
        if not all([category, description, location, incident_date_str]):
            flash('Please fill in all required fields.', 'error')
            return render_template('report.html')

        try:
            incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d')
            
            # Create report
            report = Report(
                category=category,
                description=description,
                location=location,
                incident_date=incident_date,
                ip_hash=hash_ip(request.remote_addr) if request.remote_addr else None,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None
            )
            
            db.session.add(report)
            db.session.flush() # Get ID for attachments
            
            # Handle file uploads
            if 'attachments' in request.files:
                files = request.files.getlist('attachments')
                for file in files:
                    if file and allowed_file(file.filename):
                        from werkzeug.utils import secure_filename
                        import os
                        from backend import ReportAttachment
                        
                        original_filename = secure_filename(file.filename)
                        # Add timestamp to filename to prevent duplicates
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        filename = f"{timestamp}_{original_filename}"
                        
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        
                        attachment = ReportAttachment(
                            report_id=report.id,
                            filename=filename,
                            original_filename=original_filename,
                            file_type=filename.rsplit('.', 1)[1].lower(),
                            file_path=f"uploads/{filename}"
                        )
                        db.session.add(attachment)

            db.session.commit()

            log_event('report_submitted', f'Report submitted: {report.tracking_code}')
            
            flash(f'Report submitted successfully! Your tracking code is: {report.tracking_code}. Please save this code to check your report status.', 'success')
            return redirect(url_for('track_report', tracking_code=report.tracking_code))

        except ValueError:
            flash('Invalid date format.', 'error')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Report submission error: {e}")
            flash('An error occurred while submitting your report. Please try again.', 'error')

    return render_template('report.html')

@app.route('/track/<tracking_code>')
def track_report(tracking_code):
    """Track anonymous report by tracking code"""
    report = Report.query.filter_by(tracking_code=tracking_code).first_or_404()
    updates = report.updates.all()
    return render_template('track_report.html', report=report, updates=updates)

@app.route('/directory')
def directory():
    """Service provider directory"""
    category_filter = request.args.get('category', None)
    
    query = ServiceProvider.query.filter_by(is_verified=True)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    providers = query.order_by(ServiceProvider.rating.desc()).all()
    categories = db.session.query(ServiceProvider.category).filter_by(is_verified=True).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('directory.html', providers=providers, categories=categories, selected_category=category_filter)

# Admin routes
@app.route('/admin/verify_provider/<int:provider_id>', methods=['POST'])
@login_required
def verify_provider(provider_id):
    """Admin: Verify a service provider"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    
    provider = ServiceProvider.query.get_or_404(provider_id)
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'approve':
        provider.is_verified = True
        provider.verification_date = datetime.utcnow()
        status = 'Approved'
        flash(f'{provider.name} has been verified successfully.', 'success')
    elif action == 'reject':
        status = 'Rejected'
        flash(f'{provider.name} verification has been rejected.', 'warning')
    else:
        flash('Invalid action.', 'error')
        return redirect(url_for('dashboard'))
    
    # Create verification record
    verification = VerificationRecord(
        provider_id=provider_id,
        verified_by_user_id=current_user.id,
        verification_status=status,
        verification_notes=notes
    )
    db.session.add(verification)
    db.session.commit()
    
    log_event('provider_verification', f'Provider {provider.name} {status.lower()}', current_user.id)
    
    return redirect(url_for('dashboard'))

@app.route('/admin/assign_report/<int:report_id>', methods=['POST'])
@login_required
def assign_report(report_id):
    """Admin: Assign report to service provider"""
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    
    report = Report.query.get_or_404(report_id)
    provider_id = request.form.get('provider_id', type=int)
    
    if not provider_id:
        flash('Please select a service provider.', 'error')
        return redirect(url_for('dashboard'))
    
    provider = ServiceProvider.query.get_or_404(provider_id)
    
    if not provider.is_verified:
        flash('Cannot assign to unverified provider.', 'error')
        return redirect(url_for('dashboard'))
    
    report.assigned_provider_id = provider_id
    report.assigned_at = datetime.utcnow()
    report.status = 'Assigned'
    
    # Create update
    update = ReportUpdate(
        report_id=report_id,
        status='Assigned',
        message=f'Report assigned to {provider.name}',
        created_by_user_id=current_user.id
    )
    db.session.add(update)
    db.session.commit()
    
    log_event('report_assigned', f'Report {report.tracking_code} assigned to {provider.name}', current_user.id)
    flash(f'Report assigned to {provider.name} successfully.', 'success')
    
    return redirect(url_for('dashboard'))

# Provider routes
@app.route('/provider/update_report/<int:report_id>', methods=['POST'])
@login_required
def update_report(report_id):
    """Provider: Update report status"""
    if current_user.role != 'provider':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    
    report = Report.query.get_or_404(report_id)
    
    # Verify provider owns this report
    if report.assigned_provider_id != current_user.organization_id:
        flash('You do not have permission to update this report.', 'error')
        return redirect(url_for('dashboard'))
    
    new_status = request.form.get('status')
    message = request.form.get('message', '')
    
    valid_statuses = ['Assigned', 'In Progress', 'Resolved', 'Closed']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'error')
        return redirect(url_for('dashboard'))
    
    report.status = new_status
    if new_status == 'Resolved':
        report.resolved_at = datetime.utcnow()
    
    # Create update
    update = ReportUpdate(
        report_id=report_id,
        status=new_status,
        message=message or f'Status changed to {new_status}',
        created_by_user_id=current_user.id
    )
    db.session.add(update)
    db.session.commit()
    
    log_event('report_updated', f'Report {report.tracking_code} updated to {new_status}', current_user.id)
    flash('Report updated successfully.', 'success')
    
    return redirect(url_for('dashboard'))

    return redirect(url_for('dashboard'))

@app.route('/report_details/<int:report_id>')
@login_required
def report_details(report_id):
    """View full report details (Admin/Provider)"""
    report = Report.query.get_or_404(report_id)
    
    # Security check
    if current_user.role == 'provider':
        if report.assigned_provider_id != current_user.organization_id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('dashboard'))
    elif current_user.role != 'admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
        
    return render_template('report_details.html', report=report)

# API endpoints for AJAX requests
@app.route('/api/stats')
@login_required
def api_stats():
    """Get dashboard statistics"""
    if current_user.role == 'admin':
        stats = {
            'total_reports': Report.query.count(),
            'pending_reports': Report.query.filter_by(status='Pending').count(),
            'active_reports': Report.query.filter(Report.status.in_(['Assigned', 'In Progress'])).count(),
        }
    elif current_user.role == 'provider':
        assigned_reports = Report.query.filter_by(assigned_provider_id=current_user.organization_id).all()
        stats = {
            'total_assigned': len(assigned_reports),
            'pending': len([r for r in assigned_reports if r.status in ['Assigned', 'Pending']]),
        }
    else:
        stats = {}
    
    return jsonify(stats)

# Provider route alias for update_case
@app.route('/provider/update_case/<int:report_id>', methods=['POST'])
@login_required
def update_case(report_id):
    """Alias for update_report to match dashboard JS"""
    # Simply forward to update_report logic by calling it? 
    # Or just route it to the same function. 
    # We'll just define it as a wrapper.
    if request.json and 'status' in request.json:
        # If JSON request (from fetch)
        new_status = request.json.get('status')
        # We need to simulate form data or just use logic here.
        # Let's just reimplement the logic for JSON briefly or redirect?
        # Reimplementing concisely for JSON support which is what JS calls.
        
        report = Report.query.get_or_404(report_id)
        if report.assigned_provider_id != current_user.organization_id:
            return jsonify({'success': False, 'message': 'Unauthorized'})
            
        report.status = new_status
        if new_status == 'Resolved':
            report.resolved_at = datetime.utcnow()
            
        update = ReportUpdate(
            report_id=report_id,
            status=new_status,
            message=f'Status updated to {new_status}',
            created_by_user_id=current_user.id
        )
        db.session.add(update)
        db.session.commit()
        return jsonify({'success': True})
        
    return jsonify({'success': False, 'message': 'Invalid data'})


# Initialize database
def init_db():
    """Initialize database and create admin user if not exists"""
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@safenet.ng',
                role='admin'
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'changeme123'))
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created. Username: admin, Password: changeme123")
            print("IMPORTANT: Please change the admin password immediately!")

if __name__ == '__main__':
    init_db()
    app.run(debug=os.environ.get('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
