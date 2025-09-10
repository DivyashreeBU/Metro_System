from flask import Blueprint, request, render_template, redirect, url_for,flash
from models import db, Ticket, Station, Train
from utils.fare_calculator import calculate_fare
import qrcode
import os
import random

ticket_bp = Blueprint('ticket_bp', __name__)

@ticket_bp.route('/')
def index():
    stations = Station.query.all()
    trains = Train.query.all()
    return render_template('index.html', stations=stations, trains=trains)

ticket_bp = Blueprint('ticket_bp', __name__)

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
        "color": "yellow"
    },
    "Interchanges": {
        "Majestic": ["Purple Line", "Green Line"],
        "Jayadeva Hospital": ["Yellow Line"]
    }
}

# Flatten all stations
all_stations = []
for line, data in metro_lines.items():
    if line != "Interchanges":
        all_stations.extend(data["stations"])
all_stations = sorted(set(all_stations))  # remove duplicates and sort

@ticket_bp.route('/book', methods=['GET', 'POST'])
def book_ticket():
    if request.method == 'POST':
        name = request.form['passenger_name']
        phone = request.form['phone']
        from_station = request.form['from_station']
        to_station = request.form['to_station']

        if from_station == to_station:
            flash("From and To stations cannot be the same.")
            return redirect('/book')

        fare = round(random.uniform(10, 50), 2)
        train_id = random.randint(1000, 9999)

        ticket = Ticket(
            passenger_name=name,
            phone=phone,
            train_id=train_id,
            from_station=from_station,
            to_station=to_station,
            fare=fare
        )
        db.session.add(ticket)
        db.session.commit()

        return render_template('ticket_success.html', ticket=ticket)

    return render_template('book_ticket.html', stations=all_stations)

@ticket_bp.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    return render_template('ticket_view.html', ticket=ticket)

@ticket_bp.route('/scan/<int:ticket_id>')
def scan_qr(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return "❌ Ticket not found", 404
    return f"""
    ✅ QR Scan Successful<br>
    Ticket ID: {ticket.id}<br>
    From: {ticket.from_station}<br>
    To: {ticket.to_station}
    """