# TURING PLANET ✖️ TECHSUM Newsletter

⚡ **Your weekly TechSum**: the most noteworthy tech stories — quick and clear.

A modern newsletter subscription system with subscription management, email sending, and admin dashboard.

**🌐 Live URL**: [https://web-production-914f7.up.railway.app/](https://web-production-914f7.up.railway.app/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Pages](#-pages)
- [Quick Start](#-quick-start)
- [Deployment Guide](#-deployment-guide)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)

---

## ✨ Features

- 📧 **Newsletter Generation**: Fetch tech highlights from multiple sources and generate beautiful HTML newsletters
- 📬 **Email Sending**: Batch email sending via Gmail with MongoDB subscriber management
- 🌐 **Web Interface**: 
  - Subscribe page - User registration
  - Unsubscribe page - User opt-out
  - Admin dashboard - Subscriber management
- 💾 **MongoDB Integration**: Store and manage subscribers in MongoDB Atlas
- 🏷️ **Tag System**: Organize subscribers with tags (preview, user, etc.)
- 🛡️ **Anti-Spam**: Built-in honeypot mechanism to prevent bot registration
- 📊 **Real-time Statistics**: Admin dashboard displays subscriber statistics
- 🔐 **Admin Authentication**: Login system to protect admin panel
- ✉️ **Confirmation Email**: New subscribers automatically receive welcome confirmation emails
- 📁 **Newsletter Archive**: Each newsletter is automatically saved to `output/` folder with filename format `newsletter-YYYY-MM-DD.html`

---

## 📄 Pages

### 1. Subscribe Page

**URL**: 
- Production: [https://web-production-914f7.up.railway.app/](https://web-production-914f7.up.railway.app/)
- Local: `http://localhost:3000/`

**Features**:
- Users enter email address to subscribe
- Real-time form validation
- Anti-bot registration (honeypot mechanism)
- Responsive design, mobile-friendly
- **Automatic confirmation email**: After successful subscription, the system immediately sends a welcome email to new subscribers

**Highlights**:
- 🚀 AI-filtered from 30+ top publishers
- 🧭 Actionable summaries in minutes
- 🛡️ Private & secure — no sharing
- ✉️ Receive welcome confirmation email immediately after subscription

---

### 2. Unsubscribe Page

**URL**: 
- Production: [https://web-production-914f7.up.railway.app/unsubscribe.html](https://web-production-914f7.up.railway.app/unsubscribe.html)
- Local: `http://localhost:3000/unsubscribe.html`

**Features**:
- Users enter email to unsubscribe
- Optional reason selection (too frequent, not relevant, too long, other)
- Optional feedback
- Supports URL parameter to prefill email (`?email=xxx`)

**Unsubscribe Process**:
1. User enters email address
2. Select cancellation reason (optional)
3. Fill in additional feedback (optional)
4. Confirm unsubscribe
5. System sets subscriber status to `inactive`

---

### 3. Login Page

**URL**: 
- Production: [https://web-production-914f7.up.railway.app/login.html](https://web-production-914f7.up.railway.app/login.html)
- Local: `http://localhost:3000/login.html`

**Features**:
- Admin login authentication
- Username and password configured via environment variables
- Session management, login status maintained for 24 hours
- Unauthenticated users accessing admin page are automatically redirected to login page

**Configuration**:
Set in `.env` file:
```bash
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
SESSION_SECRET=your_session_secret_key
```

If not set, default username is `admin`, password is `admin123` (**for development only, must change in production**)

---

### 4. Admin Dashboard

**URL**: 
- Production: [https://web-production-914f7.up.railway.app/admin.html](https://web-production-914f7.up.railway.app/admin.html)
- Local: `http://localhost:3000/admin.html`

**Security**: 
- Requires login to access
- Unauthenticated users are automatically redirected to login page
- Supports logout functionality

**Features**:

#### 📊 Statistics Panel
- **Total Subscribers**: Shows total number of all subscribers
- **Active Subscribers**: Number of subscribers with `active` status
- **Inactive Subscribers**: Number of subscribers with `inactive` status

#### 🔍 Search and Filter
- **Email Search**: Real-time search by subscriber email
- **Status Filter**: Filter by `active` / `inactive`
- **Tag Filter**: Filter by `preview` / `user` tags

#### ✏️ Subscriber Management
- **Edit Tags**: 
  - Check/uncheck `preview` tag
  - Check/uncheck `user` tag
- **Update Status**: 
  - Set subscriber to `active` or `inactive`
- **Delete Subscriber**: Permanently delete subscriber record

#### 🔄 Auto Refresh
- Automatically refreshes data every 30 seconds
- Manual refresh button

**Use Cases**:
- Manage subscriber list
- Batch mark preview users
- Handle unsubscribe requests
- View subscriber statistics

---

## 🚀 Quick Start

### Requirements

- Node.js 18.x or higher
- npm >= 9.0.0
- Python 3.x (for newsletter generation and email sending)
- MongoDB Atlas account

### 1. Clone Repository

```bash
git clone <repository-url>
cd Techsum-newsletter
```

### 2. Install Dependencies

```bash
# Node.js dependencies (API server)
npm install

# Python dependencies (newsletter generation & sending)
pip install -r scripts/requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file (refer to `.env.example`):

```bash
# MongoDB Configuration
# Get connection string from MongoDB Atlas Dashboard
MONGODB_URI=your_mongodb_connection_string_here
MONGODB_DB=techsum
MONGODB_COLL=subscribers

# Gmail Configuration (for sending emails)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# TechSum API (optional, for fetching tech highlights)
TECHSUM_API_KEY=your-api-key

# Admin Authentication Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SESSION_SECRET=your_random_session_secret_key

# Server Configuration
PORT=3000
CORS_ORIGIN=*
```

**⚠️ Security Notes**: 
- Do not commit real credentials to Git repository
- All sensitive information should be stored in `.env` file (already in `.gitignore`)
- For production, configure in Railway environment variables, do not use default values

**How to Get Gmail App Password**:
1. Log in to Google account
2. Enable two-factor authentication
3. Visit [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate app-specific password

### 4. Start Local Server

```bash
npm run dev
# or
npm start
```

Server will start at `http://localhost:3000`:

- **Subscribe page**: http://localhost:3000/
- **Unsubscribe page**: http://localhost:3000/unsubscribe.html
- **Login page**: http://localhost:3000/login.html
- **Admin dashboard**: http://localhost:3000/admin.html (requires login)
- **Health check**: http://localhost:3000/api/health

### 5. Generate Newsletter

```bash
python scripts/api.py
```

This will generate `newsletter-YYYY-MM-DD.html` file to `output/` directory.

**Newsletter Archive Mechanism**:
- Each newsletter is automatically saved to `output/` folder (for daily use, not committed to Git)
- Simultaneously copied to `archive/` folder (for Git commit, preserving history)
- Filename format: `newsletter-YYYY-MM-DD.html` (e.g., `newsletter-2025-01-15.html`)
- Files in `archive/` folder will be committed to Git for easy viewing of historical newsletters
- `output/` folder is in `.gitignore` and will not be committed to Git

### 6. Send Newsletter

```bash
# Send to subscribers from MongoDB
LATEST=$(ls -t output/newsletter-*.html | head -n 1)
python scripts/send_email.py \
  --file "$LATEST" \
  --subject "TechSum Weekly · $(date +%Y-%m-%d)" \
  --from-mongo --tags "preview" --status active --limit 50 \
  --batch-size 10 --sleep 2
```

---

## 🚢 Deployment Guide

### Railway Deployment

The project is configured for Railway deployment. For detailed steps, see [DEPLOYMENT.md](./DEPLOYMENT.md)

**Quick Deployment Steps**:

1. **Create Railway Project**
   - Visit [Railway](https://railway.app)
   - Create new project and connect GitHub repository

2. **Configure Environment Variables**
   - Add the following environment variables in Railway project settings:
     - `MONGODB_URI`
     - `MONGODB_DB`
     - `MONGODB_COLL`
     - `EMAIL_USER`
     - `EMAIL_PASS`
     - `TECHSUM_API_KEY` (optional)
     - `ADMIN_USERNAME` (admin username, recommended to set)
     - `ADMIN_PASSWORD` (admin password, **must set strong password**)
     - `SESSION_SECRET` (session secret key, recommended to set random string)

3. **Auto Deployment**
   - Railway will automatically detect `railway.json` and `Procfile`
   - Get deployment URL after deployment completes

4. **Test Deployment**
   - Visit deployment URL to test all pages
   - Check if API endpoints are working properly

**Deployment Files**:
- `Procfile`: Defines Railway startup command
- `railway.json`: Railway build configuration

---

## 📡 API Documentation

### Subscribe API

**Endpoint**: `POST /api/subscribe`

**Request Body**:
```json
{
  "email": "user@example.com",
  "tags": ["preview"]  // optional
}
```

**Response**:
```json
{
  "ok": true,
  "email": "user@example.com"
}
```

**Note**: After successful subscription, the system automatically sends a welcome confirmation email to new subscribers.

---

### Unsubscribe API

**Endpoint**: `POST /api/unsubscribe`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "ok": true,
  "email": "user@example.com"
}
```

---

### Statistics API

**Endpoint**: `GET /api/stats`

**Response**:
```json
{
  "ok": true,
  "total": 100,
  "active": 85,
  "inactive": 15,
  "recent": [
    {
      "email": "user@example.com",
      "status": "active",
      "tags": ["preview"],
      "updatedAt": "2025-01-15T10:00:00.000Z",
      "createdAt": "2025-01-10T10:00:00.000Z"
    }
  ]
}
```

---

### Update Tags API

**Endpoint**: `PATCH /api/subscribers/:email/tags`

**Request Body**:
```json
{
  "tag": "preview",
  "add": true  // true to add, false to remove
}
```

**Response**:
```json
{
  "ok": true,
  "tags": ["preview", "user"]
}
```

---

### Delete Subscriber API

**Endpoint**: `DELETE /api/subscribers/:email`

**Response**:
```json
{
  "ok": true,
  "message": "Deleted user@example.com"
}
```

---

### Login API

**Endpoint**: `POST /api/login`

**Request Body**:
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response**:
```json
{
  "ok": true,
  "message": "Login successful"
}
```

---

### Logout API

**Endpoint**: `POST /api/logout`

**Response**:
```json
{
  "ok": true,
  "message": "Logged out successfully"
}
```

---

### Authentication Check API

**Endpoint**: `GET /api/auth/check`

**Response**:
```json
{
  "ok": true,
  "authenticated": true,
  "username": "admin"
}
```

---

### Health Check API

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "ok": true,
  "timestamp": "2025-01-15T10:00:00.000Z"
}
```

---

## 📁 Project Structure

```
Techsum-newsletter/
├── api/                    # API endpoints
│   ├── subscribe.js        # Subscribe API
│   └── unsubscribe.js      # Unsubscribe API
├── config/                 # Configuration files
│   └── categories.json     # News category configuration
├── docs/                   # Frontend pages
│   ├── index.html          # Subscribe page
│   ├── unsubscribe.html    # Unsubscribe page
│   ├── login.html          # Login page
│   └── admin.html          # Admin dashboard
├── lib/                    # Utility libraries
│   ├── mongo.js            # MongoDB connection utility
│   └── email.js            # Email sending utility
├── archive/                # Newsletter archive (committed to Git)
│   ├── README.md           # Archive documentation
│   └── newsletter-*.html   # Historical newsletter files
├── output/                 # Generated newsletter HTML (not committed to Git)
│   └── newsletter-*.html
├── scripts/                # Python scripts
│   ├── api.py              # Newsletter HTML generation
│   ├── send_email.py       # Batch email sending
│   ├── subscribers.py      # Subscriber management CLI
│   └── requirements.txt    # Python dependencies
├── src/                    # Resource files
│   ├── newsletter_template.html  # Newsletter template
│   ├── confirmation_email_template.html  # Subscription confirmation email template
│   ├── turing_black_logo.png      # Logo
│   └── utils.py            # Python utility functions
├── server.js               # Express server (local development)
├── package.json            # Node.js dependencies
├── Procfile                # Railway deployment configuration
├── railway.json            # Railway build configuration
├── DEPLOYMENT.md           # Detailed deployment guide
└── readme.md               # This file
```

---

## 🛠️ MongoDB Management

### Using Python CLI to Manage Subscribers

```bash
# Add subscriber
python scripts/subscribers.py add \
  --email someone@example.com \
  --tags preview \
  --status active

# Update status
python scripts/subscribers.py set-status \
  --email someone@example.com \
  --status inactive

# Add tags
python scripts/subscribers.py add-tags \
  --email someone@example.com \
  --tags user

# Remove tags
python scripts/subscribers.py remove-tags \
  --email someone@example.com \
  --tags preview

# Delete subscriber
python scripts/subscribers.py remove \
  --email someone@example.com

# List subscribers
python scripts/subscribers.py list \
  --status active \
  --tags preview
```

---

## 🎨 Tech Stack

- **Backend**: 
  - Node.js (Express) - API server
  - MongoDB - Database
- **Frontend**: 
  - Vanilla HTML/CSS/JavaScript - Framework-free, lightweight
  - Responsive design, mobile-friendly
- **Email**: 
  - Gmail SMTP - Email sending
- **Newsletter Generation**: 
  - Python (requests, jinja2) - Content fetching and template rendering
- **Deployment**: 
  - Railway - Cloud platform deployment

---

## 📝 License

Private project - All rights reserved

---

## 🔗 Links

- **Website**: [https://www.techsum.ai](https://www.techsum.ai)
- **Contact Email**: info@turingplanet.org
- **Deployment URL**: [https://web-production-914f7.up.railway.app/](https://web-production-914f7.up.railway.app/)

---

## 💡 Tips

1. **Subscriber Tag Notes**:
   - `preview`: Preview users for testing email sending
   - `user`: Regular users

2. **Email Sending Recommendations**:
   - Use `--batch-size` to control batch size, avoid triggering Gmail limits
   - Use `--sleep` to set sending interval, avoid rate limiting
   - Send to `preview` tagged users first for testing

3. **Security Recommendations**:
   - Do not commit `.env` file to Git
   - Use Gmail App Password instead of account password
   - Regularly update dependencies

---

**Made with ❤️ by TURING PLANET**
