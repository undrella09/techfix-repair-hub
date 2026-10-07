from datetime import datetime, timezone
from decimal import Decimal
from extensions import db


class RepairJob(db.Model):
    __tablename__ = "repair_jobs"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    device_type = db.Column(db.String(40), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(120), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    repair_status = db.Column(
        db.String(40),
        nullable=False,
        default="Pending",
    )
    estimated_cost = db.Column(
        db.Numeric(10, 2),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    customer = db.relationship("User", back_populates="repair_jobs")

    @property
    def cost_display(self):
        if self.estimated_cost is None:
            return "Not set"
        return f"₱{Decimal(self.estimated_cost):,.2f}"
