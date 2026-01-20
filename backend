from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model for Administrators and Service Providers.
    General users (victims) do NOT have accounts to ensure anonymity.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'provider'
    organization_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ServiceProvider(db.Model):
    """
    Verified Service Providers (NGOs, Hospitals, Police, etc.)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Medical', 'Legal', 'Security', 'Shelter'
    address = db.Column(db.String(200), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    users = db.relationship('User', backref='organization', lazy=True)

class Report(db.Model):
    """
    Anonymous Incident Reports.
    No PII is linked to a user account.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Pseudonymous token for tracking without identity
    tracking_id = db.Column(db.String(36), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False) # General location (e.g., Area/District in FCT)
    incident_date = db.Column(db.DateTime, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending') # Pending, Reviewed, Assigned, Closed
    assigned_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=True)
    assigned_provider = db.relationship('ServiceProvider', backref='assigned_reports', lazy=True)
    aid_requests = db.relationship('AidRequest', backref='report', lazy=True)
    
    # Encryption note: In a full production environment, 'description' and 'location' 
    # should be encrypted at the application level before storage.

class AidRequest(db.Model):
    """
    Requests for financial or material assistance linked to reports.
    """
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    aid_type = db.Column(db.String(50), nullable=False)  # e.g., 'Financial', 'Medical', 'Legal'
    amount_requested = db.Column(db.Float, nullable=True)  # For financial aid
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Provided
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    proof_of_assistance = db.Column(db.String(200), nullable=True)  # File path or URL for proof

class VerificationRecord(db.Model):
    """
    Records of verification processes for service providers.
    """
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    provider = db.relationship('ServiceProvider', backref='verification_records', lazy=True)
    verification_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verifier = db.relationship('User', backref='verifications', lazy=True)
    notes = db.Column(db.Text)
