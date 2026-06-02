import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from model import predict_act
from translator import translate_to_english
from languages import translations
from datetime import datetime
from authority_map import authority_locations

app = Flask(__name__)
app.secret_key = "supersecretkey"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


# ---------------- DATABASE INIT ---------------- #
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        issue TEXT,
        act TEXT,
        authority TEXT,
        feedback TEXT,
        created_at TEXT
    )
    """)
def fix_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Check columns
    cursor.execute("PRAGMA table_info(records)")
    columns = [col[1] for col in cursor.fetchall()]

    # Add location if missing
    if "location" not in columns:
        cursor.execute("ALTER TABLE records ADD COLUMN location TEXT")

    conn.commit()
    conn.close()

init_db()
fix_db()   # ✅ ADD THIS LINE
    

# ---------------- LANGUAGE HELPER ---------------- #

def get_text():
    lang = session.get('lang', 'english')
    return translations.get(lang, translations['english'])


@app.route('/set_language', methods=['POST'])
def set_language():
    selected_lang = request.form['language']
    session['lang'] = selected_lang
    return redirect(request.referrer)


# ---------------- LOGIN ---------------- #

@app.route('/')
def login():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(DISTINCT user) FROM records")
    user_count = cursor.fetchone()[0]

    conn.close()

    return render_template("login.html", text=get_text(), user_count=user_count)

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    session['username'] = username

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['role'] = "admin"
        return redirect('/admin')

    session['role'] = "user"
    return redirect('/welcome')
# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():
    return render_template("user_dashboard.html", text=get_text())


# ---------------- PREDICTION ---------------- #
@app.route('/predict', methods=['POST'])
def predict():
    from datetime import datetime
    print("SYSTEM TIME:", datetime.now())

    issue = request.form['issue']
    location = request.form['location']
    language = session.get('lang', 'english')

    if language != "english":
        issue = translate_to_english(issue)

    # ML prediction
    result = predict_act(issue)

    authority = result["authority"]

    # Take first authority if multiple exist
    main_authority = authority.split(";")[0].strip()

    # Create dynamic map search
    map_location = f"{main_authority} office {location}"

    # Generate system time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
INSERT INTO records
(user, issue, act, authority, feedback, created_at, location)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    session['username'],
    issue,
    result["act"],
    result["authority"],
    "",
    current_time,
    location   # ✅ added
))

    conn.commit()
    record_id = cursor.lastrowid
    conn.close()

    session['record_id'] = record_id

    return render_template(
        "result.html",
        result=result,
        map_location=map_location,
        text=get_text()
    )

    
 # ---------------- FEEDBACK ---------------- #
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == "POST":
        fb = request.form['feedback']
        record_id = session.get('record_id')

        if record_id:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE records
                SET feedback = ?
                WHERE id = ?
            """, (fb, record_id))

            conn.commit()
            conn.close()

        return redirect('/thanks')

    return render_template("feedback.html")   # ✅ IMPORTANT FIX
# ---------------- ADMIN ---------------- #
@app.route('/admin')
def admin():
    if session.get("role") != "admin":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user, issue, act, authority, feedback, created_at, location
        FROM records
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", records=rows, text=get_text())

@app.route('/welcome')
def welcome():
    return render_template("welcome.html")


@app.route('/delete/<int:record_id>')
def delete_record(record_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/thanks')
def thanks():
    return render_template("thanks.html", text=get_text())


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == "__main__":
    app.run(debug=True)