from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for service providers and administrators"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='provider')  # admin, provider
    organization_id = db.Column(db.Integer, db.ForeignKey('service_providers.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    organization = db.relationship('ServiceProvider', backref='users', foreign_keys=[organization_id])
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ServiceProvider(db.Model):
    """Service provider organizations (NGOs, hospitals, legal aid, etc.)"""
    __tablename__ = 'service_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # NGO, Hospital, Legal Aid, Police, etc.
    address = db.Column(db.Text, nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False, index=True)
    verification_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    response_time_hours = db.Column(db.Integer, default=24)  # Average response time
    logo = db.Column(db.String(255), nullable=True)
    
    # Relationships
    assigned_reports = db.relationship('Report', backref='assigned_provider', lazy='dynamic',
                                      foreign_keys='Report.assigned_provider_id')
    
    def __repr__(self):
        return f'<ServiceProvider {self.name}>'


class Report(db.Model):
    """Anonymous incident reports"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    # Anonymous identifier for user to track report (not stored with personal info)
    tracking_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    
    # Report details
    category = db.Column(db.String(50), nullable=False, index=True)  # Assault, Theft, Medical Emergency, etc.
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False, index=True)
    incident_date = db.Column(db.DateTime, nullable=False, index=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)  # Pending, Assigned, In Progress, Resolved, Closed
    priority = db.Column(db.String(20), default='Medium', nullable=False, index=True)  # Low, Medium, High, Critical
    
    # Assignment
    assigned_provider_id = db.Column(db.Integer, db.ForeignKey('service_providers.id'), nullable=True, index=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    
    # Location Details
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Timestamps
    submission_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Privacy & Security
    ip_hash = db.Column(db.String(64), nullable=True)  # Hashed IP for abuse prevention (not for tracking)
    
    # Relationships
    aid_requests = db.relationship('AidRequest', backref='report', lazy='dynamic', cascade='all, delete-orphan')
    updates = db.relationship('ReportUpdate', backref='report', lazy='dynamic', cascade='all, delete-orphan',
                            order_by='ReportUpdate.created_at.desc()')
    attachments = db.relationship('ReportAttachment', backref='report', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)
        if not self.tracking_code:
            self.tracking_code = secrets.token_urlsafe(24)
    
    def __repr__(self):
        return f'<Report {self.tracking_code}>'


class ReportAttachment(db.Model):
    """Files attached to reports (images, videos)"""
    __tablename__ = 'report_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ReportAttachment {self.filename}>'


class ReportUpdate(db.Model):
    """Status updates for reports"""
    __tablename__ = 'report_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    created_by = db.relationship('User', backref='report_updates')
    
    def __repr__(self):
        return f'<ReportUpdate {self.id} for Report {self.report_id}>'


class AidRequest(db.Model):
    """Requests for specific types of aid/support"""
    __tablename__ = 'aid_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False, index=True)
    aid_type = db.Column(db.String(50), nullable=False, index=True)  # Medical, Legal, Shelter, Counseling, etc.
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)  # Pending, Assigned, Fulfilled, Declined
    urgency = db.Column(db.String(20), default='Normal', nullable=False)  # Normal, Urgent, Critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fulfilled_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<AidRequest {self.aid_type} for Report {self.report_id}>'


class VerificationRecord(db.Model):
    """Audit trail for service provider verifications"""
    __tablename__ = 'verification_records'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_providers.id'), nullable=False, index=True)
    verified_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verification_status = db.Column(db.String(20), nullable=False)  # Approved, Rejected, Pending
    verification_notes = db.Column(db.Text, nullable=True)
    documents_checked = db.Column(db.Text, nullable=True)  # JSON or comma-separated list
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    provider = db.relationship('ServiceProvider', backref='verification_records')
    verified_by = db.relationship('User', backref='verifications_performed')
    
    def __repr__(self):
        return f'<VerificationRecord {self.id} for Provider {self.provider_id}>'


class SystemLog(db.Model):
    """System activity logging for security and auditing"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)  # login, report_submitted, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_hash = db.Column(db.String(64), nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref='activity_logs')
    
    def __repr__(self):
        return f'<SystemLog {self.event_type} at {self.created_at}>'
