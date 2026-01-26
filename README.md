# 🛡️ SAFEnet - Secure Anonymous Feedback & Emergency Network

**SAFEnet** is a privacy-focused web platform designed for anonymous incident reporting and emergency response. It connects victims and witnesses with verified service providers (NGOs, hospitals, legal aid, and security agencies) while strictly protecting their identity.

---

## 🚀 Quick Start Guide

### 📋 Prerequisites
Before you begin, ensure you have the following installed on your system:
- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Git**

---

### 💻 Installation

#### 1. Clone the Project
```bash
git clone https://github.com/bibi231/safenet.git
cd safenet
```

#### 2. Set Up a Virtual Environment (Recommended)
This keeps the project's dependencies separate from your system.

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### ⚙️ Configuration

1. **Create your environment file:**
   Copy the example file to a new file named `.env`.
   ```bash
   cp .env.example .env
   ```

2. **Configure the `.env` file:**
   Open `.env` in a text editor and update the following:
   - `SECRET_KEY`: Set this to a long, random string.
   - `ADMIN_PASSWORD`: Set a secure password for the initial admin account.
   - `DATABASE_URL`: Defaults to local SQLite (`sqlite:///safenet.db`).

---

### 🗄️ Database Initialization

The system will automatically create the database and a default administrator account the first time you run it.

```bash
python app.py
```
**Default Admin Credentials:**
- **Username:** `admin`
- **Password:** (Whatever you set in your `.env` file, or `changeme123` by default)

---

### 🏃 Running the Application

#### Development Mode
```bash
flask run
```
Access the site at: `http://localhost:5000`

#### Production Mode
For high performance and security, use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 👥 User Roles & Features

### 1. Anonymous Reporters
- **Report Incidents:** Submit reports without an account or personal data.
- **Tracking:** Receive a unique code to check status updates privately.
- **Attachments:** Securely upload images or evidence.

### 2. Service Providers (NGOs, Clinics, etc.)
- **Dashboard:** Manage assigned cases and requests for aid.
- **Updates:** Communicate progress to the reporter via status updates.
- **Directory:** Verified organizations appear in the public help directory.

### 3. Administrators
- **Verification:** Vet and approve new service providers.
- **Assignment:** Route incoming reports to the most appropriate provider.
- **System Monitoring:** View logs and platform statistics.

---

## 📁 Project Structure

```
safenet/
├── app.py              # Main Flask application
├── backend.py          # Database models & business logic
├── requirements.txt    # List of dependencies
├── .env                # Private configuration (DO NOT COMMIT)
├── scripts/            # Setup and utility scripts
├── archive/            # Legacy files and backups
├── frontend/           # UI elements
│   ├── templates/      # HTML pages
│   └── static/         # CSS, JS, and images
└── instance/           # Local database storage
```

---

## 🔐 Security & Privacy

- **No PI Collection:** We do not store real names, emails (for reporters), or phone numbers.
- **IP Hashing:** IP addresses are hashed for abuse prevention but cannot be traced back to the user.
- **Encrypted Passes:** All passwords are hashed using industry-standard PBKDF2-SHA256.
- **CSRF Protected:** All forms include protection against Cross-Site Request Forgery.

---

## 📞 Support & Maintenance

- **Backups:** Run `pg_dump` (PostgreSQL) or copy `instance/safenet.db` regularly.
- **Logs:** Check `error.log` and `output.log` if you encounter issues.
- **Help:** Contact `support@safenet.ng` or open an issue on GitHub.

---
**Built with ❤️ for a safer Abuja.**
