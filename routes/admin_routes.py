from flask import Blueprint, request, render_template, redirect, session,flash,jsonify, url_for
from models import db, Admin, Station, Train
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Ticket, SmartCard, Train, Station,MetroLine,Complaint
from datetime import datetime
from collections import Counter
from sqlalchemy.exc import IntegrityError
from routes.ticket_routes import all_stations
import random,math
from pytz import timezone
from sqlalchemy import func

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
    complaints = Complaint.query.order_by(Complaint.id.desc()).limit(5).all()
    return render_template('admin_dashboard.html', stations=stations, trains=trains)
     
@admin_bp.route('/admin/users')
def admin_users():
    if not session.get('admin_id'):
        return redirect('/admin/login')
    users = User.query.all()
    return render_template('admin_users.html', users=users)

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
    data = request.get_json()
    name = data.get('name')
    color = data.get('color')

    if not name or not color:
        return "Missing name or color", 400

    # Check if line already exists
    line = MetroLine.query.filter_by(color=color).first()
    if not line:
        line = MetroLine(name=f"{color} Line", color=color)
        db.session.add(line)
        db.session.flush()

    # Create train
    new_train = Train(name=name, line_id=line.id)
    db.session.add(new_train)
    db.session.commit()
    return "Train added", 200

@admin_bp.route('/admin/trains/delete/<int:train_id>', methods=['POST'])
def delete_train(train_id):
    train = Train.query.get_or_404(train_id)
    db.session.delete(train)
    db.session.commit()
    return redirect('/admin/trains')
    
@admin_bp.route('/admin/trains/add', methods=['GET'])
def show_add_train_form():
    lines = MetroLine.query.all()
    return render_template('add_train.html', lines=lines)

@admin_bp.route('/admin/users')
def view_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/users/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    smartcard_number = str(random.randint(10000000, 99999999))
    balance = request.form.get('balance')

    # ✅ Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("❌ Username already exists. Please choose a different one.")
        return redirect(url_for('admin_bp.view_users'))

    # ✅ Add new user safely
    try:
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password=password,
            smartcard_number=smartcard_number,
            balance=float(balance)
        )
        db.session.add(new_user)
        db.session.commit()
        flash("✅ User added successfully!")
    except IntegrityError:
        db.session.rollback()
        flash("❌ Failed to add user due to a database constraint.")
    return redirect(url_for('admin_bp.view_users'))
    
    return redirect('/admin/users')

@admin_bp.route('/admin/users/add', methods=['GET'])
def show_add_user_form():
    return render_template('admin_add_users.html')

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.username = request.form.get('username')
        user.phone = request.form.get('phone')
        user.email = request.form.get('email')
        user.smartcard_number = request.form.get('smartcard_number')
        user.status = request.form['status']
        db.session.commit()
        flash("✅ User updated successfully.")
    else:
        flash("❌ User not found.")
    return redirect(url_for('admin_bp.view_users'))

@admin_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"✅ User '{user.username}' deleted.")
    else:
        flash("❌ User not found.")
    return redirect(url_for('admin_bp.view_users'))

@admin_bp.route('/admin/fix-user-status')
def fix_user_status():
    User.query.filter(User.status == None).update({User.status: 'Pending'})
    db.session.commit()
    return "✅ All missing statuses set to 'Pending'"

@admin_bp.route('/admin/users/search')
def search_users():
    query = request.args.get('query')
    if query:
        users = User.query.filter(User.username.ilike(f"%{query}%")).all()
        return render_template('admin_users.html', users=users)
    else:
        flash("Please enter a username to search.")
        return redirect(url_for('admin_bp.view_users'))

@admin_bp.route('/admin/users/delete-all', methods=['POST'])
def delete_all_users():
    User.query.delete()
    db.session.commit()
    flash("✅ All users have been deleted.")
    return redirect(url_for('admin_bp.view_users'))

@admin_bp.route('/admin/stations/edit/<int:station_id>', methods=['POST'])
def edit_station(station_id):
    station = Station.query.get(station_id)
    station.name = request.form['name']
    station.line_id = int(request.form['line_id'])
    station.is_interchange = request.form['is_interchange'] == 'true'
    db.session.commit()
    flash("Station updated successfully!")
    return redirect('/admin/stations')

@admin_bp.route('/admin/generate-ticket', methods=['GET', 'POST'])
def generate_ticket():
    from datetime import datetime
    import qrcode
    import os

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

        # ✅ Generate QR code content
        qr_data = f"{name} | {from_station} → {to_station} | ₹{fare} | Train #{train_id}"
        qr_img = qrcode.make(qr_data)

        # ✅ Save QR code image
        os.makedirs("static/qrcodes", exist_ok=True)
        qr_filename = f"ticket_{name}_{train_id}.png"
        qr_path = f"static/qrcodes/{qr_filename}"
        qr_img.save(qr_path)

        # ✅ Create ticket with QR path and timestamp
        ticket = Ticket(
            passenger_name=name,
            phone=phone,
            train_id=train_id,
            from_station=from_station,
            to_station=to_station,
            fare=fare,
            qr_code_path=qr_path,
            date=datetime.utcnow()  # or created_at if your model uses that
        )

        db.session.add(ticket)
        db.session.commit()
        flash("🎫 Ticket generated successfully!")
        return redirect('/admin/tickets')

    return render_template('admin_generate_ticket.html', stations=all_stations)

@admin_bp.route('/admin/users/recharge/<int:user_id>', methods=['POST'])
def recharge_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    amount = data.get('amount')

    if amount is None or amount <= 0:
        return jsonify(success=False), 400

    user.balance += amount
    db.session.commit()
    return jsonify(success=True, new_balance=user.balance)

@admin_bp.route('/admin/generate-ticket', methods=['GET', 'POST'])
def admin_generate_ticket():
    # render form or handle ticket creation
    return render_template('admin_generate_ticket.html')

@admin_bp.route('/admin/tickets', methods=['GET', 'POST'])
def admin_tickets():
    today = datetime.utcnow().date()
    ist = timezone('Asia/Kolkata')

    # 🧹 Auto-delete expired tickets (older than today)
    Ticket.query.filter(func.date(Ticket.date) < today).delete()
    db.session.commit()

    # 🎫 Fetch today's tickets
    tickets = Ticket.query.filter(func.date(Ticket.date) == today).all()

    # 🕒 Convert UTC to IST for display
    for ticket in tickets:
        ticket.local_time = ticket.date.astimezone(ist)

    # 🚉 Get station names for dropdowns
    stations = [station.name for station in Station.query.all()]

    return render_template('admin_tickets.html', tickets=tickets, stations=stations)

@admin_bp.route('/admin/delete/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        db.session.delete(ticket)
        db.session.commit()
        flash("✅ Ticket deleted.")
    return redirect(url_for('admin_bp.admin_tickets'))

@admin_bp.route('/admin/delete-all', methods=['POST'])
def delete_all_tickets():
    today = datetime.utcnow().date()
    Ticket.query.filter(db.func.date(Ticket.created_at) == today).delete()
    db.session.commit()
    flash("✅ All today's tickets deleted.")
    return redirect(url_for('admin_bp.admin_tickets'))

@admin_bp.route('/admin/update/<int:ticket_id>', methods=['POST'])
def update_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        ticket.passenger_name = request.form.get('passenger_name')
        ticket.from_station = request.form.get('from_station')
        ticket.to_station = request.form.get('to_station')
        ticket.fare = math.ceil(float(request.form.get('fare')))
        db.session.commit()
        flash("✅ Ticket updated successfully.")
    return redirect(url_for('admin_bp.admin_tickets'))
    
@admin_bp.route('/admin/complaints')
def view_complaints():
    complaints = Complaint.query.all()
    return render_template('admin_complaints.html', complaints=complaints)

@admin_bp.route('/admin/complaints/reply/<int:complaint_id>', methods=['POST'])
def reply_to_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.reply = request.form['reply']
    complaint.reply_method = request.form['reply_method']
    db.session.commit()
    flash("✅ Reply sent successfully.")
    return redirect('/admin/complaints')