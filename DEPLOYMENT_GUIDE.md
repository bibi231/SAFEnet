# SAFEnet - Comprehensive Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- PostgreSQL or MySQL (for production) or SQLite (for development)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/bibi231/safenet.git
cd safenet
```

2. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the root directory:
```bash
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///safenet.db
FLASK_ENV=development
ADMIN_PASSWORD=secure-admin-password-123
```

5. **Initialize the database:**
```bash
python app.py
```

6. **Run the application:**
```bash
flask run
# Or with gunicorn for production:
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔐 Security Improvements Implemented

### 1. Authentication & Authorization
- ✅ Password hashing with PBKDF2-SHA256
- ✅ Session management with secure cookies
- ✅ Role-based access control (Admin, Provider)
- ✅ CSRF protection on all forms
- ✅ Rate limiting on sensitive endpoints

### 2. Privacy & Anonymity
- ✅ No IP address logging (only hashed for abuse prevention)
- ✅ Anonymous tracking codes instead of user IDs
- ✅ No personal data collection in reports
- ✅ Secure report submission without authentication

### 3. Data Protection
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (Jinja2 auto-escaping)
- ✅ Input validation and sanitization
- ✅ Secure session configuration

### 4. Infrastructure Security
- ✅ Content Security Policy headers
- ✅ Secure cookie settings (HTTPOnly, SameSite)
- ✅ Rate limiting to prevent abuse
- ✅ System activity logging for auditing

## 📊 Database Optimizations

### Implemented Optimizations:
1. **Indexes** on frequently queried columns:
   - User: username, email
   - Report: tracking_code, status, location, submission_date
   - ServiceProvider: name, category, is_verified

2. **Connection Pooling:**
   - Pool size: 10 connections
   - Pool recycle: 3600 seconds
   - Pre-ping enabled for connection health checks

3. **Relationships:**
   - Lazy loading for related data
   - Cascade deletes for data integrity
   - Backref for bidirectional relationships

### Database Migration (Production):
```bash
# Install Flask-Migrate
pip install Flask-Migrate

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## 🏗️ Architecture Improvements

### Code Structure:
```
safenet/
├── app.py              # Main application file
├── backend.py          # Database models
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore file
├── frontend/
│   ├── templates/     # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── report.html
│   │   ├── track_report.html
│   │   ├── directory.html
│   │   ├── login.html
│   │   ├── register_provider.html
│   │   ├── admin_dashboard.html
│   │   ├── provider_dashboard.html
│   │   ├── about.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   └── 429.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── images/
├── instance/          # SQLite database (gitignored)
└── logs/             # Application logs (gitignored)
```

### Separation of Concerns:
- **backend.py**: All database models and business logic
- **app.py**: Routes, request handling, and view logic
- **Templates**: Presentation layer with Jinja2
- **Static files**: CSS, JavaScript, images

## 🚢 Production Deployment

### Option 1: Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t safenet .
docker run -p 5000:5000 --env-file .env safenet
```

### Option 2: Traditional Server (Ubuntu/Debian)

1. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql
```

2. **Set up PostgreSQL:**
```bash
sudo -u postgres createdb safenet
sudo -u postgres createuser safenet_user
```

3. **Configure Nginx as reverse proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

4. **Set up Systemd service:**
```ini
[Unit]
Description=SAFEnet Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/safenet
Environment="PATH=/var/www/safenet/venv/bin"
ExecStart=/var/www/safenet/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Enable and start service:**
```bash
sudo systemctl enable safenet
sudo systemctl start safenet
```

6. **Set up SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 3: Cloud Platforms

#### Heroku:
```bash
heroku create safenet-app
heroku addons:create heroku-postgresql:hobby-dev
git push heroku master
```

#### AWS Elastic Beanstalk:
```bash
eb init -p python-3.10 safenet
eb create safenet-env
eb deploy
```

#### DigitalOcean App Platform:
- Connect your GitHub repository
- Configure build command: `pip install -r requirements.txt`
- Configure run command: `gunicorn -w 4 app:app`

## ⚡ Performance Optimizations

### Implemented:
1. **Caching** (ready to implement):
   - Install Flask-Caching
   - Cache directory listings
   - Cache static dashboard stats

2. **Database Query Optimization:**
   - Use `db.session.query().options(joinedload())` for eager loading
   - Limit query results with pagination
   - Use indexes on foreign keys

3. **Asset Optimization:**
   - Minify CSS and JavaScript in production
   - Use CDN for static assets
   - Implement browser caching headers

4. **Asynchronous Tasks** (future enhancement):
   - Use Celery for email notifications
   - Background processing for reports
   - Scheduled cleanup tasks

## 🎨 UI/UX Improvements

### Modern Design:
- ✅ Responsive design (mobile-first)
- ✅ Consistent color scheme and branding
- ✅ Accessible (WCAG 2.1 Level AA)
- ✅ Loading states and error handling
- ✅ Clear call-to-action buttons

### User Experience:
- ✅ Simple, intuitive navigation
- ✅ Clear privacy information
- ✅ Real-time form validation
- ✅ Progress indicators
- ✅ Helpful error messages

## 🔍 Monitoring & Logging

### Application Logging:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/safenet.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SAFEnet startup')
```

### Metrics to Monitor:
- Request rate and response time
- Database query performance
- Error rates (4xx, 5xx)
- Report submission rate
- Active users

### Tools:
- **Application:** Flask-Monitoring-Dashboard
- **Infrastructure:** Prometheus + Grafana
- **Uptime:** UptimeRobot or Pingdom
- **Errors:** Sentry

## 🧪 Testing

### Unit Tests:
```python
# tests/test_models.py
import unittest
from app import app, db
from backend import User, Report, ServiceProvider

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='test', email='test@example.com', role='admin')
        u.set_password('password')
        self.assertFalse(u.check_password('wrongpassword'))
        self.assertTrue(u.check_password('password'))
```

### Run Tests:
```bash
python -m pytest tests/
```

## 📝 Environment Variables

Create a `.env` file with these variables:

```bash
# Flask Configuration
SECRET_KEY=your-very-long-random-secret-key
FLASK_ENV=production
FLASK_APP=app.py

# Database
DATABASE_URL=postgresql://user:password@localhost/safenet

# Admin Account
ADMIN_PASSWORD=secure-admin-password

# Email (for notifications - optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379
```

## 🔄 Backup & Recovery

### Database Backup:
```bash
# PostgreSQL
pg_dump safenet > backup_$(date +%Y%m%d).sql

# SQLite
sqlite3 instance/safenet.db ".backup 'backup.db'"
```

### Automated Backups:
```bash
# Add to crontab: 0 2 * * * (daily at 2 AM)
#!/bin/bash
BACKUP_DIR="/backups/safenet"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump safenet | gzip > $BACKUP_DIR/safenet_$DATE.sql.gz
find $BACKUP_DIR -mtime +30 -delete  # Delete backups older than 30 days
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OWASP Security Best Practices](https://owasp.org/)
- [Nigeria Data Protection Act 2023](https://ndpb.gov.ng/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues, please create a GitHub issue or contact: support@safenet.ng

## 🎯 Roadmap

### Phase 1 (Completed):
- ✅ Anonymous reporting system
- ✅ Service provider directory
- ✅ Admin dashboard
- ✅ Basic security implementation

### Phase 2 (In Progress):
- 🔄 Email notifications
- 🔄 SMS integration
- 🔄 Multi-language support (English, Hausa, Yoruba, Igbo)
- 🔄 Mobile app (React Native)

### Phase 3 (Planned):
- 📱 Real-time chat with providers
- 🗺️ Map integration for location-based services
- 📊 Analytics dashboard for administrators
- 🔔 Push notifications
- 🌍 Expansion to other Nigerian states
