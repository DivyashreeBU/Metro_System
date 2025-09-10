from app import app
from models import db, Station, Train, User, SmartCard, Ticket
from werkzeug.security import generate_password_hash
from utils.fare_calculator import calculate_fare

with app.app_context():
    db.drop_all()
    db.create_all()

    # 🚉 Seed Stations
    stations = [
        Station(name="Baiyappanahalli", zone="1"),
        Station(name="Indiranagar", zone="2"),
        Station(name="MG Road", zone="2"),
        Station(name="Majestic", zone="3"),
        Station(name="Kengeri", zone="5"),
        Station(name="Nagasandra", zone="1"),
        Station(name="Yeshwanthpur", zone="2"),
        Station(name="Banashankari", zone="4")
    ]
    db.session.add_all(stations)

    # 🚆 Seed Trains
    trains = [
        Train(name="Purple Express", route_id=1),
        Train(name="Green Commuter", route_id=2)
    ]
    db.session.add_all(trains)

    # 👤 Seed Users
    users = [
        User(username="divya", password=generate_password_hash("pass123")),
        User(username="admin", password=generate_password_hash("admin123"))
    ]
    db.session.add_all(users)
    db.session.commit()

    # 💳 Seed Smart Cards
    smartcards = [
        SmartCard(user_id=users[0].id, balance=100.0)
    ]
    db.session.add_all(smartcards)

    # 🎫 Seed Tickets
    ticket_data = [
        ("Divya", "9876543210", trains[0].id, "MG Road", "Majestic"),
        ("Ravi", "9123456780", trains[1].id, "Yeshwanthpur", "Banashankari"),
        ("Anu", "9988776655", trains[0].id, "Indiranagar", "Kengeri")
    ]

    for name, phone, train_id, from_station, to_station in ticket_data:
        from_zone = Station.query.filter_by(name=from_station).first().zone
        to_zone = Station.query.filter_by(name=to_station).first().zone
        fare = calculate_fare(from_zone, to_zone)
        ticket = Ticket(
            passenger_name=name,
            phone=phone,
            train_id=train_id,
            from_station=from_station,
            to_station=to_station,
            fare=fare,
            qr_code_path=f"static/qrcodes/ticket_seed_{name}.png"
        )
        db.session.add(ticket)

    db.session.commit()
    print("✅ Database seeded with stations, trains, users, smart cards, and tickets.")
    