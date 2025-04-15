from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import numpy as np
from datetime import datetime
import pickle
import joblib
# from .utils import predict_disease

# Get the current directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build full paths to the model files
model_path = os.path.join(BASE_DIR, 'model', 'model.pkl')
# mlb_path = os.path.join(BASE_DIR, 'model', 'mlb.pkl')

# Initialize model variable
model = None

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

# Define comprehensive disease mappings
RECOMMENDATIONS = {
    "Common Cold": [
        "Rest and stay hydrated",
        "Take over-the-counter cold medicine",
        "Use a humidifier",
        "Gargle with warm salt water"
    ],
    "Flu": [
        "Rest and stay hydrated",
        "Take antiviral medication if prescribed",
        "Use fever-reducing medication",
        "Stay home to avoid spreading"
    ],
    "COVID-19": [
        "Isolate immediately",
        "Monitor oxygen levels",
        "Take prescribed medications",
        "Seek emergency care if breathing becomes difficult"
    ],
    "Gastroenteritis": [
        "Stay hydrated with clear fluids",
        "Follow BRAT diet (Bananas, Rice, Applesauce, Toast)",
        "Take anti-nausea medication if needed",
        "Rest and avoid dairy products"
    ],
    "Anxiety Disorder": [
        "Practice deep breathing exercises",
        "Try meditation or mindfulness",
        "Consider talking to a therapist",
        "Maintain regular sleep schedule"
    ],
    "Depression": [
        "Seek professional help",
        "Maintain regular exercise routine",
        "Establish a daily routine",
        "Stay connected with friends and family"
    ]
}

PRECAUTIONS = {
    "Common Cold": [
        "Wash hands frequently",
        "Cover mouth when coughing",
        "Use tissues for nose blowing",
        "Avoid close contact with others"
    ],
    "Flu": [
        "Get annual flu vaccine",
        "Practice good hygiene",
        "Avoid touching face",
        "Stay home when sick"
    ],
    "COVID-19": [
        "Wear a mask in public",
        "Maintain social distance",
        "Get vaccinated if eligible",
        "Regular hand washing"
    ],
    "Gastroenteritis": [
        "Practice food safety",
        "Wash hands thoroughly",
        "Avoid sharing utensils",
        "Stay hydrated"
    ],
    "Anxiety Disorder": [
        "Limit caffeine intake",
        "Practice regular exercise",
        "Maintain a healthy diet",
        "Get adequate sleep"
    ],
    "Depression": [
        "Maintain regular sleep schedule",
        "Exercise regularly",
        "Stay connected with others",
        "Avoid alcohol and drugs"
    ]
}

DOCTOR_VISITS = {
    "Common Cold": "Visit a doctor if symptoms persist for more than 10 days or if you have difficulty breathing.",
    "Flu": "Seek immediate medical attention if you have difficulty breathing, chest pain, or severe weakness.",
    "COVID-19": "Seek emergency care if you experience difficulty breathing, persistent chest pain, or confusion.",
    "Gastroenteritis": "Visit a doctor if you have severe dehydration, blood in stool, or symptoms lasting more than 3 days.",
    "Anxiety Disorder": "Consult a mental health professional if anxiety interferes with daily life or if you experience panic attacks.",
    "Depression": "Seek immediate help if you have thoughts of self-harm or if symptoms persist for more than two weeks."
}

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
    # add = db.Column(db.String(200))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to load the model
def load_model():
    global model
    try:
        # Check if model file exists
        if not os.path.exists(model_path):
            print(f"Model file not found at {model_path}")
            return False
            
        # Load model using joblib instead of pickle for better compatibility
        model = joblib.load(model_path)
        
        # Verify the model has the required methods
        required_methods = ['predict', 'predict_proba']
        for method in required_methods:
            if not hasattr(model, method):
                print(f"Model missing required method: {method}")
                return False
                
        # Test the model with a sample input
        sample_input = np.zeros((1, len(SYMPTOMS)))
        sample_input[0, 0] = 1  # Set fever to 1
        try:
            prediction = model.predict(sample_input)
            probas = model.predict_proba(sample_input)
            print(f"Model test successful! Sample prediction: {prediction}")
        except Exception as e:
            print(f"Error testing model: {str(e)}")
            return False
            
        print("Model loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

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
        # Retrieve selected symptoms from the form submission
        symptoms = request.form.getlist('symptoms')  # Use getlist to capture all selected symptoms
        
        # Get additional symptoms from the text box
        additional_symptoms_text = request.form.get('additional_symptoms', '').strip()
        
        # Process additional symptoms if provided
        if additional_symptoms_text:
            # Split by commas and clean up each symptom
            additional_symptoms = [symptom.strip().lower().replace(' ', '_') for symptom in additional_symptoms_text.split(',')]
            # Add to the symptoms list
            symptoms.extend(additional_symptoms)
        
        # Debug: Print selected symptoms
        print(f"Selected symptoms: {symptoms}")
        
        # Make sure model is loaded
        if model is None:
            if not load_model():
                flash("Model could not be loaded. Please try again later.")
                return redirect(url_for('dashboard'))
        
        # Call the predict_disease function with the selected symptoms
        prediction = predict_disease(symptoms)
        
        # Check if the prediction result contains an error
        if "error" in prediction:
            flash(f"There was an issue with the prediction: {prediction['error']}")
            return redirect(url_for('symptom_form'))

        # Pass the prediction result to the template
        return render_template('prediction_result.html', prediction=prediction)
    
    return render_template('symptom_form.html', symptoms=SYMPTOMS)

@app.route('/prediction_result')
@login_required
def prediction_result():
    return render_template('prediction_result.html')

@app.route('/doctor_suggestion')
@login_required
def doctor_suggestion():
    disease = request.args.get('disease', None)

    # Map diseases to specializations
    disease_specialization_map = {
        "Common Cold": "General Physician",
        "COVID-19": "Pulmonologist",
        "Depression": "Psychiatrist",
        "Disease (Generic)": "General Physician",
        "Flu": "General Physician",
        "Gastroenteritis": "Gastroenterologist",
        "Anxiety Disorder": "Psychiatrist"
    }

    specialization = disease_specialization_map.get(disease, None)

    if specialization:
        doctors = Doctor.query.filter_by(specialization=specialization).all()
    else:
        doctors = Doctor.query.all()

    return render_template('doctor_suggestion.html', doctors=doctors, disease=disease, specialization=specialization)

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
    # Debug: Print the input symptoms
    print(f"Input symptoms: {symptoms}")
    
    # Filter out symptoms that are not in the SYMPTOMS list
    # This ensures we only use symptoms that the model was trained on
    valid_symptoms = [symptom for symptom in symptoms if symptom in SYMPTOMS]
    
    # If no valid symptoms were provided, return an error
    if not valid_symptoms:
        return {"error": "No valid symptoms were provided. Please select from the list or enter symptoms that match the predefined list."}
    
    # Create a binary vector (1 if symptom present, else 0)
    symptom_array = np.array([[1 if symptom in valid_symptoms else 0 for symptom in SYMPTOMS]])
    
    # Debug: Check the structure of the symptom array
    print(f"Symptom array shape: {symptom_array.shape}")
    print(f"Symptom array: {symptom_array}")

    # Make sure the model is loaded correctly
    if hasattr(model, 'predict'):
        # Use model to predict the disease
        try:
            # Check if the model has the expected classes
            print(f"Model classes: {model.classes_}")
            
            # Make prediction
            prediction = model.predict(symptom_array)
            print(f"Raw prediction: {prediction}")
            
            # Get probabilities
            probas = model.predict_proba(symptom_array)
            print(f"Raw probabilities: {probas}")
            
            # Get predicted disease and confidence
            predicted_disease = prediction[0]  # Predicted disease (class)
            confidence_score = round(np.max(probas) * 100, 2)  # Confidence level
            
            # Debug: Check the predicted disease and confidence score
            print(f"Predicted disease: {predicted_disease}")
            print(f"Confidence score: {confidence_score}")
            
            # Check if the predicted disease is in our mappings
            if predicted_disease not in RECOMMENDATIONS:
                print(f"Warning: Predicted disease '{predicted_disease}' not in recommendations mapping")
                # Use a default disease if the predicted one is not in our mappings
                predicted_disease = "Common Cold"  # Default to a common condition
        
        except Exception as e:
            # Handle any exceptions from prediction
            import traceback
            print(f"Error during prediction: {str(e)}")
            print(traceback.format_exc())
            return {"error": f"Error during prediction: {str(e)}"}
    else:
        # Return an error or fallback if the model is not valid
        print("Model does not have predict method")
        return {"error": "Model is not loaded correctly."}

    # Return the result in a structured dictionary
    # Store the predicted disease in session storage
    session['predicted_disease'] = predicted_disease
    return {
        "disease": predicted_disease,
        "confidence": confidence_score,
        "recommendations": RECOMMENDATIONS.get(predicted_disease, ["Consult a healthcare provider for proper diagnosis and treatment."]),
        "precautions": PRECAUTIONS.get(predicted_disease, ["Maintain good hygiene and follow general health guidelines."]),
        "when_to_see_doctor": DOCTOR_VISITS.get(predicted_disease, "If symptoms worsen or persist, consult a healthcare provider.")
    }

@app.route('/add_specialty_doctors')
def add_specialty_doctors():
    doctors = [
        Doctor(name="Dr. Ramesh Verma", specialization="General Physician", contact="1111111111", hospital="City Clinic", add="101 Street A"),
        Doctor(name="Dr. Seema Nair", specialization="Pulmonologist", contact="2222222222", hospital="Lung Care Hospital", add="102 Street B"),
        Doctor(name="Dr. Anita Sharma", specialization="Psychiatrist", contact="3333333333", hospital="Mind Wellness Center", add="103 Street C"),
        Doctor(name="Dr. Vivek Joshi", specialization="General Physician", contact="4444444444", hospital="Health Hub", add="104 Street D"),
        Doctor(name="Dr. Neha Kapoor", specialization="General Physician", contact="5555555555", hospital="Flu Clinic", add="105 Street E"),
        Doctor(name="Dr. Arjun Mehta", specialization="Gastroenterologist", contact="6666666666", hospital="Digestive Health Institute", add="106 Street F")
    ]
    db.session.bulk_save_objects(doctors)
    db.session.commit()
    return "Specialty-based doctors added!"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Load the model at startup
        load_model()
    app.run(debug=True)
