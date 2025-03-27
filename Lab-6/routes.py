from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import mysql, bcrypt, login_manager
from models import User, get_user_by_id
from forms import RegistrationForm, LoginForm, UpdateProfileForm, ResetPasswordForm

app = Flask(__name__)
app.config.from_object('config.Config')

mysql.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


# ---------------------- REGISTER ROUTE ---------------------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            # Validate input data
            required_fields = ["username", "email", "password", "confirm_password", "subject", "grade"]
            if not all(field in data for field in required_fields):
                return jsonify({"message": "Missing required fields"}), 400

            if data['password'] != data['confirm_password']:
                return jsonify({"message": "Passwords do not match"}), 400

            if len(data['grade']) > 2:
                return jsonify({"message": "Grade must be at most 2 characters"}), 400

            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            cur = mysql.connection.cursor()

            # Insert user data
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (data['username'], data['email'], hashed_password))

            user_id = cur.lastrowid  # Get new user ID

            # Insert subject and grade
            cur.execute("INSERT INTO grades (user_id, subject, grade) VALUES (%s, %s, %s)",
                        (user_id, data['subject'], data['grade']))

            mysql.connection.commit()
            cur.close()

            return jsonify({"message": "Account created successfully!"}), 201

        elif form.validate_on_submit():
            if form.password.data != form.confirm_password.data:
                flash('Passwords do not match.', 'danger')
                return render_template('register.html', form=form)

            if len(form.grade.data) > 2:
                flash('Grade must be at most 2 characters.', 'danger')
                return render_template('register.html', form=form)

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            cur = mysql.connection.cursor()

            # Insert user data
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (form.username.data, form.email.data, hashed_password))

            user_id = cur.lastrowid  # Get new user ID

            # Insert subject and grade
            cur.execute("INSERT INTO grades (user_id, subject, grade) VALUES (%s, %s, %s)",
                        (user_id, form.subject.data, form.grade.data))

            mysql.connection.commit()
            cur.close()

            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ---------------------- LOGIN ROUTE ---------------------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if not data or "email" not in data or "password" not in data:
                return jsonify({"message": "Missing email or password"}), 400

            cur = mysql.connection.cursor()
            cur.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (data['email'],))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.check_password_hash(user[3], data['password']):
                login_user(User(user[0], user[1], user[2]))
                return jsonify({"message": "Login successful!", "user_id": user[0]}), 200
            else:
                return jsonify({"message": "Invalid email or password"}), 401

        elif form.validate_on_submit():
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (form.email.data,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.check_password_hash(user[3], form.password.data):
                login_user(User(user[0], user[1], user[2]))
                return redirect(url_for('dashboard'))
            else:
                flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html', form=form)


# ---------------------- UPDATE PROFILE ROUTE ---------------------- #
@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()

    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s, email = %s WHERE id = %s",
                    (form.username.data, form.email.data, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_profile.html', form=form, user=current_user)


# ---------------------- RESET PASSWORD ROUTE ---------------------- #
@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        if form.new_password.data != form.confirm_password.data:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', form=form)

        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('reset_password.html', form=form)


# ---------------------- VIEW GRADES ROUTE (READ-ONLY) ---------------------- #
@app.route('/grades')
@login_required
def view_grades():
    cur = mysql.connection.cursor()
    cur.execute("SELECT marks FROM grades WHERE user_id = %s", (current_user.id,))
    marks = cur.fetchone()
    cur.close()

    if request.is_json:
        return jsonify({"marks": marks[0] if marks else "No marks available"}), 200

    return render_template('grades.html', marks=marks[0] if marks else "No marks available")


# ---------------------- DASHBOARD ROUTE ---------------------- #
@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    # Fetch all subjects and grades for the current user
    cur.execute("SELECT subject, grade FROM grades WHERE user_id = %s", (current_user.id,))
    grades = cur.fetchall()  # Fetch all records

    cur.close()

    return render_template('dashboard.html', user=current_user, grades=grades)


# ---------------------- LOGOUT ROUTE ---------------------- #
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
