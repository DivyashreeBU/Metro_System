from flask import Blueprint, request, render_template, redirect, session,flash,jsonify
from models import db, Admin, Station, Train
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Ticket, SmartCard, Train, Station,MetroLine
from datetime import datetime
from collections import Counter
from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint('admin_bp', __name__)

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
color_map = {
    "Purple Line": "purple",
    "Green Line": "green",
    "Yellow Line": "gold"
}

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form['username']).first()
        if admin and check_password_hash(admin.password, request.form['password']):
            session['admin_id'] = admin.id
            flash("Admin login successful.")
            return redirect('/admin/dashboard')
        else:
            flash("Invalid admin credentials.")
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_id'):
        return redirect('/admin/login')
    stations = Station.query.all()
    trains = Train.query.all()
    return render_template('admin_dashboard.html', stations=stations, trains=trains)
     
@admin_bp.route('/admin/users')
def admin_users():
    if not session.get('admin_id'):
        return redirect('/admin/login')
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/tickets')
def admin_tickets():
    if not session.get('admin_id'):
        return redirect('/admin/login')
    tickets = Ticket.query.all()
    return render_template('admin_tickets.html', tickets=tickets)

@admin_bp.route('/admin/cards')
def admin_cards():
    if not session.get('admin_id'):
        return redirect('/admin/login')
    cards = SmartCard.query.all()
    return render_template('admin_cards.html', cards=cards)
    
@admin_bp.route('/api/admin/analytics')
def admin_analytics():
    # Count how many times each route was booked
    route_counts = {}
    tickets = Ticket.query.all()

    for ticket in tickets:
        key = f"{ticket.from_station} → {ticket.to_station}"
        route_counts[key] = route_counts.get(key, 0) + 1

    # Convert to list of dicts
    popular_routes = [
        {"route": route, "count": count}
        for route, count in sorted(route_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return jsonify(popular_routes)

@admin_bp.route('/admin/analytics')
def analytics_page():
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    if start and end:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        tickets = Ticket.query.filter(Ticket.date.between(start_date, end_date)).all()
    else:
        tickets = Ticket.query.all()

    # ✅ Daily ticket volume aggregation
    daily_counts = Counter(
    ticket.created_at.strftime("%Y-%m-%d")
    for ticket in tickets
    if ticket.created_at is not None
)
    daily_data = sorted(daily_counts.items())  # [(date, count)]

    return render_template('analytics.html', daily_data=daily_data)

@admin_bp.route('/admin/station-info')
def station_info():
    query = request.args.get('station_query')
    found_lines = []
    for line, data in metro_lines.items():
        if line != "Interchanges" and query in data["stations"]:
            found_lines.append({"name": line, "color": data["color"]})

    interchange = metro_lines["Interchanges"].get(query, [])

    return render_template('station_info.html', station=query, lines=found_lines, interchange=interchange, color_map=color_map)


@admin_bp.route('/admin/line-analytics')
def line_analytics():
    tickets = Ticket.query.all()
    line_stats = {
        "Purple Line": {"count": 0, "revenue": 0},
        "Green Line": {"count": 0, "revenue": 0},
        "Yellow Line": {"count": 0, "revenue": 0}
    }

    def get_line(from_station, to_station):
        for line, data in metro_lines.items():
            if line != "Interchanges":
                if from_station in data["stations"] and to_station in data["stations"]:
                    return line
        return None

    for ticket in tickets:
        line = get_line(ticket.from_station, ticket.to_station)
        if line:
            line_stats[line]["count"] += 1
            line_stats[line]["revenue"] += ticket.fare

    return render_template('line_analytics.html', line_stats=line_stats)

@admin_bp.route('/admin/stations')
def view_stations():
    lines = MetroLine.query.order_by(MetroLine.name).all()
    return render_template('admin_stations.html', lines=lines)
        
@admin_bp.route('/admin/trains')
def view_trains():
    trains = Train.query.all()
    return render_template('admin_trains.html', trains=trains)
    
@admin_bp.route('/admin/trains/add', methods=['POST'])
def add_train():
    name = request.form['train_name']
    line_id = request.form['line_id']
    new_train = Train(name=name, line_id=line_id)
    db.session.add(new_train)
    db.session.commit()
    return redirect('/admin/trains')

@admin_bp.route('/admin/users')
def view_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    user.name = request.form['username']
    user.email = request.form['email']
    user.phone = request.form['phone']
    db.session.commit()
    flash("User updated successfully!")
    return redirect('/admin/users')


@admin_bp.route('/admin/users/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')  # Optional, depending on your form

    # ✅ Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("❌ Username already exists. Please choose a different one.")
        return redirect('/admin/users')

    # ✅ Add new user safely
    try:
        new_user = User(username=username, email=email, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("✅ User added successfully!")
    except IntegrityError:
        db.session.rollback()
        flash("❌ Failed to add user due to a database constraint.")
    
    return redirect('/admin/users')

@admin_bp.route('/admin/stations/edit/<int:station_id>', methods=['POST'])
def edit_station(station_id):
    station = Station.query.get(station_id)
    station.name = request.form['name']
    station.line_id = int(request.form['line_id'])
    station.is_interchange = request.form['is_interchange'] == 'true'
    db.session.commit()
    flash("Station updated successfully!")
    return redirect('/admin/stations')

@admin_bp.route('/admin/trains/edit/<int:train_id>', methods=['POST'])
def edit_train(train_id):
    train = Train.query.get(train_id)
    train.name = request.form['name']
    train.route_id = request.form['route_id']
    db.session.commit()
    flash("Train updated successfully!")
    return redirect('/admin/trains')

@admin_bp.route('/admin/generate-ticket', methods=['GET', 'POST'])
def generate_ticket():
    all_stations = sorted(set(
        s for line, data in metro_lines.items() if line != "Interchanges"
        for s in data["stations"]
    ))

    if request.method == 'POST':
        name = request.form['passenger_name']
        phone = request.form['phone']
        from_station = request.form['from_station']
        to_station = request.form['to_station']
        fare = round(random.uniform(10, 50), 2)
        train_id = random.randint(1000, 9999)

        ticket = Ticket(passenger_name=name, phone=phone, train_id=train_id,
                        from_station=from_station, to_station=to_station, fare=fare)
        db.session.add(ticket)
        db.session.commit()
        flash("Ticket generated successfully!")
        return redirect('/admin/tickets')

    return render_template('admin_generate_ticket.html', stations=all_stations)

@admin_bp.route('/admin/issue-smartcard', methods=['GET', 'POST'])
def issue_smartcard():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        balance = request.form.get('balance')
        new_card = SmartCard(user_id=user_id, balance=balance)
        db.session.add(new_card)
        db.session.commit()
        flash("✅ Smartcard issued successfully!")
        return redirect('/admin/issue-smartcard')
    return render_template('admin_issue_card.html')

@admin_bp.route('/admin/recharge-smartcard', methods=['GET', 'POST'])
def recharge_smartcard():
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        amount = float(request.form.get('amount'))
        card = SmartCard.query.get(card_id)
        if card:
            card.balance += amount
            db.session.commit()
            flash("✅ Smartcard recharged successfully!")
        else:
            flash("❌ Card not found.")
        return redirect('/admin/recharge-smartcard')
    return render_template('admin_recharge_card.html')

@admin_bp.route('/admin/generate-ticket', methods=['GET', 'POST'])
def admin_generate_ticket():
    # render form or handle ticket creation
    return render_template('admin_generate_ticket.html')