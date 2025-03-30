# setup_db.py
from app import app
from model import db, Admin  
from werkzeug.security import generate_password_hash  

with app.app_context():
    # db.drop_all()
    db.create_all()

    # Create an initial admin user
    admin_username = "21f1001520"
    admin_email = "21f1001520@ds.study.iitm.ac.in"
    admin_password = "123456"  
    admin_full_name = "Admin One"

    # Check if the admin already exists to avoid duplicates
    existing_admin = Admin.query.filter_by(username=admin_username).first()
    if not existing_admin:
        new_admin = Admin(
            username=admin_username,
            email=admin_email,
            password=generate_password_hash(admin_password),
            full_name=admin_full_name
            )
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin '{admin_username}' created successfully.")
    else:
        print(f"Admin '{admin_username}' already exists, skipping creation.")
    print("Database setup complete.")