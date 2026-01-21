from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uems.db'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin or student

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    registered = db.relationship('Registration', backref='event', lazy=True)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    student = db.relationship('User', backref='registrations', lazy=True)

# Initialize database and default admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created")

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for('register'))
        user = User(username=username, password=password, role='student')
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    events = Event.query.all()
    registered_events = []

    if session['role'] == 'student':
        regs = Registration.query.filter_by(student_id=session['user_id']).all()
        registered_events = [r.event_id for r in regs]
        return render_template('dashboard.html', events=events, role='student', registered_events=registered_events)

    elif session['role'] == 'admin':
        event_registrations = {}
        for event in events:
            regs = Registration.query.filter_by(event_id=event.id).all()
            students = [User.query.get(r.student_id).username for r in regs]
            event_registrations[event.id] = students
        return render_template('dashboard.html', events=events, role='admin', event_registrations=event_registrations)

@app.route('/add_event', methods=['GET','POST'])
def add_event():
    if 'role' not in session or session['role'] != 'admin':
        flash("Unauthorized access!", "error")
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        date = datetime.strptime(request.form['date'], "%Y-%m-%d")
        venue = request.form['venue']
        capacity = int(request.form['capacity'])
        event = Event(name=name, date=date, venue=venue, capacity=capacity)
        db.session.add(event)
        db.session.commit()
        flash("Event added successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('add_event.html')

@app.route('/register_event/<int:event_id>')
def register_event(event_id):
    if 'role' not in session or session['role'] != 'student':
        flash("Unauthorized access!", "error")
        return redirect(url_for('dashboard'))

    existing = Registration.query.filter_by(student_id=session['user_id'], event_id=event_id).first()
    if not existing:
        reg = Registration(student_id=session['user_id'], event_id=event_id)
        db.session.add(reg)
        db.session.commit()
        flash("Registered for the event successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

