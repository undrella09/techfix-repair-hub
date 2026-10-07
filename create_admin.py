from app import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = "admin@techfix.test"
    password = "Admin123!"

    admin = User.query.filter_by(email=email).first()

    if admin:
        admin.name = "TechFix Administrator"
        admin.password_hash = generate_password_hash(password)
        admin.role = "admin"
        print("Existing account updated to admin.")
    else:
        admin = User(
            name="TechFix Administrator",
            email=email,
            password_hash=generate_password_hash(password),
            role="admin"
        )

        db.session.add(admin)
        print("Admin account created.")

    db.session.commit()

    print()
    print("===================================")
    print("ADMIN ACCOUNT")
    print("Email:    admin@techfix.test")
    print("Password: Admin123!")
    print("Role:     admin")
    print("===================================")