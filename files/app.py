#Terry
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
import json
import os
import re
import hashlib
import requests  # For HIBP API calls
from datetime import datetime, timedelta
# Terry added 
from tracker.activity import log_activity
from database import get_db
import tldextract 



#  Create ONE Flask app (Terry)
app = Flask(__name__, static_folder='static')

#Terry modified
# ===== Secure Secret Key =====
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("FLASK_SECRET_KEY environment variable is required.")

# CSRF Configuration for production
# Disable strict referer checking for HTTPS (Render deployment)
app.config['WTF_CSRF_SSL_STRICT'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour token validity

#Terry - modified (made more modular and flexible for larger Flask apps)
csrf = CSRFProtect()
csrf.init_app(app)

#Terry modified
# ===== Configure and link the database =====
# Database configuration - PostgreSQL (production) or SQLite (local dev)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render uses 'postgres://' but SQLAlchemy requires 'postgresql://'
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["DATABASE"] = os.path.join(basedir, "instance", "data.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config["DATABASE"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- TERRY: 
# Path to the single blocklist file
# --- TRACKER CONFIGURATION ---
RADAR_FILE = os.path.join(app.root_path, 'tds.json')
RADAR_URL = "https://raw.githubusercontent.com/duckduckgo/tracker-blocklists/main/web/tds.json"

def update_tracker_data():
    """Downloads the latest DDG Radar file if it doesn't exist."""
    if not os.path.exists(RADAR_FILE):
        try:
            print("Downloading DuckDuckGo Tracker Radar data...")
            r = requests.get(RADAR_URL, timeout=10)
            with open(RADAR_FILE, 'w') as f:
                f.write(r.text)
        except Exception as e:
            print(f"Could not download Radar data: {e}")

def get_tracker_list():
    file_path = os.path.join(app.root_path, 'trackers.json')
    
    # Check if file exists first
    if not os.path.exists(file_path):
        print("⚠️ trackers.json is missing! Creating a blank one.")
        with open(file_path, 'w') as f:
            json.dump({"trackers": {}}, f)
        return {}

    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content).get('trackers', {})
    except Exception as e:
        print(f"❌ Error reading trackers.json: {e}")
        return {}

def check_domain_safety(url):
    trackers = get_tracker_list()
    # Use tldextract for professional domain parsing
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}".lower()
    
    match = trackers.get(domain)
    if not match:
        # Check if any tracker domain is a parent of our current domain
        for t_domain, details in trackers.items():
            if domain.endswith('.' + t_domain):
                match = details
                break

    if match:
        owner = match.get('owner', 'Unknown Entity')
        # Use new refined logic instead of just '10'
        score = calculate_refined_score(match) if isinstance(match, dict) else 10
        return True, owner, score
        
    return False, "Clean", 0

# Run update on startup
with app.app_context():
    update_tracker_data()

# ===== User model =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


#Inshaal - LoginAttempt model (persistent rate limiting)
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, index=True)
    failed_count = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)


#Inshaal - Input Validation
def validate_email(email):
    """Validate email format."""
    if not email or len(email) > 254:
        return False, "Email is required and must be under 254 characters."
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format."
    return True, ""


def validate_username(username):
    """Validate username - alphanumeric, underscore, hyphen only."""
    if not username:
        return False, "Username is required."
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be 3-30 characters."
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    return True, ""


def validate_password(password):
    """Validate password strength."""
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if len(password) > 128:
        return False, "Password must be under 128 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    return True, ""

#Khang 
class RemovalProvider(db.Model):
    id = db.Column(db.String(50), primary_key=True)  
    name = db.Column(db.String(120), nullable=False)
    opt_out_url = db.Column(db.String(300), nullable=False)
    eta = db.Column(db.String(50), nullable=True)
    steps_json = db.Column(db.Text, nullable=True)   

class RemovalAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    provider_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

#Khang (review model for user feedback on providers)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#Trung Nguyen
# ===== URL Review model (reviews tied to scanned website URLs) =====
class UrlReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    url = db.Column(db.String(350), nullable=False, index=True)   # normalized URL
    rating = db.Column(db.Integer, nullable=False)               # 1-5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#Terry modified
# Create tables
with app.app_context():
    try:
        db.create_all()
        update_tracker_data()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    # Create activity_logs table (used by tracker module)
    from sqlalchemy import text
    with db.engine.connect() as conn:
        if DATABASE_URL:
            # PostgreSQL syntax
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    action TEXT,
                    target TEXT,
                    status TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
        else:
            # SQLite syntax
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    target TEXT,
                    status TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """))
        conn.commit()
    if RemovalProvider.query.count() == 0:
        providers = [
            # Tier 1: High Priority People-Search Sites
            RemovalProvider(
                id="whitepages",
                name="Whitepages",
                opt_out_url="https://www.whitepages.com/suppression-requests",
                eta="1-7 days",
                steps_json=json.dumps([
                    "Search for your listing on the suppression page",
                    "Select your record from the results",
                    "Verify via phone number to confirm removal"
                ])
            ),
            RemovalProvider(
                id="spokeo",
                name="Spokeo",
                opt_out_url="https://www.spokeo.com/optout",
                eta="3-10 days",
                steps_json=json.dumps([
                    "Search for your profile on Spokeo.com",
                    "Copy your profile URL",
                    "Paste URL in opt-out form and enter email",
                    "Click confirmation link in email"
                ])
            ),
            RemovalProvider(
                id="beenverified",
                name="BeenVerified",
                opt_out_url="https://www.beenverified.com/f/optout/search",
                eta="24-48 hours",
                steps_json=json.dumps([
                    "Search for your name and state",
                    "Find your listing and click the arrow",
                    "Enter your email and complete CAPTCHA",
                    "Verify via email confirmation link"
                ])
            ),
            RemovalProvider(
                id="intelius",
                name="Intelius",
                opt_out_url="https://www.intelius.com/opt-out",
                eta="72 hours",
                steps_json=json.dumps([
                    "Search for your profile on Intelius.com",
                    "Copy your profile URL",
                    "Paste URL in the opt-out form",
                    "Verify your request via email"
                ])
            ),
            RemovalProvider(
                id="radaris",
                name="Radaris",
                opt_out_url="https://radaris.com/control/privacy",
                eta="24-48 hours",
                steps_json=json.dumps([
                    "Search for your listing on Radaris.com",
                    "Click 'Full Profile' to open your record",
                    "Copy the profile URL",
                    "Submit URL in the privacy control form",
                    "Verify via email"
                ])
            ),
            RemovalProvider(
                id="peoplefinders",
                name="PeopleFinders",
                opt_out_url="https://www.peoplefinders.com/opt-out",
                eta="5-7 days",
                steps_json=json.dumps([
                    "Search for your profile on PeopleFinders.com",
                    "Copy your profile URL",
                    "Paste URL in the opt-out form",
                    "Enter email and solve CAPTCHA",
                    "Confirm via email"
                ])
            ),
            RemovalProvider(
                id="mylife",
                name="MyLife",
                opt_out_url="https://www.mylife.com/ccpa/index.pubview",
                eta="7-14 days",
                steps_json=json.dumps([
                    "Go to MyLife CCPA opt-out page",
                    "Submit your name and profile URL",
                    "Or email privacy@mylife.com with your details",
                    "Wait for confirmation"
                ])
            ),
            RemovalProvider(
                id="fastpeoplesearch",
                name="FastPeopleSearch",
                opt_out_url="https://www.fastpeoplesearch.com/removal",
                eta="72 hours",
                steps_json=json.dumps([
                    "Search your name on FastPeopleSearch.com",
                    "Find your listing and click View Free Details",
                    "Scroll down and click 'Remove My Record'",
                    "Complete the CAPTCHA and confirm"
                ])
            ),
            RemovalProvider(
                id="nuwber",
                name="Nuwber",
                opt_out_url="https://nuwber.com/removal/link",
                eta="3-5 days",
                steps_json=json.dumps([
                    "Search for your profile on Nuwber.com",
                    "Copy your profile URL",
                    "Submit the URL in the removal form",
                    "Confirm via email"
                ])
            ),
            # Tier 2: Parent Companies (cover multiple sites)
            RemovalProvider(
                id="peopleconnect",
                name="PeopleConnect (TruthFinder/InstantCheckmate)",
                opt_out_url="https://suppression.peopleconnect.us/login",
                eta="48-72 hours",
                steps_json=json.dumps([
                    "Go to PeopleConnect suppression center",
                    "Create an account or log in",
                    "Submit your suppression request",
                    "This covers TruthFinder, InstantCheckmate, USSearch, and Intelius"
                ])
            ),
            RemovalProvider(
                id="acxiom",
                name="Acxiom (Major Data Aggregator)",
                opt_out_url="https://isapps.acxiom.com/optout/optout.aspx",
                eta="7-30 days",
                steps_json=json.dumps([
                    "Fill in your personal information",
                    "Submit the opt-out form",
                    "Acxiom supplies data to thousands of sites",
                    "Opting out here has wide-reaching effects"
                ])
            ),
            RemovalProvider(
                id="lexisnexis",
                name="LexisNexis",
                opt_out_url="https://consumer.risk.lexisnexis.com/request",
                eta="7-14 days",
                steps_json=json.dumps([
                    "Request your personal data file first",
                    "Review what data they have on you",
                    "Submit opt-out request",
                    "Follow up if needed"
                ])
            ),
            # Tier 3: Additional Brokers
            RemovalProvider(
                id="thatsthem",
                name="That's Them",
                opt_out_url="https://thatsthem.com/optout",
                eta="24-48 hours",
                steps_json=json.dumps([
                    "Search for your record on ThatsThem.com",
                    "Copy the record URL",
                    "Submit opt-out request with the URL",
                    "Confirm via email"
                ])
            ),
            RemovalProvider(
                id="familytreenow",
                name="FamilyTreeNow",
                opt_out_url="https://www.familytreenow.com/optout",
                eta="24-48 hours",
                steps_json=json.dumps([
                    "Search for your name on FamilyTreeNow.com",
                    "Find your record",
                    "Click opt-out and confirm your identity"
                ])
            ),
            RemovalProvider(
                id="usphonebook",
                name="USPhoneBook",
                opt_out_url="https://www.usphonebook.com/opt-out",
                eta="24-48 hours",
                steps_json=json.dumps([
                    "Search for your listing",
                    "Find your record and click it",
                    "Click the opt-out link",
                    "Confirm removal"
                ])
            )
        ]
        db.session.add_all(providers)
        db.session.commit()


# ===== Home =====
@app.route("/")
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

#Trung Nguyen
#----- About Us =====
@app.route("/about")
def about():
    return render_template("aboutus.html")

#Terry
# ===== Rate Limiting Constants ===
MAX_ATTEMPTS = 3
LOCK_TIME = 300  # 5 minutes in seconds


# ===== Login POST with security checks =====
@app.route("/login", methods=["POST"])
def login():
    from werkzeug.security import check_password_hash

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for('home'))

    # Get or create login attempt record
    attempt = LoginAttempt.query.filter_by(username=username).first()
    if not attempt:
        attempt = LoginAttempt(username=username, failed_count=0)
        db.session.add(attempt)

    current_time = datetime.utcnow()

    # Check if account is locked
    if attempt.locked_until and current_time < attempt.locked_until:
        remaining = int((attempt.locked_until - current_time).total_seconds())
        flash(f"Account locked. Try again in {remaining} seconds.", "error")
        return redirect(url_for('home'))

    # Clear lock if expired
    if attempt.locked_until and current_time >= attempt.locked_until:
        attempt.failed_count = 0
        attempt.locked_until = None

    # Check credentials
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Successful login - reset attempts
        attempt.failed_count = 0
        attempt.locked_until = None
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        log_activity("login")
        flash("Login successful!", "success")

        return redirect(url_for('dashboard'))

    # Failed login - increment counter
    attempt.failed_count += 1
    attempt.last_attempt = current_time

    if attempt.failed_count >= MAX_ATTEMPTS:
        attempt.locked_until = current_time + timedelta(seconds=LOCK_TIME)
        db.session.commit()
        flash(f"Account locked for {LOCK_TIME // 60} minutes due to multiple failed attempts.", "error")
    else:
        db.session.commit()
        remaining_attempts = MAX_ATTEMPTS - attempt.failed_count
        flash(f"Invalid credentials. {remaining_attempts} attempt(s) remaining.", "error")

    return redirect(url_for('home'))

# ===== Signup POST =====

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Validate username
    valid, error = validate_username(username)
    if not valid:
        flash(error, "error")
        return redirect(url_for("home"))

    # Validate email
    valid, error = validate_email(email)
    if not valid:
        flash(error, "error")
        return redirect(url_for("home"))

    # Validate password
    valid, error = validate_password(password)
    if not valid:
        flash(error, "error")
        return redirect(url_for("home"))

    # Password match check
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("home"))

    # Username exists check
    if User.query.filter_by(username=username).first():
        flash("Username already exists!", "error")
        return redirect(url_for("home"))

    # Email exists check
    if User.query.filter_by(email=email).first():
        flash("Email already registered!", "error")
        return redirect(url_for("home"))

    # Create user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash("Signup successful! Please log in.", "success")
    return redirect(url_for("home"))

#Khang
# ===== Dashboard =====
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    username = session.get('username', 'User')
    return render_template("dashboard.html", username=username)

#Trung Nguyen
# ===== Ratings Page (shows all reviews for a URL) =====
@app.route("/ratings")
def ratings_page():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    username = session.get('username', 'User')
    return render_template("ratings.html", username=username)

# ===== Logout =====
@app.route("/logout")
def logout():
    log_activity("logout")
    session.clear()
    return redirect(url_for('home'))

# ===== Modals served separately =====
@app.route("/login_modal")
def login_modal():
    return render_template("login.html")

@app.route("/signup_modal")
def signup_modal():
    return render_template("signup.html")

#GET 
@app.route("/api/removal/providers", methods=["GET"])
def api_removal_providers():
    # Only allow logged-in users to access this API
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    providers = RemovalProvider.query.all()

    # Convert DB rows into JSON objects for the frontend
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "optOutUrl": p.opt_out_url,
            "eta": p.eta,
            "steps": json.loads(p.steps_json) if p.steps_json else []
        } for p in providers
    ])

#POST
@app.route("/api/removal/action", methods=["POST"])
@csrf.exempt  # Exempt from CSRF - uses session auth + JSON body
def api_removal_action():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    provider_id = data.get("provider_id")
    status = data.get("status")
    notes = data.get("notes", "")

    # Validate request
    if not provider_id or not status:
        return jsonify({"error": "provider_id and status required"}), 400

    if status not in ["Not started", "Submitted", "Completed"]:
        return jsonify({"error": "invalid status"}), 400

    action = RemovalAction(
        user_id=session["user_id"],
        provider_id=provider_id,
        status=status,
        notes=notes
    )

    db.session.add(action)
    db.session.commit()

    return jsonify({"ok": True})

#SUMMARY
@app.route("/api/removal/summary", methods=["GET"])
def api_removal_summary():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    actions = (RemovalAction.query
               .filter_by(user_id=session["user_id"])
               .order_by(RemovalAction.id.desc())
               .all())

    submitted = sum(1 for a in actions if a.status == "Submitted")
    completed = sum(1 for a in actions if a.status == "Completed")

    return jsonify({
        "submitted": submitted,
        "completed": completed,
        "actions": [
            {
                "provider_id": a.provider_id,
                "status": a.status,
                "notes": a.notes,
                "created_at": a.created_at.isoformat() if a.created_at else None
            } for a in actions
        ]
    })

# Khang (add GET route for reviews)
@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    reviews = Review.query.order_by(Review.created_at.desc()).all()

    return jsonify([
        {
            "id": r.id,
            "user_id": r.user_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in reviews
    ])


# Breach-specific remediation actions mapping
# Maps breach names (from XposedOrNot API) to recommended security actions
BREACH_ACTIONS = {
    "LinkedIn": {
        "action_type": "account_security",
        "priority": "high",
        "company": "LinkedIn",
        "url": "https://www.linkedin.com/psettings/security",
        "steps": [
            "Change your LinkedIn password immediately",
            "Enable two-factor authentication in Security Settings",
            "Review all connected third-party apps",
            "Check active sessions and sign out unrecognized devices",
            "Request a copy of your data at Settings > Data Privacy"
        ]
    },
    "Adobe": {
        "action_type": "account_security",
        "priority": "high",
        "company": "Adobe",
        "url": "https://account.adobe.com/security",
        "steps": [
            "Change your Adobe account password",
            "Enable two-step verification",
            "Check if you use this password elsewhere and change those too",
            "Review connected apps under Account > Privacy"
        ]
    },
    "Dropbox": {
        "action_type": "account_security",
        "priority": "high",
        "company": "Dropbox",
        "url": "https://www.dropbox.com/account/security",
        "steps": [
            "Change your Dropbox password immediately",
            "Enable two-step verification",
            "Go to Security > Active sessions and end unfamiliar sessions",
            "Review linked apps and revoke unrecognized ones"
        ]
    },
    "Twitter": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "X (Twitter)",
        "url": "https://twitter.com/settings/security",
        "steps": [
            "Change your X (Twitter) password",
            "Enable two-factor authentication",
            "Review apps with account access and revoke untrusted ones",
            "Check recent login history for unfamiliar activity"
        ]
    },
    "Facebook": {
        "action_type": "account_security",
        "priority": "high",
        "company": "Facebook",
        "url": "https://www.facebook.com/settings?tab=security",
        "steps": [
            "Change your Facebook password immediately",
            "Enable two-factor authentication",
            "Review active sessions in Security Settings",
            "Check connected apps and remove suspicious ones"
        ]
    },
    "MySpace": {
        "action_type": "account_deletion",
        "priority": "low",
        "company": "MySpace",
        "url": "https://help.myspace.com/hc/en-us/articles/202241380",
        "steps": [
            "Log in to your MySpace account (desktop only)",
            "Go to Settings",
            "Click Delete Account",
            "Select a reason and confirm deletion"
        ]
    },
    "Canva": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Canva",
        "url": "https://www.canva.com/settings/account",
        "steps": [
            "Change your Canva password immediately",
            "Go to Account Settings > Login & Security",
            "Enable two-factor authentication",
            "If no longer using, delete account (takes up to 14 days)"
        ]
    },
    "Deezer": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Deezer",
        "url": "https://www.deezer.com/account/",
        "steps": [
            "Change your Deezer password",
            "Review account settings",
            "Submit GDPR data deletion request if needed"
        ]
    },
    "Dailymotion": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Dailymotion",
        "url": "https://www.dailymotion.com/settings/security",
        "steps": [
            "Change your Dailymotion password",
            "Contact privacy@dailymotion.com for data deletion"
        ]
    },
    "Tumblr": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Tumblr",
        "url": "https://www.tumblr.com/settings/account",
        "steps": [
            "Change your Tumblr password",
            "Enable two-factor authentication",
            "Review connected apps"
        ]
    },
    "Zynga": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Zynga",
        "url": "https://www.zynga.com/privacy/",
        "steps": [
            "Change your Zynga password",
            "Review connected social accounts",
            "Submit deletion request via privacy portal if needed"
        ]
    },
    "Bitly": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Bitly",
        "url": "https://app.bitly.com/settings/",
        "steps": [
            "Change your Bitly password",
            "Enable two-factor authentication",
            "Review API access tokens"
        ]
    },
    "Disqus": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Disqus",
        "url": "https://disqus.com/home/settings/",
        "steps": [
            "Change your Disqus password",
            "Review account settings",
            "Delete account if no longer needed"
        ]
    },
    "Imgur": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Imgur",
        "url": "https://imgur.com/account/settings",
        "steps": [
            "Change your Imgur password",
            "Enable two-factor authentication",
            "Review connected apps"
        ]
    },
    "Kickstarter": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Kickstarter",
        "url": "https://www.kickstarter.com/settings/account",
        "steps": [
            "Change your Kickstarter password",
            "Enable two-factor authentication",
            "Review saved payment methods"
        ]
    },
    "Last.fm": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Last.fm",
        "url": "https://www.last.fm/settings",
        "steps": [
            "Change your Last.fm password",
            "Review connected applications"
        ]
    },
    "Patreon": {
        "action_type": "account_security",
        "priority": "high",
        "company": "Patreon",
        "url": "https://www.patreon.com/settings/security",
        "steps": [
            "Change your Patreon password immediately",
            "Enable two-factor authentication",
            "Review payment methods and subscriptions",
            "Check connected social accounts"
        ]
    },
    "Snapchat": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Snapchat",
        "url": "https://accounts.snapchat.com/accounts/login",
        "steps": [
            "Change your Snapchat password",
            "Enable two-factor authentication",
            "Review connected devices"
        ]
    },
    "Spotify": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Spotify",
        "url": "https://www.spotify.com/account/",
        "steps": [
            "Change your Spotify password",
            "Click 'Sign out everywhere'",
            "Review connected apps",
            "Check Family/Duo members if applicable"
        ]
    },
    "Trello": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "Trello",
        "url": "https://trello.com/your/account",
        "steps": [
            "Change your Trello password",
            "Enable two-factor authentication",
            "Review Power-Ups and connected apps",
            "Check team/workspace access"
        ]
    },
    "Dubsmash": {
        "action_type": "account_deletion",
        "priority": "low",
        "company": "Dubsmash",
        "url": "https://dubsmash.com/",
        "steps": [
            "Service was acquired by Reddit",
            "Delete your Dubsmash account if still accessible",
            "Change password if you used it elsewhere"
        ]
    },
    "Evite": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Evite",
        "url": "https://www.evite.com/account",
        "steps": [
            "Change your Evite password",
            "Review account settings",
            "Delete account if no longer needed"
        ]
    },
    "Houzz": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Houzz",
        "url": "https://www.houzz.com/user/settings",
        "steps": [
            "Change your Houzz password",
            "Review connected accounts",
            "Update profile privacy settings"
        ]
    },
    "MyFitnessPal": {
        "action_type": "account_security",
        "priority": "medium",
        "company": "MyFitnessPal",
        "url": "https://www.myfitnesspal.com/account",
        "steps": [
            "Change your MyFitnessPal password",
            "Review connected apps and devices",
            "Check diary privacy settings"
        ]
    },
    "Wattpad": {
        "action_type": "account_security",
        "priority": "low",
        "company": "Wattpad",
        "url": "https://www.wattpad.com/settings",
        "steps": [
            "Change your Wattpad password",
            "Enable two-factor authentication",
            "Review account privacy settings"
        ]
    }
}

# API endpoint for breach-specific actions
@app.route("/api/removal/breach-actions", methods=["POST"])
@csrf.exempt
def api_breach_actions():
    """
    Given a list of breach names, return matching remediation actions.
    Only returns actions for breaches that have specific remediation steps.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    breaches = data.get("breaches", [])

    if not isinstance(breaches, list):
        return jsonify({"error": "breaches must be a list"}), 400

    # Find matching actions for the provided breach names
    matched_actions = []
    for breach_name in breaches:
        # Try exact match first
        if breach_name in BREACH_ACTIONS:
            action = BREACH_ACTIONS[breach_name].copy()
            action["breach_name"] = breach_name
            matched_actions.append(action)
        else:
            # Try case-insensitive match
            for key in BREACH_ACTIONS:
                if key.lower() == breach_name.lower():
                    action = BREACH_ACTIONS[key].copy()
                    action["breach_name"] = breach_name
                    matched_actions.append(action)
                    break

    # Sort by priority (high > medium > low)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    matched_actions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    return jsonify({
        "actions": matched_actions,
        "total_breaches": len(breaches),
        "matched_count": len(matched_actions)
    })


#Inshaal - XposedOrNot API Proxy (FREE email breach checking)
@app.route("/api/check-breach", methods=["POST"])
@csrf.exempt  # Exempt from CSRF - uses session auth + JSON body
def check_breach():
    """
    Backend proxy for XposedOrNot API.
    FREE API - no API key required.
    Avoids CORS issues by making the API call server-side.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    email = data.get("email", "").strip().lower() if data else ""

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Basic email validation
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Invalid email format"}), 400

    try:
        api_url = f"https://api.xposedornot.com/v1/check-email/{email}"
        headers = {
            "User-Agent": "FootprintApp/1.0"
        }

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 404:
            # No breaches found - this is good news
            return jsonify({"breaches": [], "email": email, "breached": False}), 200
        elif response.status_code == 429:
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
        elif response.status_code == 200:
            # XposedOrNot returns: {"breaches": [["Adobe", "LinkedIn", ...]]}
            data = response.json()
            # Extract breaches from nested array
            breaches_list = data.get("breaches", [[]])
            breach_names = breaches_list[0] if breaches_list and len(breaches_list) > 0 else []
            return jsonify({
                "breaches": breach_names,
                "email": email,
                "breached": len(breach_names) > 0,
                "breach_count": len(breach_names)
            }), 200
        else:
            return jsonify({"error": f"API error: {response.status_code}"}), 502

    except requests.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except requests.RequestException as e:
        return jsonify({"error": "Unable to check breaches at this time."}), 503


#Inshaal - Pwned Passwords API (k-anonymity model)
@app.route("/api/check-password", methods=["POST"])
@csrf.exempt  # Exempt from CSRF - uses session auth + JSON body
def check_password_pwned():
    """
    Check if password has been exposed in data breaches.
    Uses k-anonymity: only first 5 chars of SHA-1 hash are sent to API.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    password = data.get("password", "") if data else ""

    if not password:
        return jsonify({"error": "Password is required"}), 400

    try:
        # Hash password with SHA-1 (only for breach checking, NOT storage)
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        # Query HIBP Pwned Passwords API (no API key needed)
        api_url = f"https://api.pwnedpasswords.com/range/{prefix}"
        headers = {"User-Agent": "FootprintApp/1.0"}

        response = requests.get(api_url, headers=headers, timeout=5)

        if response.status_code == 200:
            # Parse response - each line is "HASH_SUFFIX:COUNT"
            for line in response.text.splitlines():
                if ':' not in line:
                    continue
                hash_suffix, count = line.split(':', 1)
                if suffix == hash_suffix:
                    count = int(count)
                    # Determine severity
                    if count > 100000:
                        severity = "critical"
                    elif count > 10000:
                        severity = "high"
                    elif count > 1000:
                        severity = "medium"
                    else:
                        severity = "low"

                    return jsonify({
                        "breached": True,
                        "count": count,
                        "severity": severity,
                        "message": f"This password has been exposed {count:,} times in data breaches."
                    })

            # Password not found in breaches
            return jsonify({
                "breached": False,
                "count": 0,
                "message": "This password has not been found in known data breaches."
            })
        else:
            return jsonify({"error": f"API error: {response.status_code}"}), 502

    except requests.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except requests.RequestException:
        return jsonify({"error": "Unable to check password at this time."}), 503
    

#Trung Nguyen
# ===== URL Reviews API (store + fetch + summaries) =====

@app.route("/api/url-reviews", methods=["POST"])
@csrf.exempt
def api_create_url_review():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    rating = data.get("rating")
    comment = (data.get("comment") or "").strip()

    if not url:
        return jsonify({"error": "url is required"}), 400
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "rating must be an integer 1-5"}), 400
    if len(comment) < 3:
        return jsonify({"error": "comment must be at least 3 characters"}), 400

    r = UrlReview(
        user_id=session["user_id"],
        url=url,
        rating=rating,
        comment=comment
    )
    db.session.add(r)
    db.session.commit()

    return jsonify({"ok": True})


@app.route("/api/url-reviews", methods=["GET"])
def api_get_url_reviews():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    url = (request.args.get("url") or "").strip()
    if not url:
        return jsonify({"error": "url is required"}), 400

    # optional limit
    try:
        limit = int(request.args.get("limit") or "50")
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 200))

    # join to get usernames
    rows = (db.session.query(UrlReview, User.username)
            .join(User, UrlReview.user_id == User.id)
            .filter(UrlReview.url == url)
            .order_by(UrlReview.created_at.desc())
            .limit(limit)
            .all())

    # summary stats
    avg_row = (db.session.query(db.func.avg(UrlReview.rating), db.func.count(UrlReview.id))
               .filter(UrlReview.url == url)
               .first())
    avg_rating = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0.0
    count = int(avg_row[1]) if avg_row and avg_row[1] is not None else 0

    return jsonify({
        "url": url,
        "avg_rating": round(avg_rating, 2),
        "review_count": count,
        "reviews": [
            {
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "username": username
            }
            for (r, username) in rows
        ]
    })


@app.route("/api/url-review-summaries", methods=["POST"])
@csrf.exempt
def api_url_review_summaries():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    urls = data.get("urls", [])

    if not isinstance(urls, list):
        return jsonify({"error": "urls must be a list"}), 400

    # sanitize + unique
    clean_urls = []
    seen = set()
    for u in urls:
        if not isinstance(u, str):
            continue
        u = u.strip()
        if not u or u in seen:
            continue
        seen.add(u)
        clean_urls.append(u)

    if not clean_urls:
        return jsonify({"summaries": {}})

    rows = (db.session.query(
                UrlReview.url,
                db.func.avg(UrlReview.rating),
                db.func.count(UrlReview.id)
            )
            .filter(UrlReview.url.in_(clean_urls))
            .group_by(UrlReview.url)
            .all())

    summary_map = {u: {"avg": 0.0, "count": 0} for u in clean_urls}
    for (u, avg, cnt) in rows:
        summary_map[u] = {
            "avg": float(avg) if avg is not None else 0.0,
            "count": int(cnt) if cnt is not None else 0
        }

    return jsonify({"summaries": summary_map})


#Terry added

@app.route("/scan", methods=["POST"])
def scan():
    domain = request.form["domain"]
    log_activity("run_scan", domain)
    return redirect(url_for("dashboard"))
    # scan logic here

@app.teardown_appcontext
def close_db(exception=None):
    db_conn = g.pop("db", None)

    if db_conn is not None:
        db_conn.close()

#Terry added

# --- NEW SCANNER ROUTE ---
@app.route("/api/scan-url", methods=["POST"])
@csrf.exempt
def scan_url():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    url = data.get("url", "")
    
    # This calls the helper function
    is_blocked, owner, score = check_domain_safety(url)
    
    return jsonify({
        "url": url,
        "is_tracker": is_blocked,
        "owner": owner,
        "risk_score": score,
        "message": f"Caution: This domain is owned by {owner}" if is_blocked else "Low risk."
    })

def calculate_refined_score(tracker_data):
    base_score = 1
    # Add points based on what the tracker is known for
    if tracker_data.get('category') == 'fingerprinting':
        base_score += 6
    if tracker_data.get('category') == 'ads':
        base_score += 4
    if tracker_data.get('category') == 'session_replay':
        base_score += 8  # Very high risk (records mouse movements)
        
    return min(base_score, 10) # Cap it at 10

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)

