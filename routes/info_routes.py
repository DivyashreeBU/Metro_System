# routes/info_routes.py
from flask import Blueprint, render_template
from flask import Blueprint, render_template, request, redirect
from models import Complaint  # Assuming you have a Complaint model
from extensions import db

info_bp = Blueprint('info_bp', __name__)

metro_lines = {
    "Purple Line": {
        "stations": [
            "Challaghatta", "Kengeri", "Mysuru Road", "Vijayanagar", "Hosahalli",
            "Magadi Road", "Majestic", "Cubbon Park", "MG Road", "Trinity",
            "Indiranagar", "Baiyappanahalli", "KR Puram", "Whitefield"
        ],
        "color": "purple"
    },
    "Green Line": {
        "stations": [
            "Nagasandra", "Peenya", "Yeshwanthpur", "Rajajinagar",
            "Mantri Square Sampige Road", "Majestic", "Chickpete", "KR Market",
            "National College", "South End Circle", "Jayanagar", "Banashankari",
            "Yelachenahalli", "Silk Institute"
        ],
        "color": "green"
    },
    "Yellow Line": {
        "stations": [
            "RV Road", "Ragigudda", "Jayadeva Hospital", "BTM Layout",
            "HSR Layout", "Central Silk Board", "Bommasandra"
        ],
        "color": "gold"
    },
    "Interchanges": {
        "Majestic": ["Purple Line", "Green Line"],
        "Jayadeva Hospital": ["Yellow Line"]
    }
}

@info_bp.route('/routes')
def route_info():
    return render_template('route_info.html', metro_lines=metro_lines)

@info_bp.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        new_complaint = Complaint(name=name, email=email, subject=subject, message=message)
        db.session.add(new_complaint)
        db.session.commit()

        return redirect('/feedback')  # Or show a thank-you message

    return render_template('feedback.html')

from models import Complaint  # Make sure this model exists


@info_bp.route('/submit-complaint', methods=['POST'])
def submit_complaint():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    complaint = Complaint(name=name, email=email, subject=subject, message=message)
    db.session.add(complaint)
    db.session.commit()

    return redirect('/feedback')  # Or show a thank-you page
