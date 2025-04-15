# Health Diagnosis System

A web-based health diagnosis system that helps users identify potential health conditions based on their symptoms and provides appropriate medical guidance.

## Features

- User authentication (login/register)
- Personal health information management
- Symptom-based disease prediction
- Doctor recommendations
- Health precautions and guidelines
- Contact and feedback system

## Technology Stack

### Frontend
- HTML5
- CSS3 (Bootstrap 5)
- JavaScript
- Jinja2 Templates

### Backend
- Python 3.x
- Flask
- SQLite
- scikit-learn (for disease prediction)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/health-diagnosis-system.git
cd health-diagnosis-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
health-diagnosis-system/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # Custom JavaScript
│   └── images/           # Image assets
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── health_details.html # Health information form
│   ├── symptom_form.html # Symptom checker form
│   ├── prediction_result.html # Disease prediction results
│   ├── doctor_suggestion.html # Doctor recommendations
│   ├── precautions.html  # Health precautions
│   ├── about.html        # About page
│   └── contact.html      # Contact page
└── README.md             # Project documentation
```

## Usage

1. Register a new account or login with existing credentials
2. Update your personal health information
3. Use the symptom checker to identify potential health conditions
4. View recommended doctors and precautions
5. Contact support if needed

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap for the frontend framework
- Flask for the web framework
- scikit-learn for machine learning capabilities 