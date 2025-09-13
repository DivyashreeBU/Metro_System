from extensions import db  # ✅ Use shared instance
from datetime import datetime

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False, unique=True)
    line_id = db.Column(db.Integer, db.ForeignKey('metro_line.id'), nullable=False)

    line = db.relationship('MetroLine', backref='trains')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    train_id = db.Column(db.Integer, nullable=False)
    from_station = db.Column(db.String(100), nullable=False)
    to_station = db.Column(db.String(100), nullable=False)
    fare = db.Column(db.Float, nullable=False)
    qr_code_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100),unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(100),nullable=False)
    smartcard_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    full_name = db.Column(db.String(100))
    
class SmartCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)

    # ✅ Add this relationship
    user = db.relationship('User', backref='smartcard')
    
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)

class MetroLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    color = db.Column(db.String(20))
    stations = db.relationship('Station', backref='line', lazy=True)

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    line_id = db.Column(db.Integer, db.ForeignKey('metro_line.id'))
    is_interchange = db.Column(db.Boolean, default=False)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to User
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    reply = db.Column(db.Text)
    reply_method = db.Column(db.String(10))  # 'email' or 'phone'
