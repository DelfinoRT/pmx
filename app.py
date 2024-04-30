from flask import Flask, render_template, request, redirect, url_for, session as flask_session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '45fsa5!2p3r4553c1r3tK3y!'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://postgres.pklaisbyehmemsrxwiav:{os.getenv('DATABASE_PASSWORD')}@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    member_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    aviary = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_password_changed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    membership_year = db.Column(db.Integer, nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=True)
    user_type = db.Column(db.String(50), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Replace the engine and session setup with Flask-SQLAlchemy
# engine = create_engine(DATABASE_URI)
# Session = sessionmaker(bind=engine)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/eventos')
def eventos():
    return render_template('eventos.html')

@app.route('/contenido')
def contenido():
    return "Contenido page content here"

@app.route('/miembros')
def miembros():
    users = User.query.all()
    return render_template('miembros.html', users=users)

@app.route('/galeria')
def galeria():
    return "Galería page content here"

@app.route('/formatos')
def formatos():
    return render_template('formatos.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html', enctype="multipart/form-data")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if user.password_hash and user.check_password(password):
                flask_session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password or no password set', 'error')
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

