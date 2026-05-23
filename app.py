"""
Atanu Das — Portfolio
─────────────────────
Local:   python app.py  →  opens http://localhost:5000
Render:  gunicorn app:app
"""

import os, json, smtplib, threading, webbrowser, uuid
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, render_template, jsonify, request, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER   = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXT     = {"pdf", "png", "jpg", "jpeg", "webp"}
MAX_CONTENT_MB  = 10
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Persistent posts stored as JSON on disk (works fine for Render free tier)
POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE) as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)

# ── Static data ───────────────────────────────────────────────────────────────

PROFILE = {
    "name": "Atanu Das",
    "title": "Risk & Compliance Consultant",
    "company": "Protiviti",
    "tagline": "Turning data into risk intelligence — credit models, fraud analytics & AI-powered compliance.",
    "location": "Mumbai, India",
    "email": "atanu.das1729@gmail.com",
    "phone": "+91 9775591457",
    "linkedin": "https://www.linkedin.com/in/atanudas1729",
    "medium": "https://medium.com/@atanu.das1729",
}

EXPERIENCE = [
    {
        "role": "Consultant – Risk & Compliance",
        "company": "Protiviti India Member Firm",
        "period": "Aug 2025 – Present",
        "location": "Mumbai, India",
        "highlights": [
            "IFRS 9 end-to-end: PIT PD estimation, Z-score modelling, macroeconomic regression, Lifetime ECL across multiple economic scenarios.",
            "Model validation using AUC-ROC, Gini, KS Statistics, WoE, IV, PSI and CSI stability measures.",
            "Built AI-powered MRM Findings Library using NLP & GenAI — reduced manual effort by 40–60%.",
            "Kotak Mahindra Bank: mule account linkage analysis across NEFT, RTGS, IMPS, UPI and Payment Gateway channels.",
            "Fraud monitoring via Falcon (Credit Card) and Clari 5 alerts across CC, DC, Net Banking, Mobile Banking and UPI.",
            "Branch-level & PIN-code hotspot fraud analysis for Kotak 811 / Non-811 accounts — Q1–Q3 FY26.",
        ],
    },
    {
        "role": "BI Developer Associate",
        "company": "Workmates Core2Cloud Solution Ltd",
        "period": "Sep 2024 – May 2025",
        "location": "Kolkata, India",
        "highlights": [
            "Scalable AI/ML solutions on AWS: SageMaker, Textract, Rekognition, Lex, Translate and Bedrock.",
            "ML-based resume screening system improving shortlisting efficiency across multiple job roles.",
            "Advanced OCR pipelines for Aadhaar, PAN, salary slips and bank statements (EasyOCR + Tesseract + OpenCV).",
            "Interactive dashboards on AWS QuickSight for business intelligence.",
        ],
    },
    {
        "role": "Data Scientist – Credit Risk",
        "company": "Roopya (Geoalgo Technologies Pvt. Ltd.)",
        "period": "Jul 2023 – Sep 2024",
        "location": "Kolkata, India",
        "highlights": [
            "Built PD models and credit scorecards leveraging payment behaviour and macroeconomic factors.",
            "Designed and deployed real-time APIs for PD and scorecard outputs.",
            "Coverage: PD, LGD, EAD, ECL under IFRS 9; TTC PD, RAROC and Stress Testing.",
            "Cross-sell analytics and data segmentation for loan portfolio clients.",
        ],
    },
]

SKILLS = {
    "Credit Risk":    ["PD Modelling","LGD","EAD","ECL","IFRS 9","Scorecards","RAROC","Stress Testing"],
    "Fraud Risk":     ["Mule Account Detection","Transaction Monitoring","Fraud Analytics","Falcon","Clari 5"],
    "Machine Learning":["Logistic Regression","Random Forest","XGBoost","PCA","LDA","Clustering","NLP","LLM / GenAI"],
    "Cloud & Tools":  ["AWS SageMaker","AWS Bedrock","GCP BigQuery","Vertex AI","Power BI","Superset","QuickSight"],
    "Programming":    ["Python","SQL","NumPy","Pandas","Scikit-learn","Streamlit","Seaborn","Matplotlib"],
    "Statistics":     ["Probability Distributions","Hypothesis Testing","Inferential Statistics","Time Series"],
}

EDUCATION = [
    {"degree":"Post-Graduate Diploma in Statistical Methods & Analytics","institution":"Indian Statistical Institute, Kolkata","year":"2022 – 2023","grade":"First Division"},
    {"degree":"M.Sc Applied Mathematics (Computational & Applied)","institution":"West Bengal State University","year":"2019 – 2021","grade":"CGPA 8.91 / 10"},
    {"degree":"M.Tech in Data Science","institution":"MAKAUT, West Bengal","year":"2021 – 2022","grade":""},
    {"degree":"B.Sc in Mathematics","institution":"Rahara RKM Vivekananda Centenary College","year":"2016 – 2019","grade":""},
]

CERTIFICATIONS = [
    "Second Winter School on Deep Learning (WSDL) — ISI Kolkata, 2023",
    "Developing Credit Risk Scorecard using SAS — 2023",
    "Credit Risk Modeling in Python — 2023",
    "BOOTCAMP – Credit Risk Modeling, Peaks2Tails Industrial Training",
    "Credit Risk Scorecard — Automating Credit Decision, K2 Analytics",
    "Quantitative Finance & Algorithmic Trading in Python — 2025",
    "McKinsey.org Forward Program — 2025",
    "Complete Generative AI Course with LangChain & HuggingFace — 2025",
    "AWS Cloud Practitioner Essentials — 2024",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/profile")
def api_profile():
    return jsonify(PROFILE)

@app.route("/api/experience")
def api_experience():
    return jsonify(EXPERIENCE)

@app.route("/api/skills")
def api_skills():
    return jsonify(SKILLS)

@app.route("/api/education")
def api_education():
    return jsonify(EDUCATION)

@app.route("/api/certifications")
def api_certs():
    return jsonify(CERTIFICATIONS)

# ── Posts / Blog ──────────────────────────────────────────────────────────────

@app.route("/api/posts", methods=["GET"])
def get_posts():
    return jsonify(load_posts())

@app.route("/api/posts", methods=["POST"])
def create_post():
    """
    Multipart form:
      title    (required)
      summary  (required)
      tag      e.g. "Credit Risk", "Research", "Tutorial"
      file     optional PDF or image
    Protected by ADMIN_KEY env var. Pass header:  X-Admin-Key: <your-key>
    """
    admin_key = os.getenv("ADMIN_KEY", "")
    if admin_key and request.headers.get("X-Admin-Key") != admin_key:
        abort(401)

    title   = request.form.get("title","").strip()
    summary = request.form.get("summary","").strip()
    tag     = request.form.get("tag","Article").strip()

    if not title or not summary:
        return jsonify({"success": False, "message": "Title and summary are required."}), 400

    file_url = None
    file_type = None
    f = request.files.get("file")
    if f and f.filename and allowed(f.filename):
        ext      = f.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        f.save(os.path.join(UPLOAD_FOLDER, filename))
        file_url  = f"/static/uploads/{filename}"
        file_type = "pdf" if ext == "pdf" else "image"

    posts = load_posts()
    post  = {
        "id":       uuid.uuid4().hex[:8],
        "title":    title,
        "summary":  summary,
        "tag":      tag,
        "file_url": file_url,
        "file_type":file_type,
        "date":     datetime.utcnow().strftime("%b %d, %Y"),
    }
    posts.insert(0, post)
    save_posts(posts)
    return jsonify({"success": True, "post": post})

@app.route("/api/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    admin_key = os.getenv("ADMIN_KEY", "")
    if admin_key and request.headers.get("X-Admin-Key") != admin_key:
        abort(401)
    posts = [p for p in load_posts() if p["id"] != post_id]
    save_posts(posts)
    return jsonify({"success": True})

@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ── Profile Photo ─────────────────────────────────────────────────────────────

PHOTO_FILE = os.path.join(os.path.dirname(__file__), "static", "uploads", "profile_photo.meta")

def get_profile_photo():
    if os.path.exists(PHOTO_FILE):
        with open(PHOTO_FILE) as f:
            return f.read().strip()
    return None

def set_profile_photo(url):
    with open(PHOTO_FILE, "w") as f:
        f.write(url)

@app.route("/api/profile-photo")
def api_profile_photo():
    url = get_profile_photo()
    return jsonify({"url": url})

@app.route("/api/profile-photo", methods=["POST"])
def upload_profile_photo():
    f = request.files.get("photo")
    if not f or not f.filename:
        return jsonify({"success": False, "message": "No file provided."}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"png", "jpg", "jpeg", "webp"}:
        return jsonify({"success": False, "message": "Invalid file type."}), 400
    filename = f"profile.{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    # Remove old profile photos
    for old_ext in ["png","jpg","jpeg","webp"]:
        old = os.path.join(UPLOAD_FOLDER, f"profile.{old_ext}")
        if os.path.exists(old) and old != path:
            os.remove(old)
    f.save(path)
    url = f"/static/uploads/{filename}?v={uuid.uuid4().hex[:6]}"
    set_profile_photo(url)
    return jsonify({"success": True, "url": url})

# ── Contact ───────────────────────────────────────────────────────────────────

@app.route("/contact", methods=["POST"])
def contact():
    data    = request.get_json(force=True)
    name    = data.get("name","").strip()
    email   = data.get("email","").strip()
    subject = data.get("subject","").strip()
    message = data.get("message","").strip()

    if not all([name, email, subject, message]):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    mail_to   = os.getenv("MAIL_TO", PROFILE["email"])

    if smtp_host and smtp_user and smtp_pass:
        try:
            body = f"Name:    {name}\nEmail:   {email}\n\n{message}"
            msg  = MIMEText(body)
            msg["Subject"] = f"[Portfolio] {subject}"
            msg["From"]    = smtp_user
            msg["To"]      = mail_to
            with smtplib.SMTP(smtp_host, smtp_port) as s:
                s.starttls()
                s.login(smtp_user, smtp_pass)
                s.sendmail(smtp_user, mail_to, msg.as_string())
        except Exception as exc:
            print(f"[EMAIL ERROR] {exc}")
            return jsonify({"success": False, "message": "Email failed. Please try again."}), 500
    else:
        print(f"\n{'='*50}\n  FROM: {name} <{email}>\n  SUBJECT: {subject}\n  MSG: {message}\n{'='*50}\n")

    return jsonify({"success": True, "message": "Message received! I'll get back to you soon."})

# ── Launch ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:5000")).start()
    print("\n  ✅  Portfolio → http://localhost:5000\n  Ctrl+C to stop.\n")
    app.run(debug=False, port=5000)
