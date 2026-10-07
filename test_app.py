from app import app
from extensions import db
from models.user import User
from models.repair_job import RepairJob
from werkzeug.security import check_password_hash


def run():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(
            name="Admin Test",
            email="admin@test.local",
            password_hash=__import__("werkzeug.security", fromlist=["generate_password_hash"]).generate_password_hash("Admin123!"),
            role="admin",
        )
        customer = User(
            name="Customer Test",
            email="customer@test.local",
            password_hash=__import__("werkzeug.security", fromlist=["generate_password_hash"]).generate_password_hash("Customer123!"),
            role="customer",
        )
        other = User(
            name="Other Customer",
            email="other@test.local",
            password_hash=__import__("werkzeug.security", fromlist=["generate_password_hash"]).generate_password_hash("Other123!"),
            role="customer",
        )
        db.session.add_all([admin, customer, other])
        db.session.commit()

        assert check_password_hash(customer.password_hash, "Customer123!")
        assert customer.password_hash != "Customer123!"

        client = app.test_client()

        # Public landing page
        response = client.get("/")
        assert response.status_code == 200
        assert b"TechFix Repair Hub" in response.data

        # Customer registration
        response = client.post(
            "/register",
            data={
                "name": "New Customer",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Registration successful" in response.data

        # Customer login
        response = client.post(
            "/login",
            data={"email": "customer@test.local", "password": "Customer123!"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/customer/dashboard")

        # Customer create
        response = client.post(
            "/customer/repair-jobs/new",
            data={
                "device_type": "Cellphone",
                "brand": "Apple",
                "model": "iPhone 13",
                "problem_description": "Cracked screen",
                "estimated_cost": "2500",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

        job = RepairJob.query.filter_by(customer_id=customer.id).order_by(RepairJob.id.desc()).first()
        assert job is not None
        assert job.repair_status == "Pending"

        # Ownership check: customer cannot access another customer's job.
        other_job = RepairJob(
            customer_id=other.id,
            device_type="Laptop",
            brand="Lenovo",
            model="IdeaPad",
            problem_description="Won't boot",
            repair_status="Pending",
        )
        db.session.add(other_job)
        db.session.commit()

        response = client.get(f"/customer/repair-jobs/{other_job.id}")
        assert response.status_code == 403

        # Customer cannot edit after status changes.
        job.repair_status = "In Repair"
        db.session.commit()
        response = client.get(f"/customer/repair-jobs/{job.id}/edit")
        assert response.status_code == 302

        # Admin login and access.
        client.get("/logout")
        response = client.post(
            "/login",
            data={"email": "admin@test.local", "password": "Admin123!"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/admin/dashboard")

        # Admin can edit the job.
        response = client.post(
            f"/admin/repair-jobs/{job.id}/edit",
            data={
                "customer_id": str(customer.id),
                "device_type": job.device_type,
                "brand": job.brand,
                "model": job.model,
                "problem_description": job.problem_description,
                "repair_status": "Completed",
                "estimated_cost": "2600",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        db.session.refresh(job)
        assert job.repair_status == "Completed"
        assert str(job.estimated_cost) == "2600.00"

        # Persistent DB code path is covered by normal SQLAlchemy commit.
        print("All application tests passed.")


if __name__ == "__main__":
    run()
