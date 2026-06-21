from flask import Flask, render_template, redirect, request, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
import datetime
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

def get_db_connection ():
   conn = mysql.connector.connect(
        user='root',
        host= 'localhost',
        password = '',
        database = 'mbdtech'

) 
   return conn

# # =========================
# # App setup
# # =========================
app = Flask(__name__)
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_DEBUG'] = True
app.secret_key = os.environ.get('SECRET_KEY')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        identifier = request.form['identifier']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user from DB (username OR email)
        cursor.execute("""
            SELECT * FROM users
            WHERE (username=%s OR email=%s)
        """, (identifier, identifier))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        # Check user + password hash
        if user and check_password_hash(user['password'], password):

            # Session create
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']

            flash("Login Successful!")

            # Admin redirect
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))

            # User redirect
            return redirect(url_for('user_dashboard'))

        else:
            flash("Incorrect Username or Password!")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        phone = request.form['phone']
        cnic = request.form['cnic']

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        # Check existing user
        cursor.execute(
            "SELECT * FROM users WHERE email=%s OR username=%s",
            (email, username)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            flash("User already exists!")

            cursor.close()
            conn.close()

            return redirect(url_for('register'))

        # Insert new user
        cursor.execute("""
            INSERT INTO users
            (username, email, password, phone, cnic, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, email, password, phone, cnic, 'user'))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Registration Successful!")

        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/user_dashboard' , methods=['GET' , 'POST'])
def user_dashboard():

     if 'user_id' not in session or session.get('role') != 'user':

        flash('Please login first', 'warning')

        return redirect(url_for('login'))
     
     conn = get_db_connection()

     cursor = conn.cursor(dictionary=True)

     cursor.execute(
         "SELECT * FROM users WHERE id=%s",
         (session['user_id'],)
     )

     user_data = cursor.fetchone()

     cursor.close()
     conn.close()

     return render_template(
         'user_dashboard.html',
         user=user_data
     )
@app.route('/admin_dashboard')
def admin_dashboard():

    # Check admin login
    if 'user_id' not in session or session.get('role') != 'admin':

        flash("Admin login required!")

        return redirect(url_for('login'))

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    # Example dashboard data
    cursor.execute(
        "SELECT COUNT(*) AS total_users FROM users"
    )

    total_users = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users
    )
@app.route('/profile')
def profile():

    # Check login
    if 'user_id' not in session:

        flash("Please login first!")
        return redirect(url_for('login'))

    # Database connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch logged-in user data
    cursor.execute("""
        SELECT * FROM users
        WHERE id=%s
    """, (session['user_id'],))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # If user not found
    if not user:

        flash("User not found!")
        return redirect(url_for('logout'))

    # Render profile page
    return render_template(
        'profile.html',
        user=user
    )
                       

@app.route('/admin/user')
def admin_user():
    if 'role' not in session or session ['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_user.html')

@app.route('/admin/projects', methods=['GET', 'POST'])
def admin_projects():

    # Admin check
    if 'role' not in session or session['role'] != 'admin':

        return redirect(url_for('login'))

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    # Add project
    if request.method == 'POST':

        project_name = request.form['project_name']

        description = request.form['description']

        cursor.execute("""
            INSERT INTO projects
            (project_name, description)
            VALUES (%s, %s)
        """, (project_name, description))

        conn.commit()

        flash("Project added successfully!")

    # Show projects
    cursor.execute("SELECT * FROM projects")

    projects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin_projects.html',
        projects=projects
    )
@app.route('/admin/view_messages')
def admin_messages():

    # Admin check
    if 'role' not in session or session['role'] != 'admin':

        return redirect(url_for('login'))

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    # Fetch feedback messages
    cursor.execute("""
        SELECT * FROM feedbacks
    """)

    feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin_messages.html',
        feedbacks=feedbacks
    )
@app.route('/admin/setting')
def admin_settings():
    if 'role' not in session or session['role'] != 'admin':
      return redirect(url_for('login'))
    return render_template('admin_setting.html')

@app.route('/admin/manage_users/<int:user_id>')
def admin_users(user_id):

    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "DELETE FROM users WHERE id=%s",
        (user_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("User deleted successfully!")

    return redirect(url_for('admin_user'))
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        user_message = request.form['message']

        msg = Message(
            subject=f"New Contact Form: {subject}",
            sender='kinza.sharif8@gmail.com',
            recipients=['kinza.sharif8@gmail.com']
        )

        msg.body = f"""
Name: {name}

Email: {email}

Subject: {subject}

Message:
{user_message}
"""

        mail.send(msg)

        flash("Message Sent Successfully!")

        return redirect(url_for('contact'))

    return render_template('contact.html')
@app.route('/services')
def services():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM services
        """)

        services_data = cursor.fetchall()

    except Exception as e:
        print("Error fetching services:", e)
        services_data = []

    finally:
        cursor.close()
        conn.close()

    return render_template('services.html', services=services_data)

           
# =========================
# Logout
# =========================
@app.route('/logout')
def logout():

    session.clear()

    flash("Logged out successfully!")

    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)