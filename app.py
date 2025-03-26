import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.sql import func
from auth_config import users  # Import credentials

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Debug: Show registered routes
print("📌 Registered Routes:")
for rule in app.url_map.iter_rules():
    print(f"🔹 {rule} → {rule.endpoint}")

@auth.verify_password
def verify_password(username, password):
    print(f"🛠️ Attempting Login: {username}")  # Debug log
    if username in users and users[username] == password:
        print("✅ Login Success!")
        return username
    print("❌ Unauthorized Access!")
    return None  # Authentication failed

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    bio = db.Column(db.Text)

    def __repr__(self):
        return f'<Student {self.firstname}>'

@app.route('/')
@auth.login_required
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/<int:student_id>/')
@auth.login_required
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', student=student)

@app.route('/<int:student_id>/edit/', methods=['GET', 'POST'])
@auth.login_required
def edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.firstname = request.form['firstname']
        student.lastname = request.form['lastname']
        student.email = request.form['email']
        student.age = int(request.form['age'])
        student.bio = request.form['bio']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', student=student)

@app.route('/<int:student_id>/delete/', methods=['POST'])
@auth.login_required
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/create/', methods=['GET', 'POST'])
@auth.login_required
def create():
    if request.method == 'POST':
        student = Student(
            firstname=request.form['firstname'],
            lastname=request.form['lastname'],
            email=request.form['email'],
            age=int(request.form['age']),
            bio=request.form['bio']
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
