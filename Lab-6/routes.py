from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import mysql, bcrypt, login_manager
from models import User, get_user_by_id
from forms import RegistrationForm, LoginForm

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
        if request.is_json:  # Handling Postman JSON request
            data = request.get_json()
            if not data or "username" not in data or "email" not in data or "password" not in data or "confirm_password" not in data:
                return jsonify({"message": "Missing required fields"}), 400

            if data['password'] != data['confirm_password']:
                return jsonify({"message": "Passwords do not match"}), 400

            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (data['username'], data['email'], hashed_password))
            mysql.connection.commit()
            cur.close()
            return jsonify({"message": "Account created successfully!"}), 201

        elif form.validate_on_submit():  # Handling HTML form request
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (form.username.data, form.email.data, hashed_password))
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
        if request.is_json:  # If request is from Postman (API)
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

        elif form.validate_on_submit():  # If request is from an HTML form
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


# ---------------------- DASHBOARD ROUTE ---------------------- #
@app.route('/dashboard')
@login_required
def dashboard():
    if request.is_json:  # If request is from Postman (API)
        return jsonify({
            "message": "Welcome to the dashboard!",
            "username": current_user.username,
            "email": current_user.email
        }), 200

    return render_template('dashboard.html', user=current_user)


# ---------------------- LOGOUT ROUTE ---------------------- #
@app.route('/logout')
@login_required
def logout():
    logout_user()

    if request.is_json:  # If request is from Postman (API)
        return jsonify({"message": "You have been logged out."}), 200

    return redirect(url_for('login'))
