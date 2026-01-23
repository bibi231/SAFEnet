
from app import app, db, User, ServiceProvider
from werkzeug.security import generate_password_hash
import os

with app.app_context():
    # Ensure tables exist
    db.create_all()

    # Check Admin
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@safenet.ng', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Created Admin: admin / admin123")
    else:
        # Reset admin password to be sure
        admin.set_password('admin123')
        print("Reset Admin Password: admin / admin123")
    
    # Check Provider
    provider_org = ServiceProvider.query.filter_by(name='Test Hospital').first()
    if not provider_org:
        provider_org = ServiceProvider(
            name='Test Hospital',
            category='Medical',
            address='123 Health St, Abuja',
            contact_phone='08012345678',
            contact_email='health@test.com',
            is_verified=True, 
            description='A test medical facility'
        )
        db.session.add(provider_org)
        db.session.commit() # Commit to get ID
    
    provider_user = User.query.filter_by(username='provider').first()
    if not provider_user:
        provider_user = User(
            username='provider',
            email='provider@test.com',
            role='provider',
            organization_id=provider_org.id
        )
        provider_user.set_password('provider123')
        db.session.add(provider_user)
        print("Created Provider: provider / provider123")
    else:
        provider_user.set_password('provider123')
        provider_user.organization_id = provider_org.id
        print("Reset Provider Password: provider / provider123")

    db.session.commit()
    print("Database setup complete.")
