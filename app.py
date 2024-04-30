from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy import or_, cast, String
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ChangePasswordForm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TelField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email

app = Flask(__name__)
app.secret_key = '45fsa5!2p3r4553c1r3tK3y!'

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://postgres.pklaisbyehmemsrxwiav:{os.getenv('DATABASE_PASSWORD')}@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
  with app.app_context():
    session = Session()
    user = session.query(User).get(int(user_id))
    session.close()
    return user


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
  last_updated_at = db.Column(db.DateTime,
                              default=datetime.utcnow,
                              onupdate=datetime.utcnow)
  membership_year = db.Column(db.Integer, nullable=True)
  password_changed_at = db.Column(db.DateTime, nullable=True)
  user_type = db.Column(db.String(50), nullable=True)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)


with app.app_context():
  Session = sessionmaker(bind=db.engine)


class LoginForm(FlaskForm):
  username = StringField('Usuario',
                         validators=[DataRequired(),
                                     Length(min=2, max=20)])
  password = PasswordField('Contraseña', validators=[DataRequired()])
  submit = SubmitField('Acceder')


class ChangePasswordForm(FlaskForm):
  password = PasswordField('Nueva Contraseña',
                           validators=[DataRequired(),
                                       Length(min=6)])
  confirm_password = PasswordField(
      'Confirmar Nueva Contraseña',
      validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Cambiar Contraseña')


class CreateUserForm(FlaskForm):
  username = StringField(
      'Nombre de usuario (Esto no se puede cambiar en un futuro, ten cuidado)',
      validators=[DataRequired(), Length(min=3, max=20)])
  first_name = StringField('Nombre(s)',
                           validators=[DataRequired(),
                                       Length(max=100)])  # New
  last_name = StringField('Apellido(s)',
                          validators=[DataRequired(),
                                      Length(max=100)])  # New
  member_id = StringField('# Miembro',
                          validators=[DataRequired(),
                                      Length(max=50)])  # New
  initial_password = PasswordField('Contraseña Inicial',
                                   validators=[DataRequired(),
                                               Length(min=6)])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  phone = TelField('Teléfono')
  city = StringField('Ciudad', validators=[DataRequired(), Length(max=100)])
  state = StringField('Estado', validators=[DataRequired(), Length(max=100)])
  aviary = StringField('Aviario', validators=[DataRequired(), Length(max=100)])
  membership_year = StringField('Membresia Activa', validators=[DataRequired(), Length(max=100)])
  submit = SubmitField('Crear usuario')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError(
          'Nombre de usuario ya en uso, por favor elige uno diferente.')

  def validate_member_id(self, member_id):
    user = User.query.filter_by(member_id=member_id.data).first()
    if user:
      raise ValidationError(
          'Número de miembro ya en uso, por favor revisa y define uno diferente.'
      )


class UserDetailsForm(FlaskForm):
  username = StringField('Usuario',
                         validators=[DataRequired(),
                                     Length(min=3, max=20)])
  first_name = StringField('Nombre(s)',
                           validators=[DataRequired(),
                                       Length(max=100)])
  last_name = StringField('Apellido(s)',
                          validators=[DataRequired(),
                                      Length(max=100)])
  member_id = StringField('# Miembro',
                          validators=[DataRequired(),
                                      Length(max=50)])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  phone = TelField('Teléfono')
  city = StringField('Ciudad')
  state = StringField('Estado')
  aviary = StringField('Aviario')
  membership_year = StringField('Membresia Activa')
  submit = SubmitField('Actualizar datos')


@app.route('/')
def index():
  if current_user.is_authenticated:
    print("User Type:", current_user.user_type)
  return render_template('home.html')


@app.route('/profile')
@login_required
def profile():
  return render_template('user_profile.html', user=current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user and user.check_password(form.password.data):
      login_user(user)
      next_page = request.args.get('next')
      return redirect(next_page) if next_page else redirect(url_for('home'))
    else:
      flash(
          'Error de inicio de sesión: Comprueba tu usuario y contraseña e inténtalo de nuevo.',
          'danger')
  return render_template('login.html', title='Login', form=form)


@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
  form = ChangePasswordForm()
  if form.validate_on_submit():
    current_user.set_password(form.password.data)
    current_user.is_password_changed = True
    db.session.commit()
    flash('Tu contraseña ha sido actualizada.', 'success')
    return redirect(url_for('profile'))
  return render_template('change_password.html',
                         title='Cambiar Contraseña',
                         form=form)


@app.route("/change_password_user", methods=['GET', 'POST'])
@login_required
def change_password_user():
  form = ChangePasswordForm()
  if form.validate_on_submit():
    app.logger.info('Before updating password for user: %s', current_user.id)
    current_user.set_password(form.password.data)
    db.session.commit()
    app.logger.info('After updating password for user: %s', current_user.id)
    flash('Tu contraseña ha sido actualizada.', 'success')
    return redirect(url_for('home'))
  return render_template('change_password_user.html',
                         title='Cambiar Contraseña',
                         form=form)

@app.route("/admin/create_user", methods=['GET', 'POST'])
@login_required
def admin_create_user():
  if current_user.user_type != "admin":
    flash('No tienes permisos para acceder a esta página.', 'danger')
    return redirect(url_for('home'))

  form = CreateUserForm()
  if form.validate_on_submit():
    username_exists = User.query.filter_by(username=form.username.data).first()
    member_id_exists = User.query.filter_by(
        member_id=form.member_id.data).first()

    if username_exists:
      flash("Nombre de usuario ya en uso, por favor elige uno diferente",
            "warning")
    elif member_id_exists:
      flash(
          "Número de miembro ya en uso, por favor revisa y define uno diferente.",
          "warning")
    else:
      hashed_password = generate_password_hash(form.initial_password.data)
      user = User(username=form.username.data,
                  email=form.email.data,
                  phone=form.phone.data,
                  city=form.city.data,
                  state=form.state.data,
                  aviary=form.aviary.data,
                  first_name=form.first_name.data,
                  last_name=form.last_name.data,
                  member_id=form.member_id.data,
                  password_hash=hashed_password,
                  is_password_changed=False)
      db.session.add(user)
      db.session.commit()
      flash(f"Usuario {user.first_name} {user.last_name} creado exitosamente.",
            'success')
      return redirect(url_for('manage_users'))

  return render_template('admin_create_user.html',
                         title='Create User',
                         form=form)


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))


@app.route('/manage_users', methods=['GET'])
@login_required
def manage_users():
    if current_user.user_type != "admin":
        flash("Unauthorized. Admins only.", "danger")
        return redirect(url_for('home'))

    users = User.query.order_by(User.id).all()
    total_results = len(users)
    last_three_users = User.query.order_by(User.member_id.desc()).limit(3).all()

    return render_template('manage_users.html',
                           users=users,
                           total_results=total_results,
                           last_three_users=last_three_users)

@app.route('/manage_users/search', methods=['GET'])
@login_required
def search_users():
    if current_user.user_type != "admin":
        flash("Unauthorized. Admins only.", "danger")
        return jsonify({"error": "unauthorized"}), 403
      
    search_term = f"%{request.args.get('term', '').lower()}%"
    # Filter on other fields as before, and cast member_id to text for the search
    users = User.query.filter(
        or_(
            User.username.ilike(search_term),
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term),
            cast(User.member_id, String).ilike(search_term),  # Cast member_id to String
            User.phone.ilike(search_term),
            User.email.ilike(search_term),
            User.city.ilike(search_term),
            User.state.ilike(search_term),
            User.aviary.ilike(search_term),
            cast(User.membership_year, String).ilike(search_term)
        )
     ).all()
    results = [{"username": user.username, "first_name": user.first_name, "last_name": user.last_name, "member_id": user.member_id, "email": user.email, "phone": user.phone, "city": user.city, "state": user.state, "aviary": user.aviary, "membership_year": user.membership_year} for user in users]
    return jsonify({"results": results})
  
@app.route('/user/<int:user_id>/change_password', methods=['GET', 'POST'])
@login_required
def change_user_password(user_id):
  if current_user.user_type != "admin":
    flash("Unauthorized. Admins only.", "danger")
    return redirect(url_for('home'))

  user = User.query.get_or_404(user_id)
  form = ChangePasswordForm()
  if form.validate_on_submit():
    user.set_password(form.password.data)
    db.session.commit()
    flash(
        f"La contraseña para {user.first_name} {user.last_name} fue cambiada exitosamente!",
        'success')
    return redirect(url_for('manage_users'))
  return render_template('change_password.html',
                         title='Change User Password',
                         form=form,
                         user=user)


@app.route('/user/<int:user_id>/details', methods=['GET', 'POST'])
@login_required
def manage_user_details(user_id):
  if current_user.user_type != "admin":
    flash("Unauthorized. Admins only.", "danger")
    return redirect(url_for('home'))

  user = User.query.get_or_404(user_id)

  form = UserDetailsForm(
      obj=user)

  if form.validate_on_submit():
    form.populate_obj(user)

    user.email = form.email.data
    user.phone = form.phone.data
    user.city = form.city.data
    user.state = form.state.data
    user.aviary = form.aviary.data

    db.session.commit()
    flash(
        f"Los datos de {user.first_name} {user.last_name} fueron actualizados exitosamente.",
        'success')
    return redirect(url_for('manage_users'))

  for error in form.errors.values():
    flash("; ".join(error), 'danger')

  return render_template('user_details.html',
                         title='User Details',
                         form=form,
                         user_id=user_id)

@app.route('/home')
def home():
  return render_template('home.html', title='Home')


@app.route('/eventos')
def eventos():
  return 'Evento registrado exitosamente'


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
