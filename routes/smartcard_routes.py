from flask import Blueprint, request, render_template, redirect, session,flash
from models import db, User, SmartCard
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

@smartcard_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        # ✅ Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Please choose a different one.")
            return render_template('register.html')

        try:
            user = User(
                full_name=full_name,
                email=email,
                phone=phone,
                username=username,
                password=password
            )
            db.session.add(user)
            db.session.commit()

            # ✅ Optionally create smart card
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