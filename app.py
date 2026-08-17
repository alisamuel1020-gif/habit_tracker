import os
import csv
import io
from datetime import date, datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///habits.db').replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    habits = db.relationship('Habit', backref='owner', lazy=True, cascade="all, delete-orphan")

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    reminder_time = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade="all, delete-orphan")

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    completed = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTH ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- HABIT ROUTES ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/habits', methods=['GET'])
@login_required
def get_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    output = []
    for h in habits:
        logs = [{"id": l.id, "date": l.date.isoformat(), "completed": l.completed} for l in h.logs]
        output.append({
            "id": h.id,
            "name": h.name,
            "description": h.description,
            "reminder_time": h.reminder_time,
            "logs": logs
        })
    return jsonify(output)

@app.route('/habits', methods=['POST'])
@login_required
def add_habit():
    data = request.get_json()
    new_habit = Habit(
        name=data.get('name'),
        description=data.get('description'),
        reminder_time=data.get('reminder_time'),
        user_id=current_user.id
    )
    db.session.add(new_habit)
    db.session.commit()
    return jsonify({"message": "Habit created"}), 201

@app.route('/habits/<int:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    return jsonify({"message": "Habit deleted"})

@app.route('/habits/<int:habit_id>/logs', methods=['POST'])
@login_required
def log_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    today = date.today()
    existing_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
    if not existing_log:
        new_log = HabitLog(habit_id=habit.id, date=today, completed=True)
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Logged successfully"}), 201
    return jsonify({"message": "Already logged today"}), 200

@app.route('/export/csv')
@login_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Habit ID', 'Name', 'Description', 'Reminder Time', 'Total Logs'])
    
    for h in current_user.habits:
        writer.writerow([h.id, h.name, h.description or '', h.reminder_time or '', len(h.logs)])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=habits_export.csv"}
    )

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)