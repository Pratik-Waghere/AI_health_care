import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
import joblib

# 21 symptoms
SYMPTOMS = [
    "fever", "fatigue", "headache", "cough", "sore_throat", "runny_nose", "shortness_of_breath",
    "chest_pain", "dizziness", "nausea", "vomiting", "diarrhea", "abdominal_pain",
    "loss_of_appetite", "constipation", "muscle_pain", "joint_pain", "rash", "swelling",
    "anxiety", "depression"
]

# Possible diseases
diseases = ["Common Cold", "Flu", "COVID-19", "Gastroenteritis", "Anxiety Disorder", "Depression"]

# Step 1: Generate the synthetic dataset and save to CSV
def generate_data_csv(filename='symptom_data.csv', n=500):
    data = []
    for _ in range(n):
        symptoms = [random.randint(0, 1) for _ in SYMPTOMS]

        # Rules to assign diseases based on selected symptoms
        if symptoms[0] and symptoms[3] and symptoms[5]:  # fever + cough + runny_nose
            disease = "Common Cold"
        elif symptoms[0] and symptoms[1] and symptoms[2] and symptoms[3]:  # flu pattern
            disease = "Flu"
        elif symptoms[0] and symptoms[3] and symptoms[6] and symptoms[7]:  # covid pattern
            disease = "COVID-19"
        elif symptoms[9] and symptoms[10] and symptoms[11]:  # digestive
            disease = "Gastroenteritis"
        elif symptoms[19]:  # anxiety
            disease = "Anxiety Disorder"
        elif symptoms[20]:  # depression
            disease = "Depression"
        else:
            disease = random.choice(diseases)

        data.append(symptoms + [disease])

    df = pd.DataFrame(data, columns=SYMPTOMS + ['disease'])
    df.to_csv(filename, index=False)
    print(f"✅ Dataset saved to {filename}")

# Step 2: Load CSV and train model
def train_model_from_csv(filename='symptom_data.csv'):
    df = pd.read_csv(filename)
    X = df[SYMPTOMS]
    y = df['disease']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, 'model/model.pkl')
    print("✅ Model trained and saved to model.pkl")

# Run both steps
generate_data_csv()
train_model_from_csv()
