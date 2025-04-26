from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os
import certifi
import ssl


# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

SECRET_KEY = os.getenv("SECRET_KEY")

print("DEBUG: MONGO_URI =", MONGO_URI)
print("DEBUG: SECRET_KEY =", SECRET_KEY)

# Initialize the Flask app
app = Flask(__name__)
# MongoDB Configuration
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set. Please check your .env file.")
else:
    print("mongodb connected succesfully")

app.config["MONGO_URI"] = MONGO_URI
app.config['SECRET_KEY'] = SECRET_KEY or "defaultsecret"

# Initialize PyMongo with certifi CA bundle

mongo = PyMongo(app, uri=MONGO_URI, tls=True, tlsCAFile=certifi.where())
# Home Route
@app.route('/')
def index():
    if 'username' in session:
        students = mongo.db.students.find()
        student_list = [{**s, '_id': str(s['_id'])} for s in students]
        return render_template('index.html', students=student_list, username=session['username'])
    return redirect(url_for('landing_page'))

# Landing Page
@app.route('/landing')
def landing_page():
    return render_template('landing_page.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        if mongo.db.studtrack.find_one({'username': username}):
            flash("Username already exists, please choose another one.", "danger")
            return redirect(url_for('register'))

        mongo.db.studtrack.insert_one({'username': username, 'password': hashed_password})
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('landing_page'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = mongo.db.studtrack.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials, please try again.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('landing_page'))

# Add Student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'username' in session:
        if request.method == 'POST':
            name = request.form.get('name')
            subject = request.form.get('subject')
            grade = request.form.get('grade')

            mongo.db.students.insert_one({
                'name': name,
                'subject': subject,
                'grade': grade,
                'added_by': session['username'],
                'created_at': datetime.utcnow()
            })
            flash("Student added successfully!", "success")
            return redirect(url_for('index'))

        return render_template('add_student.html')
    return redirect(url_for('landing_page'))

# Edit Student
@app.route('/edit/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))

    student = mongo.db.students.find_one({'_id': ObjectId(student_id)})

    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        grade = request.form.get('grade')

        mongo.db.students.update_one(
            {'_id': ObjectId(student_id)},
            {'$set': {'name': name, 'subject': subject, 'grade': grade}}
        )
        flash("Student updated successfully!", "success")
        return redirect(url_for('index'))

    student['_id'] = str(student['_id'])
    return render_template('edit_student.html', student=student)

# Delete Student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    if 'username' not in session:
        return redirect(url_for('landing_page'))

    mongo.db.students.delete_one({'_id': ObjectId(student_id)})
    flash("Student deleted successfully!", "success")
    return redirect(url_for('index'))

# 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

print(mongo.db.list_collection_names())

# Run the app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
