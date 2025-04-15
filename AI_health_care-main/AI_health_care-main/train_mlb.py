# create_mlb.py

import pickle
from sklearn.preprocessing import MultiLabelBinarizer

SYMPTOMS = [
    "fever", "fatigue", "headache", "cough", "sore_throat", "runny_nose", "shortness_of_breath",
    "chest_pain", "dizziness", "nausea", "vomiting", "diarrhea", "abdominal_pain",
    "loss_of_appetite", "constipation", "muscle_pain", "joint_pain", "rash", "swelling",
    "anxiety", "depression"
]

# Create and fit the MultiLabelBinarizer
mlb = MultiLabelBinarizer(classes=SYMPTOMS)
mlb.fit([SYMPTOMS])  # Fit with the full list once

# Save to pickle file
with open('model/mlb.pkl', 'wb') as f:
    pickle.dump(mlb, f)

print("✅ mlb.pkl saved in 'model/' directory")
