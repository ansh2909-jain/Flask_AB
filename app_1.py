import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from functools import wraps
from token_config import VALID_TOKENS  # Import tokens from external file

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key

db = SQLAlchemy(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        print(f"Received Token: {token}")  # Debugging line
        
        if not token or not token.startswith("Bearer "):
            return jsonify({'message': 'Unauthorized'}), 401
        
        token_value = token.replace("Bearer ", "").strip()
        if token_value not in VALID_TOKENS:
            return jsonify({'message': 'Unauthorized'}), 401

        return f(*args, **kwargs)
    return decorated

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
@token_required
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/<int:student_id>/')
@token_required
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', student=student)

@app.route('/<int:student_id>/edit/', methods=['GET', 'POST'])
@token_required
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
@token_required
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/create/', methods=['GET', 'POST'])
@token_required
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
