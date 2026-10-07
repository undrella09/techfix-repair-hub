from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models.user import User
from models.repair_job import RepairJob


def get_or_create_user(name, email, password, role):
    user = User.query.filter_by(email=email).first()
    if user:
        return user, False

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.flush()
    return user, True


with app.app_context():
    admin, _ = get_or_create_user(
        "TechFix Admin",
        "admin@techfix.test",
        "Admin123!",
        "admin",
    )
    customer, customer_created = get_or_create_user(
        "Demo Customer",
        "customer@techfix.test",
        "Customer123!",
        "customer",
    )

    if customer_created and RepairJob.query.count() == 0:
        jobs = [
            RepairJob(
                customer_id=customer.id,
                device_type="Laptop",
                brand="Dell",
                model="Inspiron 15",
                problem_description="Laptop does not turn on.",
                repair_status="Diagnosing",
                estimated_cost=Decimal("1500.00"),
            ),
            RepairJob(
                customer_id=customer.id,
                device_type="Cellphone",
                brand="Samsung",
                model="Galaxy A54",
                problem_description="Screen is cracked and touch input is unreliable.",
                repair_status="In Repair",
                estimated_cost=Decimal("3500.00"),
            ),
            RepairJob(
                customer_id=customer.id,
                device_type="Desktop Computer",
                brand="Custom Build",
                model="Gaming PC",
                problem_description="Computer overheats during long gaming sessions.",
                repair_status="Ready for Pickup",
                estimated_cost=Decimal("2000.00"),
            ),
        ]
        db.session.add_all(jobs)

    db.session.commit()
    print("Seed completed successfully.")
    print("Admin: admin@techfix.test / Admin123!")
    print("Customer: customer@techfix.test / Customer123!")
