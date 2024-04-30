from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from app import app, User, db

def set_user_password(username, new_password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            print(f"Password updated for user '{username}'")
            # Query all information about the user to ensure it still exists
            updated_user = User.query.filter_by(username=username).first()
            print("User details after password update:")
            print(updated_user.__dict__)
        else:
            print(f"User '{username}' not found")

if __name__ == "__main__":
    username = "delfino2"
    new_password = "deldeoxisldn"
    set_user_password(username, new_password)
