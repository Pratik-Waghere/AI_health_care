import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 21 symptoms
SYMPTOMS = [
    "fever", "fatigue", "headache", "cough", "sore_throat", "runny_nose", "shortness_of_breath",
    "chest_pain", "dizziness", "nausea", "vomiting", "diarrhea", "abdominal_pain",
    "loss_of_appetite", "constipation", "muscle_pain", "joint_pain", "rash", "swelling",
    "anxiety", "depression"
]

# Possible diseases
DISEASES = ["Common Cold", "Flu", "COVID-19", "Gastroenteritis", "Anxiety Disorder", "Depression"]

def generate_data_csv(filename='symptom_data.csv', n=1000):
    logger.info(f"Generating {n} samples of training data...")
    data = []
    for i in range(n):
        symptoms = [random.randint(0, 1) for _ in SYMPTOMS]
        
        # Define disease patterns based on common symptom combinations
        if sum(symptoms) == 0:  # No symptoms
            disease = random.choice(DISEASES)
        else:
            # Common Cold pattern
            if symptoms[0] and symptoms[3] and symptoms[5] and not symptoms[6]:  # fever + cough + runny_nose
                disease = "Common Cold"
            # Flu pattern
            elif symptoms[0] and symptoms[1] and symptoms[2] and symptoms[3] and symptoms[16]:  # fever + fatigue + headache + cough + muscle_pain
                disease = "Flu"
            # COVID-19 pattern
            elif symptoms[0] and symptoms[3] and symptoms[6] and symptoms[7]:  # fever + cough + shortness_of_breath + chest_pain
                disease = "COVID-19"
            # Gastroenteritis pattern
            elif symptoms[9] and symptoms[10] and symptoms[11] and symptoms[12]:  # nausea + vomiting + diarrhea + abdominal_pain
                disease = "Gastroenteritis"
            # Anxiety pattern
            elif symptoms[19] and (symptoms[6] or symptoms[7] or symptoms[8]):  # anxiety + (shortness_of_breath or chest_pain or dizziness)
                disease = "Anxiety Disorder"
            # Depression pattern
            elif symptoms[20] and symptoms[1] and symptoms[13]:  # depression + fatigue + loss_of_appetite
                disease = "Depression"
            else:
                # Random assignment with weighted probabilities based on symptom patterns
                disease = random.choice(DISEASES)

        data.append(symptoms + [disease])
        if (i + 1) % 100 == 0:
            logger.info(f"Generated {i + 1} samples...")

    df = pd.DataFrame(data, columns=SYMPTOMS + ['disease'])
    
    # Create model directory if it doesn't exist
    os.makedirs('model', exist_ok=True)
    
    # Save the dataset
    df.to_csv(filename, index=False)
    logger.info(f"✅ Dataset saved to {filename}")
    
    # Print some statistics
    logger.info("\nDataset Statistics:")
    logger.info(f"Total samples: {len(df)}")
    logger.info("\nDisease distribution:")
    logger.info(df['disease'].value_counts())
    
    return df

def train_model_from_csv(filename='symptom_data.csv'):
    logger.info("Loading dataset...")
    df = pd.read_csv(filename)
    X = df[SYMPTOMS]
    y = df['disease']

    logger.info("Training Random Forest model...")
    # Create and train the model with more trees and better parameters
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    model.fit(X, y)

    # Verify the model has the required methods
    logger.info("Verifying model methods...")
    required_methods = ['predict', 'predict_proba']
    for method in required_methods:
        if not hasattr(model, method):
            logger.error(f"Model missing required method: {method}")
            raise ValueError(f"Model missing required method: {method}")
    
    # Test the model with a sample input
    logger.info("Testing model with sample input...")
    sample_input = np.zeros((1, len(SYMPTOMS)))
    sample_input[0, 0] = 1  # Set fever to 1
    try:
        prediction = model.predict(sample_input)
        probas = model.predict_proba(sample_input)
        logger.info(f"Sample prediction: {prediction}")
        logger.info(f"Sample probabilities: {probas}")
    except Exception as e:
        logger.error(f"Error testing model: {str(e)}")
        raise

    # Save the model
    model_path = 'model/model.pkl'
    joblib.dump(model, model_path)
    logger.info(f"✅ Model trained and saved to {model_path}")
    
    # Print model accuracy
    from sklearn.metrics import accuracy_score
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    logger.info(f"Model accuracy on training data: {accuracy:.2%}")
    
    return model

def verify_model(model_path='model/model.pkl'):
    """Verify that the saved model can be loaded and has the required methods"""
    logger.info(f"Verifying model at {model_path}...")
    try:
        # Load the model
        model = joblib.load(model_path)
        
        # Check if it has the required methods
        required_methods = ['predict', 'predict_proba']
        for method in required_methods:
            if not hasattr(model, method):
                logger.error(f"Loaded model missing required method: {method}")
                return False
        
        # Test with a sample input
        sample_input = np.zeros((1, len(SYMPTOMS)))
        sample_input[0, 0] = 1  # Set fever to 1
        prediction = model.predict(sample_input)
        probas = model.predict_proba(sample_input)
        
        logger.info(f"Model verification successful!")
        logger.info(f"Sample prediction: {prediction}")
        logger.info(f"Sample probabilities: {probas}")
        return True
    except Exception as e:
        logger.error(f"Error verifying model: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Run both steps
        df = generate_data_csv()
        model = train_model_from_csv()
        
        # Verify the model
        if verify_model():
            logger.info("✅ Training and verification completed successfully!")
        else:
            logger.error("❌ Model verification failed!")
    except Exception as e:
        logger.error(f"❌ Error during training: {str(e)}")
        raise
