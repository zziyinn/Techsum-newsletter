# TechSum Newsletter

A newsletter system that fetches tech highlights, generates HTML newsletters, and sends them via Gmail with subscriber management.

## Features

- 📧 **Newsletter Generation**: Fetch tech highlights from multiple sources and generate beautiful HTML newsletters
- 📬 **Email Sending**: Batch email sending via Gmail with MongoDB subscriber management
- 🌐 **Web Interface**: 
  - Subscribe page for users to sign up
  - Unsubscribe page for users to opt-out
  - Admin dashboard for subscriber management
- 💾 **MongoDB Integration**: Store and manage subscribers in MongoDB Atlas
- 🏷️ **Tag System**: Organize subscribers with tags (preview, user, etc.)

## Local Deployment

### 1. Environment Setup

Copy `env.example` to `.env` and fill in your configuration:

```bash
cp env.example .env
```

Required environment variables:
- `MONGODB_URI`: MongoDB Atlas connection string
- `MONGODB_DB`: Database name (default: techsum)
- `MONGODB_COLL`: Collection name (default: subscribers)
- `EMAIL_USER`: Gmail account for sending emails
- `EMAIL_PASS`: Gmail App Password
- `TECHSUM_API_KEY`: (Optional) TechSum API token for fetching highlights

### 2. Install Dependencies

```bash
# Node.js dependencies (API server)
npm install

# Python dependencies (newsletter generation & sending)
pip install -r requirements.txt
```

### 3. Start Local Server

```bash
npm run dev
# or
npm start
```

The server will start at `http://localhost:3000`:
- **Subscribe page**: http://localhost:3000/
- **Unsubscribe page**: http://localhost:3000/unsubscribe.html
- **Admin dashboard**: http://localhost:3000/admin.html
- **Health check**: http://localhost:3000/api/health

### 4. Generate Newsletter

```bash
python scripts/api.py
```

This generates `newsletter-YYYY-MM-DD.html` in the `output/` directory.

### 5. Send Newsletter

```bash
# Send to recipients from MongoDB
LATEST=$(ls -t output/newsletter-*.html | head -n 1)
python scripts/send_email.py \
  --file "$LATEST" \
  --subject "TechSum Weekly · $(date +%Y-%m-%d)" \
  --from-mongo --tags "preview" --status active --limit 50 \
  --batch-size 10 --sleep 2
```

## Admin Dashboard

Access the admin dashboard at http://localhost:3000/admin.html to:

- 📊 View subscriber statistics (total, active, inactive)
- 🔍 Search and filter subscribers by email, status, or tags
- ✏️ Edit subscriber tags (preview/user checkboxes)
- 🔄 Update subscriber status (active/inactive)
- 🗑️ Delete subscribers

## API Endpoints

- `POST /api/subscribe` - Subscribe a new email
- `POST /api/unsubscribe` - Unsubscribe an email
- `GET /api/stats` - Get subscriber statistics
- `PATCH /api/subscribers/:email/tags` - Update subscriber tags
- `DELETE /api/subscribers/:email` - Delete a subscriber

## MongoDB Management

Use the Python script for command-line subscriber management:

```bash
# Add subscriber
python scripts/subscribers.py add --email someone@example.com --tags preview --status active

# Update status
python scripts/subscribers.py set-status --email someone@example.com --status inactive

# Add tags
python scripts/subscribers.py add-tags --email someone@example.com --tags user

# Remove tags
python scripts/subscribers.py remove-tags --email someone@example.com --tags preview

# Delete subscriber
python scripts/subscribers.py remove --email someone@example.com

# List subscribers
python scripts/subscribers.py list --status active --tags preview
```

## Project Structure

```
├── api/
│   ├── subscribe.js      # Subscription API endpoint
│   └── unsubscribe.js    # Unsubscription API endpoint
├── docs/
│   ├── index.html        # Subscribe page (frontend)
│   ├── unsubscribe.html  # Unsubscribe page
│   └── admin.html        # Admin dashboard
├── lib/
│   └── mongo.js          # MongoDB connection utility
├── scripts/
│   ├── api.py            # Newsletter HTML generation
│   ├── send_email.py     # Batch email sending
│   └── subscribers.py    # MongoDB subscriber management CLI
├── server.js             # Express server for local development
├── package.json          # Node.js dependencies
└── requirements.txt      # Python dependencies
```

## Tech Stack

- **Backend**: Node.js (Express), MongoDB
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Email**: Gmail SMTP
- **Newsletter Generation**: Python (requests, jinja2)

## License

Private project - All rights reserved
