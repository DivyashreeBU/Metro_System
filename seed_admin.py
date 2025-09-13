from models import db, Admin
from werkzeug.security import generate_password_hash
from app import app  # or wherever your Flask app is defined

with app.app_context():
    # Check if admin already exists
    existing = Admin.query.filter_by(username='admin').first()
    if existing:
        print("Admin already exists.")
    else:
        admin = Admin(
            username='admin',
            password=generate_password_hash('admin123')  # You can change this
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: username='admin', password='admin123'")