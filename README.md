<p align="center">
  <img src="files/static/img/fplogo.png" alt="FootPrint Logo" width="200">
</p>

<h1 align="center">FootPrint</h1>

<p align="center">
  <strong>Track - Detect - Protect</strong>
</p>

<p align="center">
  A comprehensive data breach detection and removal web application that helps users discover if their personal information has been compromised and provides actionable steps to secure their digital footprint.
</p>

<p align="center">
  <a href="https://footprint-ia69.onrender.com">View Live Demo</a>
</p>

---

## Demo

<p align="center">
  <img src="FootPrintDashboardDemo.gif" alt="FootPrint Dashboard Demo" width="800">
</p>

---

## Table of Contents

- [Why FootPrint?](#why-footprint)
- [Features](#features)
- [How It Works](#how-it-works)
- [Data Removal Protocol](#data-removal-protocol)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Deployment](#deployment)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Security Measures](#security-measures)
- [External APIs](#external-apis)
- [Project Structure](#project-structure)
- [Contributors](#contributors)
- [License](#license)

---

## Why FootPrint?

In today's digital age, data breaches occur with alarming frequency. Major companies like Adobe, LinkedIn, and Yahoo have all experienced breaches exposing millions of user credentials. The average person has over 100 online accounts, and many reuse passwords across multiple services. When a breach occurs, compromised credentials often end up for sale on the dark web within hours.

**FootPrint empowers you to:**

- **Detect** - Identify if your email or password has been exposed before attackers can exploit it
- **Protect** - Receive breach-specific remediation steps tailored to each compromised service
- **Remove** - Follow guided opt-out procedures for 15+ data brokers selling your personal information
- **Prevent** - Stop credential stuffing attacks by identifying and changing compromised passwords

FootPrint provides a simple, secure interface to check your credentials against databases of known breaches without ever storing or transmitting your actual password.

---

## Features

### Email Breach Checking
Check if your email address appears in any known data breaches. FootPrint queries the XposedOrNot database containing millions of compromised records from documented breaches.

### Password Breach Checking
Verify if your password has been exposed in data breaches. Using the k-anonymity model, your password is never sent over the network - only a partial hash is transmitted, ensuring your password remains private even during the check.

### Data Removal Protocol

FootPrint provides a comprehensive two-tier data removal system:

**Tier 1: Breach-Specific Remediation Actions**
- 25+ major breaches mapped to specific security steps
- Priority-ranked actions (High, Medium, Low)
- Direct links to security settings pages
- Step-by-step instructions for each breached service (LinkedIn, Adobe, Facebook, Twitter, Spotify, and more)

**Tier 2: Data Broker Opt-Out Guide**
- 15 data broker removal providers with opt-out URLs
- Estimated removal timeframes (ETA)
- Step-by-step opt-out instructions
- Covers major brokers: Whitepages, Spokeo, BeenVerified, Intelius, Radaris, and more
- Includes parent company opt-outs for broader coverage (PeopleConnect, Acxiom, LexisNexis)

### Secure User Authentication
- Create an account with validated credentials
- Login with rate limiting protection against brute-force attacks (3 attempts, 5-minute lockout)
- Session-based authentication with secure cookies
- CSRF protection on all forms

### Modern UI/UX
- Clean, responsive dashboard design
- Real-time breach checking with visual feedback
- Smooth animated light/dark theme toggle
- Mobile-responsive layout

### Privacy-First Design
- No passwords are stored in plain text (PBKDF2-SHA256 hashing)
- Password checking uses k-anonymity (only 5 characters of SHA-1 hash sent to API)
- All sensitive operations happen server-side

---

## How It Works

### Email Breach Checking Process

```
User enters email
        |
        v
+-------------------+
| Frontend sends    |
| email to backend  |
+-------------------+
        |
        v
+-------------------+
| Backend proxies   |
| request to        |
| XposedOrNot API   |
+-------------------+
        |
        v
+-------------------+
| API returns list  |
| of breaches       |
| (if any)          |
+-------------------+
        |
        v
+-------------------+
| Backend fetches   |
| breach-specific   |
| remediation steps |
+-------------------+
        |
        v
+-------------------+
| Results displayed |
| with actions and  |
| security advice   |
+-------------------+
```

### Password Breach Checking Process (k-Anonymity)

The password check uses a privacy-preserving technique called k-anonymity:

```
User enters password
        |
        v
+------------------------+
| Backend computes       |
| SHA-1 hash of password |
| Example: 5BAA61E4...   |
+------------------------+
        |
        v
+------------------------+
| Only first 5 chars     |
| sent to HIBP API       |
| Example: 5BAA6          |
+------------------------+
        |
        v
+------------------------+
| API returns all hashes |
| starting with 5BAA6    |
| (hundreds of matches)  |
+------------------------+
        |
        v
+------------------------+
| Backend checks if full |
| hash exists in results |
| locally (never sent!)  |
+------------------------+
        |
        v
+------------------------+
| Return breach count    |
| and severity level     |
+------------------------+
```

**Why this matters:** Your actual password never leaves your browser. Only a partial hash prefix is transmitted, making it impossible for anyone (including the API provider) to determine your password.

### Severity Levels for Password Breaches

| Severity | Breach Count | Meaning |
|----------|--------------|---------|
| Critical | 100,000+ | Extremely common, change immediately |
| High | 10,000+ | Very frequently exposed |
| Medium | 1,000+ | Moderately common |
| Low | < 1,000 | Less common but still exposed |

---

## Data Removal Protocol

### Breach-Specific Actions

When breaches are detected, FootPrint provides tailored remediation steps for 25+ services:

| Service | Priority | Actions Include |
|---------|----------|-----------------|
| LinkedIn | High | Password change, 2FA, session review, connected apps audit |
| Adobe | High | Password change, two-step verification, privacy review |
| Facebook | High | Password change, 2FA, active sessions check, app review |
| Dropbox | High | Password change, 2FA, linked apps audit |
| Patreon | High | Password change, 2FA, payment methods review |
| Twitter/X | Medium | Password change, 2FA, login history check |
| Spotify | Medium | Password change, sign out everywhere |
| Canva | Medium | Password change, 2FA, account deletion option |
| MyFitnessPal | Medium | Password change, connected apps review |
| Kickstarter | Medium | Password change, 2FA, payment methods review |
| And 15+ more... | Varies | Service-specific security steps |

### Data Broker Opt-Out Providers

FootPrint guides you through removing your data from 15 major data brokers:

| Provider | Category | Estimated Time |
|----------|----------|----------------|
| Whitepages | People Search | 1-7 days |
| Spokeo | People Search | 3-10 days |
| BeenVerified | People Search | 24-48 hours |
| Intelius | People Search | 72 hours |
| Radaris | People Search | 24-48 hours |
| PeopleFinders | People Search | 5-7 days |
| FastPeopleSearch | People Search | 72 hours |
| Nuwber | People Search | 3-5 days |
| PeopleConnect | Parent Company | 48-72 hours |
| Acxiom | Data Aggregator | 7-30 days |
| LexisNexis | Data Aggregator | 7-14 days |
| MyLife | People Search | 7-14 days |
| That's Them | People Search | 24-48 hours |
| FamilyTreeNow | People Search | 24-48 hours |
| USPhoneBook | People Search | 24-48 hours |

---

## Architecture

```
+--------------------------------------------------+
|                    CLIENT                         |
|  +-------------+  +-------------+  +-----------+  |
|  | Landing     |  | Auth Modals |  | Dashboard |  |
|  | Page        |  | (Login/     |  |           |  |
|  | (index.html)|  | Signup)     |  |           |  |
|  +-------------+  +-------------+  +-----------+  |
|        |               |               |          |
|        +-------+-------+-------+-------+          |
|                |               |                  |
|           script.js     dashboardScripts.js       |
+--------------------------------------------------+
                         |
                         | HTTP/HTTPS
                         v
+--------------------------------------------------+
|                 FLASK BACKEND                     |
|  +------------+  +------------+  +--------------+ |
|  | Routes     |  | Auth       |  | API Proxy    | |
|  | - /        |  | - /login   |  | - /api/      | |
|  | - /dashboard| | - /signup  |  |   check-     | |
|  | - /logout  |  | - /logout  |  |   breach     | |
|  +------------+  +------------+  | - /api/      | |
|                                  |   check-     | |
|  +------------+                  |   password   | |
|  | Removal    |                  | - /api/      | |
|  | Protocol   |                  |   removal/*  | |
|  | - Breach   |                  +--------------+ |
|  |   Actions  |                                  |
|  | - Data     |   +------------------+           |
|  |   Brokers  |   | Security Layer   |           |
|  +------------+   | - CSRF Protection|           |
|                   | - Rate Limiting  |           |
|                   | - Input Valid.   |           |
|                   +------------------+           |
+--------------------------------------------------+
           |                           |
           v                           v
+------------------+         +-------------------+
|    Database      |         |   External APIs   |
| +-------------+  |         | +---------------+ |
| | PostgreSQL  |  |         | | XposedOrNot   | |
| | (production)|  |         | | (Email)       | |
| | SQLite      |  |         | +---------------+ |
| | (local dev) |  |         | +---------------+ |
| +-------------+  |         | | HIBP Pwned    | |
| +-------------+  |         | | Passwords     | |
| | Users       |  |         | +---------------+ |
| | LoginAttempt|  |         +-------------------+
| | Removal*    |  |
| | Reviews     |  |
| +-------------+  |
+------------------+
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Flask 3.x (Python 3.10+) | Web framework, routing, API handling |
| **Database** | PostgreSQL (production) | User storage, removal tracking |
| **Database** | SQLite (development) | Local development database |
| **ORM** | Flask-SQLAlchemy | Database abstraction layer |
| **Security** | Flask-WTF | CSRF protection |
| **Security** | Werkzeug | Password hashing (PBKDF2-SHA256) |
| **Server** | Gunicorn | Production WSGI server |
| **Frontend** | HTML5, CSS3, CSS Variables | Structure and theming |
| **Frontend** | JavaScript (ES6+) | Client-side interactivity |
| **Frontend** | jQuery 4.0 | DOM manipulation |
| **Fonts** | Google Fonts (Inter) | Typography |
| **Deployment** | Render | Cloud hosting with PostgreSQL |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/inshaal81/FootPrint.git
cd FootPrint

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r files/requirements.txt

# 5. Run the application
cd files
python app.py
```

The application will be available at http://localhost:5001

### Quick Start (One-liner)

```bash
git clone https://github.com/inshaal81/FootPrint.git && cd FootPrint && python -m venv venv && source venv/bin/activate && pip install -r files/requirements.txt && cd files && python app.py
```

---

## Deployment

### Deploy to Render

FootPrint includes a `render.yaml` blueprint for one-click deployment to Render.

#### Option 1: Blueprint Deployment (Recommended)

1. Fork or push this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New** > **Blueprint**
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and configure:
   - A PostgreSQL database (`footprint-db`)
   - A Python web service with Gunicorn
   - Auto-generated `FLASK_SECRET_KEY`
   - Database connection string

#### Option 2: Manual Deployment

1. Create a new **PostgreSQL** database on Render
2. Create a new **Web Service** with these settings:
   - **Runtime**: Python
   - **Build Command**: `pip install -r files/requirements.txt`
   - **Start Command**: `cd files && gunicorn app:app`
3. Add environment variables:
   - `FLASK_SECRET_KEY`: Generate a secure random string
   - `DATABASE_URL`: Copy from your PostgreSQL database
   - `PYTHON_VERSION`: `3.11.4`

### Production URL

The live application is deployed at: **https://footprint-ia69.onrender.com**

---

## Usage

### Creating an Account

1. Navigate to https://footprint-ia69.onrender.com (or http://localhost:5001 for local)
2. Click "Sign Up" button
3. Enter:
   - Username (3-30 characters, alphanumeric with underscores/hyphens)
   - Email address
   - Password (minimum 8 characters, must include uppercase, lowercase, and number)
   - Confirm password
4. Click "Register"

### Checking for Breaches

1. Log in to your account
2. On the dashboard, you can check:
   - **Email Address**: Enter your email in the "Email Address" field
   - **Password**: Enter any password to check (it will NOT be stored)
3. Click "Check for Breaches"
4. Review results:
   - Green = No breaches found
   - Red = Breaches detected with list of compromised services

### Using Data Removal Protocol

1. After checking for breaches, view the **Removal Protocol** section
2. **Breach-Specific Actions**: For each detected breach, follow the provided steps to secure that specific account
3. **Data Broker Opt-Out**: Visit each data broker's opt-out page and follow the step-by-step instructions to remove your information

### Theme Toggle

Click the theme toggle button in the header to switch between light and dark modes. The preference is saved for future visits.

---

## API Documentation

### Authentication Required

All API endpoints require an active session (user must be logged in).

### POST /api/check-breach

Check if an email address has been exposed in data breaches.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (breaches found):**
```json
{
  "email": "user@example.com",
  "breached": true,
  "breach_count": 3,
  "breaches": ["LinkedIn", "Adobe", "Dropbox"]
}
```

**Response (no breaches):**
```json
{
  "email": "user@example.com",
  "breached": false,
  "breaches": []
}
```

### POST /api/check-password

Check if a password has been exposed in data breaches using k-anonymity.

**Request:**
```json
{
  "password": "yourpassword123"
}
```

**Response (password found):**
```json
{
  "breached": true,
  "count": 52847,
  "severity": "critical",
  "message": "This password has been exposed 52,847 times in data breaches."
}
```

**Response (password safe):**
```json
{
  "breached": false,
  "count": 0,
  "message": "This password has not been found in known data breaches."
}
```

### POST /api/removal/breach-actions

Get breach-specific remediation actions for detected breaches.

**Request:**
```json
{
  "breaches": ["LinkedIn", "Adobe", "Facebook"]
}
```

**Response:**
```json
{
  "actions": [
    {
      "breach_name": "LinkedIn",
      "action_type": "account_security",
      "priority": "high",
      "company": "LinkedIn",
      "url": "https://www.linkedin.com/psettings/security",
      "steps": [
        "Change your LinkedIn password immediately",
        "Enable two-factor authentication in Security Settings",
        "Review all connected third-party apps"
      ]
    }
  ],
  "total_breaches": 3,
  "matched_count": 3
}
```

### GET /api/removal/providers

Get list of data broker opt-out providers.

**Response:**
```json
[
  {
    "id": "whitepages",
    "name": "Whitepages",
    "optOutUrl": "https://www.whitepages.com/suppression-requests",
    "eta": "1-7 days",
    "steps": [
      "Search for your listing on the suppression page",
      "Select your record from the results",
      "Verify via phone number to confirm removal"
    ]
  }
]
```

### Error Responses

| Status | Description |
|--------|-------------|
| 400 | Invalid request (missing or malformed data) |
| 401 | Unauthorized (not logged in) |
| 429 | Rate limit exceeded |
| 502 | External API error |
| 503 | Service unavailable |
| 504 | Request timeout |

---

## Security Measures

### Password Storage

Passwords are never stored in plain text. FootPrint uses Werkzeug's secure password hashing:

```python
# Hashing (on signup)
hashed = generate_password_hash(password, method='pbkdf2:sha256')

# Verification (on login)
check_password_hash(stored_hash, provided_password)
```

**PBKDF2-SHA256** uses:
- 260,000 iterations (Werkzeug default)
- Random salt per password
- Industry-standard key derivation

### Rate Limiting

Protection against brute-force attacks:

| Setting | Value |
|---------|-------|
| Max attempts | 3 |
| Lockout duration | 5 minutes (300 seconds) |
| Storage | Database (persists across restarts) |

### CSRF Protection

All forms include CSRF tokens via Flask-WTF:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Input Validation

Both client-side and server-side validation:

**Username:**
- 3-30 characters
- Alphanumeric, underscores, hyphens only
- Unique in database

**Email:**
- Valid email format
- Maximum 254 characters
- Unique in database

**Password:**
- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### k-Anonymity for Password Checking

Your password is NEVER sent to external services:

1. Password hashed locally with SHA-1
2. Only first 5 characters of hash sent to HIBP API
3. API returns all matching hash suffixes
4. Matching done locally on server
5. Password never leaves your infrastructure

---

## External APIs

### XposedOrNot API

**Purpose:** Email breach checking

| Property | Value |
|----------|-------|
| Endpoint | `https://api.xposedornot.com/v1/check-email/{email}` |
| Method | GET |
| Authentication | None required |
| Rate Limit | Reasonable use policy |
| Cost | Free |

### HIBP Pwned Passwords API

**Purpose:** Password breach checking with k-anonymity

| Property | Value |
|----------|-------|
| Endpoint | `https://api.pwnedpasswords.com/range/{hash_prefix}` |
| Method | GET |
| Authentication | None required |
| Rate Limit | ~10 requests/second |
| Cost | Free |

---

## Project Structure

```
FootPrint/
|-- files/
|   |-- app.py                    # Main Flask application
|   |-- database.py               # Database connection utilities
|   |-- requirements.txt          # Python dependencies
|   |-- static/
|   |   |-- styles.css            # Landing page styles
|   |   |-- dashboardStyles.css   # Dashboard styles
|   |   |-- script.js             # Landing page JavaScript
|   |   |-- dashboardScripts.js   # Dashboard JavaScript
|   |   |-- jquery-4.0.0.min.js   # jQuery library
|   |   |-- img/
|   |       |-- fplogo.png        # Application logo
|   |       |-- tbg.png           # Background image (light)
|   |       |-- tbbg.png          # Background image (dark)
|   |       |-- mbg.png           # Mobile background
|   |-- templates/
|   |   |-- index.html            # Landing page template
|   |   |-- dashboard.html        # Dashboard template
|   |   |-- login.html            # Login modal template
|   |   |-- signup.html           # Signup modal template
|   |   |-- aboutus.html          # About page template
|   |-- instance/
|       |-- data.db               # SQLite database (local dev, auto-generated)
|-- FootPrintDashboardDemo.gif    # Demo animation
|-- render.yaml                   # Render deployment blueprint
|-- README.md                     # This file
```

---

## Contributors

<table>
  <tr>
    <td align="center">
      <strong>Muhammad Inshaal</strong><br>
      <sub>Web Development, Machine Learning</sub><br>
      <sub>Project Lead & Developer</sub>
    </td>
    <td align="center">
      <strong>Terry Tran</strong><br>
      <sub>Information Systems</sub><br>
      <sub>Database Developer</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Trung Nguyen</strong><br>
      <sub>Information Systems</sub><br>
      <sub>JavaScript Dev</sub>
    </td>
    <td align="center">
      <strong>Vi Khang Tran</strong><br>
      <sub>Information Systems</sub><br>
      <sub>Removal Protocol</sub>
    </td>
  </tr>
</table>

---

## Troubleshooting

### Port 5001 Already in Use

```bash
# Find and kill the process using port 5001
lsof -i :5001
kill -9 <PID>
```

### Database Errors (Local Development)

```bash
# Delete and recreate database
rm files/instance/data.db
python app.py  # Database auto-creates on startup
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r files/requirements.txt
```

### Rate Limit Exceeded

Wait 5 minutes for the lockout to expire, or manually clear the LoginAttempt table in the database.

### Render Deployment Issues

- Ensure `DATABASE_URL` environment variable is set
- Check that `FLASK_SECRET_KEY` is configured
- Verify Python version is 3.10+
- Review Render logs for specific error messages

---

## License

This is an academic project developed for coursework at **Drexel University**.

---

## Acknowledgments

- [XposedOrNot](https://xposedornot.com/) for the free email breach checking API
- [Have I Been Pwned](https://haveibeenpwned.com/) for the Pwned Passwords API
- [Inter Font](https://rsms.me/inter/) for typography

---

<p align="center">
  <strong>Stay safe. Check your footprint.</strong>
</p>
