from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import joblib

joblib.dump(model, 'model.pkl')
joblib.dump(mlb, 'mlb.pkl')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

SYMPTOMS = [
    "fever", "fatigue", "headache", "cough", "sore_throat", "runny_nose", "shortness_of_breath",
    "chest_pain", "dizziness", "nausea", "vomiting", "diarrhea", "abdominal_pain",
    "loss_of_appetite", "constipation", "muscle_pain", "joint_pain", "rash", "swelling",
    "anxiety", "depression"
]


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    weight = db.Column(db.Float)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    hospital = db.Column(db.String(200))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = User.query.filter_by(phone=phone).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid phone number or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        address = request.form.get('address')
        
        if User.query.filter_by(phone=phone).first():
            flash('Phone number already registered')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, phone=phone, password=hashed_password, address=address)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/health_details', methods=['GET', 'POST'])
@login_required
def health_details():
    if request.method == 'POST':
        current_user.age = request.form.get('age')
        current_user.gender = request.form.get('gender')
        current_user.blood_group = request.form.get('blood_group')
        current_user.weight = request.form.get('weight')
        db.session.commit()
        flash('Health details updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('health_details.html')

@app.route('/symptom_form', methods=['GET', 'POST'])
@login_required
def symptom_form():
    if request.method == 'POST':
        symptoms = request.form.getlist('symptoms')
        # Here you would implement your AI model prediction
        # For now, we'll just redirect to a dummy result
        return redirect(url_for('prediction_result'))
    return render_template('symptom_form.html')

@app.route('/prediction_result')
@login_required
def prediction_result():
    return render_template('prediction_result.html')

@app.route('/doctor_suggestion')
@login_required
def doctor_suggestion():
    doctors = Doctor.query.all()
    return render_template('doctor_suggestion.html', doctors=doctors)

@app.route('/precautions')
@login_required
def precautions():
    return render_template('precautions.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        feedback = Feedback(name=name, message=message)
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!')
        return redirect(url_for('contact'))
    return render_template('contact.html')

def predict_disease(symptoms):
    # Convert user symptoms into model input format
    symptom_array = mlb.transform([symptoms])
    
    # Predict using the trained model
    prediction = model.predict(symptom_array)
    probas = model.predict_proba(symptom_array)
    
    # Get predicted disease and confidence
    predicted_disease = prediction[0]
    confidence_score = round(np.max(probas) * 100, 2)

    # Define some dummy mappings (replace with real ones later)
    RECOMMENDATIONS = {
        "Flu": ["Rest", "Hydrate", "Take paracetamol"],
        "Food Poisoning": ["Avoid solid food", "Oral rehydration", "Visit nearby clinic"],
        # Add more...
    }

    PRECAUTIONS = {
        "Flu": ["Avoid cold drinks", "Stay indoors", "Monitor temperature"],
        "Food Poisoning": ["Avoid street food", "Wash hands", "Boil water before drinking"],
        # Add more...
    }

    DOCTOR_VISITS = {
        "Flu": "Visit a doctor if fever persists for more than 3 days.",
        "Food Poisoning": "Consult a doctor if vomiting or diarrhea continues after 24 hours.",
        # Add more...
    }

    return {
        "disease": predicted_disease,
        "confidence": confidence_score,
        "recommendations": RECOMMENDATIONS.get(predicted_disease, ["Consult a doctor."]),
        "precautions": PRECAUTIONS.get(predicted_disease, ["Maintain hygiene."]),
        "when_to_see_doctor": DOCTOR_VISITS.get(predicted_disease, "If symptoms worsen, visit a hospital.")
    }
   

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 