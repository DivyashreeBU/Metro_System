from flask import Blueprint, request, render_template, redirect, session,flash,jsonify
from models import db, User, SmartCard,Complaint
from werkzeug.security import generate_password_hash, check_password_hash

smartcard_bp = Blueprint('smartcard_bp', __name__)

@smartcard_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            flash("Login successful!")
            return redirect('/smartcard')
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

import random
import string

def generate_smartcard_number():
    return 'SC' + ''.join(random.choices(string.digits, k=10))

@smartcard_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Please choose a different one.")
            return render_template('register.html')

        try:
            smartcard_number = generate_smartcard_number()

            user = User(
                full_name=full_name,
                email=email,
                phone=phone,
                username=username,
                password=password,
                smartcard_number=smartcard_number,
                balance=0.0,
                status='Pending'
            )
            db.session.add(user)
            db.session.commit()

            card = SmartCard(user_id=user.id, balance=0.0)
            db.session.add(card)
            db.session.commit()

            flash("Registration successful! You can now log in.")
            return redirect('/login')

        except Exception as e:
            flash(f"Registration failed: {str(e)}")
            return render_template('register.html')

    return render_template('register.html')
    
@smartcard_bp.route('/smartcard', methods=['GET', 'POST'])
def smartcard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    user = User.query.get(user_id)  # ✅ This fetches the logged-in user's details
    card = SmartCard.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        amount = float(request.form['amount'])
        card.balance += amount
        db.session.commit()
        flash(f"Recharge successful! ₹{amount} added.")

    return render_template('smartcard.html', card=card, user=user)
    
@smartcard_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin_id', None)
    return redirect('/')

@smartcard_bp.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    if request.method == 'POST':
        user_id = session.get('user_id')
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        phone = request.form.get('phone', '')  # use get() so it won’t crash if missing

        new_complaint = Complaint(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        db.session.add(new_complaint)
        db.session.commit()
        flash("✅ Complaint submitted successfully.")
    return redirect('/feedback')


    # Show user's complaints
    user_id = session.get('user_id')
    complaints = Complaint.query.filter_by(user_id=user_id).order_by(Complaint.id.desc()).all()
    return render_template('feedback.html', complaints=complaints)

@smartcard_bp.route("/check-reply", methods=["POST"])
def check_reply():
    try:
        data = {}
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict() or {}

        email = (data.get('email') or '').strip()
        if not email:
            return jsonify({"error": "Email required", "replies": []}), 400

        complaints = Complaint.query.filter_by(email=email).order_by(Complaint.id.desc()).all()
        replies = []

        for c in complaints:
            replies.append({
                "id": getattr(c, 'id', 0),
                "subject": getattr(c, 'subject', ''),
                "reply": getattr(c, 'admin_reply', 'Pending'),
                "created_at": getattr(c, 'replied_at', None).strftime("%Y-%m-%d %H:%M") if getattr(c, 'replied_at', None) else None
            })

        return jsonify({"replies": replies}), 200

    except Exception as e:
        print("Error in /check-reply:", e)
        return jsonify({"replies": [], "error": str(e)}), 500
