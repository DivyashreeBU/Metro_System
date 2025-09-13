from flask import Flask, flash, get_flashed_messages, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes.ticket_routes import ticket_bp
from routes.smartcard_routes import smartcard_bp
from routes.admin_routes import admin_bp
from routes.station_info_routes import station_bp
from routes.info_routes import info_bp
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'timeout': 30  # timeout in seconds
    }
}

app.secret_key = 'your-unique-secret-key'

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(ticket_bp)
app.register_blueprint(smartcard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(station_bp)
app.register_blueprint(info_bp)

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)