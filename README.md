# 🛡️ SAFEnet - Secure Anonymous Feedback & Emergency Network

**SAFEnet** is a privacy-focused web platform for anonymous incident reporting and emergency response in Abuja, Nigeria. It connects victims with verified service providers (NGOs, hospitals, legal aid, police) while protecting their identity.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-3.0+-red)

## ✨ Features

### For Reporters (Anonymous Users)
- ✅ **Anonymous Reporting**: Submit incident reports without revealing identity
- ✅ **Tracking System**: Unique tracking codes to monitor report status
- ✅ **Privacy First**: No IP logging, no personal data collection
- ✅ **Multiple Categories**: Assault, theft, medical emergencies, domestic violence, and more
- ✅ **Service Directory**: Find verified support organizations

### For Service Providers
- ✅ **Dashboard**: Manage assigned reports and track progress
- ✅ **Status Updates**: Update report status and communicate with reporters
- ✅ **Verification System**: Admin verification before activation
- ✅ **Aid Requests**: Handle specific assistance requests

### For Administrators
- ✅ **Central Dashboard**: Overview of all reports and providers
- ✅ **Provider Verification**: Vet and approve service organizations
- ✅ **Report Assignment**: Assign reports to appropriate providers
- ✅ **System Monitoring**: Track platform usage and performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/bibi231/safenet.git
cd safenet
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database:**
```bash
python app.py
```

6. **Run the application:**
```bash
flask run
# Access at: http://localhost:5000
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `changeme123`
⚠️ **Change immediately after first login!**

## 📋 What's New in Version 2.0

### 🔐 Security Improvements
- Password hashing with PBKDF2-SHA256
- CSRF protection on all forms
- Rate limiting on sensitive endpoints
- Session security (HTTPOnly, SameSite cookies)
- IP address hashing (privacy-preserving abuse prevention)
- Content Security Policy headers
- System activity logging

### ⚡ Performance Optimizations
- Database connection pooling
- Query optimization with indexes
- Lazy loading for relationships
- Efficient cascade operations
- Prepared for caching implementation

### 🏗️ Code Structure
- Clean separation of concerns
- Modular backend (models separate from routes)
- Improved error handling
- Comprehensive logging
- Type hints and documentation

### 🎨 UI/UX Enhancements
- Modern, responsive design
- Mobile-first approach
- Consistent color scheme
- Accessible (WCAG 2.1 AA)
- Better user feedback
- Loading states and animations

### 🚢 Deployment Ready
- Docker support
- Docker Compose for full stack
- Production-ready configurations
- Environment-based settings
- Comprehensive deployment guide

## 📁 Project Structure

```
safenet/
├── app.py                      # Main application
├── backend.py                  # Database models
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Multi-container setup
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── DEPLOYMENT_GUIDE.md         # Detailed deployment instructions
├── frontend/
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html          # Base template
│   │   ├── index.html         # Homepage
│   │   ├── report.html        # Report form
│   │   ├── directory.html     # Provider directory
│   │   ├── login.html         # Login page
│   │   ├── register_provider.html  # Registration
│   │   ├── admin_dashboard.html    # Admin panel
│   │   ├── provider_dashboard.html # Provider panel
│   │   ├── about.html         # About page
│   │   └── error pages...     # 404, 500, 429
│   └── static/
│       ├── css/
│       │   └── style.css      # Main stylesheet
│       ├── js/
│       │   └── main.js        # Frontend JavaScript
│       └── images/            # Images and icons
└── instance/                   # SQLite database (gitignored)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example` for template):

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///safenet.db  # Or PostgreSQL URL
FLASK_ENV=development
ADMIN_PASSWORD=secure-password
```

### Database Options

**Development (SQLite):**
```bash
DATABASE_URL=sqlite:///safenet.db
```

**Production (PostgreSQL):**
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/safenet
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This starts:
- Web application (port 5000)
- PostgreSQL database
- Redis (for rate limiting)
- Nginx reverse proxy (port 80)

### Single Container:

```bash
docker build -t safenet .
docker run -p 5000:5000 --env-file .env safenet
```

## 📊 Database Schema

### Core Models:
- **User**: Service providers and administrators
- **ServiceProvider**: Organizations offering assistance
- **Report**: Anonymous incident reports
- **ReportUpdate**: Status updates for reports
- **AidRequest**: Specific assistance requests
- **VerificationRecord**: Provider verification audit trail
- **SystemLog**: Activity logging for security

### Key Relationships:
- Users belong to ServiceProviders
- Reports assigned to ServiceProviders
- Reports have multiple Updates and AidRequests
- ServiceProviders have VerificationRecords

## 🔒 Security Features

1. **Authentication & Authorization**
   - Password hashing (PBKDF2-SHA256)
   - Role-based access control
   - Session management
   - CSRF protection

2. **Privacy Protection**
   - No IP address logging
   - Anonymous tracking codes
   - No personal data in reports
   - Hashed IPs for abuse prevention only

3. **Application Security**
   - SQL injection protection (ORM)
   - XSS protection (template auto-escaping)
   - Rate limiting
   - Secure headers
   - Input validation

4. **Infrastructure Security**
   - Environment-based configuration
   - Secure cookie settings
   - HTTPS ready
   - Docker security best practices

## 📈 Performance Features

- Database connection pooling (10 connections)
- Query optimization with indexes
- Lazy loading for relationships
- Pagination for large datasets
- Ready for Redis caching
- Static file optimization

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📝 API Endpoints

### Public Routes:
- `GET /` - Homepage
- `GET /about` - About page
- `GET /report` - Report form
- `POST /report` - Submit report
- `GET /track/<code>` - Track report
- `GET /directory` - Service providers

### Authenticated Routes:
- `GET /dashboard` - User dashboard
- `POST /logout` - Logout

### Admin Routes:
- `POST /admin/verify_provider/<id>` - Verify provider
- `POST /admin/assign_report/<id>` - Assign report

### Provider Routes:
- `POST /provider/update_report/<id>` - Update report

### API Routes:
- `GET /api/stats` - Dashboard statistics (JSON)

## 🌍 Deployment Options

### 1. Traditional Server
See `DEPLOYMENT_GUIDE.md` for detailed instructions on:
- Ubuntu/Debian deployment
- Nginx configuration
- Systemd service setup
- SSL with Let's Encrypt
- PostgreSQL setup

### 2. Docker (Recommended)
```bash
docker-compose up -d
```

### 3. Cloud Platforms
- **Heroku**: Ready with Procfile
- **AWS Elastic Beanstalk**: Configuration included
- **DigitalOcean App Platform**: One-click deployment
- **Railway**: Direct GitHub integration

## 🔄 Backup & Maintenance

### Database Backup:
```bash
# PostgreSQL
pg_dump safenet > backup.sql

# SQLite
sqlite3 instance/safenet.db ".backup 'backup.db'"
```

### Automated Backups:
Add to crontab for daily backups at 2 AM:
```bash
0 2 * * * /path/to/backup-script.sh
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [API Documentation](#api-endpoints) - API reference
- [Security Guide](DEPLOYMENT_GUIDE.md#security-improvements-implemented) - Security best practices

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Styled with custom CSS inspired by Tailwind CSS
- Icons from [Font Awesome](https://fontawesome.com/) (optional)
- Compliant with [Nigeria Data Protection Act 2023](https://ndpb.gov.ng/)

## 📞 Support

- **Email**: support@safenet.ng
- **GitHub Issues**: [Create an issue](https://github.com/bibi231/safenet/issues)
- **Documentation**: See DEPLOYMENT_GUIDE.md

## 🗺️ Roadmap

### Current (v2.0)
- ✅ Anonymous reporting
- ✅ Provider dashboard
- ✅ Admin panel
- ✅ Service directory

### Upcoming (v2.1)
- 📧 Email notifications
- 📱 SMS integration
- 🌐 Multi-language support
- 📊 Analytics dashboard

### Future (v3.0)
- 📱 Mobile application
- 💬 Real-time chat
- 🗺️ Map integration
- 🔔 Push notifications
- 🌍 Multi-state expansion

## ⚠️ Important Notes

1. **Change default passwords** immediately after installation
2. **Use HTTPS** in production
3. **Regular backups** are essential
4. **Monitor logs** for security issues
5. **Update dependencies** regularly

## 🎯 Mission

SAFEnet aims to create a safer Abuja by providing a secure, anonymous platform for incident reporting and connecting victims with help. We believe everyone deserves access to emergency services and support, regardless of their circumstances.

---

**Built with ❤️ for Abuja, Nigeria**

*If you find SAFEnet helpful, please star ⭐ the repository!*
