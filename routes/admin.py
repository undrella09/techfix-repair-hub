from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models.repair_job import RepairJob
from models.user import User
from routes.auth import roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

DEVICE_TYPES = ["Laptop", "Desktop Computer", "Cellphone", "Tablet", "Other"]
REPAIR_STATUSES = [
    "Pending",
    "Diagnosing",
    "Waiting for Parts",
    "In Repair",
    "Ready for Pickup",
    "Completed",
    "Cancelled",
]


def parse_repair_form(form):
    device_type = form.get("device_type", "").strip()
    brand = form.get("brand", "").strip()
    model = form.get("model", "").strip()
    problem_description = form.get("problem_description", "").strip()
    status = form.get("repair_status", "Pending").strip()
    raw_cost = form.get("estimated_cost", "").strip()
    customer_id_raw = form.get("customer_id", "").strip()
    errors = []
    estimated_cost = None
    customer_id = None

    if device_type not in DEVICE_TYPES:
        errors.append("Please select a valid device type.")

    if not brand:
        errors.append("Brand is required.")
    elif len(brand) > 80:
        errors.append("Brand must be 80 characters or fewer.")

    if not model:
        errors.append("Model is required.")
    elif len(model) > 120:
        errors.append("Model must be 120 characters or fewer.")

    if not problem_description:
        errors.append("Problem description is required.")
    elif len(problem_description) > 2000:
        errors.append("Problem description must be 2000 characters or fewer.")

    if status not in REPAIR_STATUSES:
        errors.append("Please select a valid repair status.")

    if raw_cost:
        try:
            estimated_cost = Decimal(raw_cost)
            if estimated_cost < 0:
                errors.append("Estimated cost must be zero or greater.")
            elif estimated_cost > Decimal("99999999.99"):
                errors.append("Estimated cost is too large.")
        except InvalidOperation:
            errors.append("Estimated cost must be a valid number.")

    try:
        customer_id = int(customer_id_raw)
        if not db.session.get(User, customer_id):
            errors.append("Selected customer does not exist.")
    except (TypeError, ValueError):
        errors.append("Please select a valid customer.")

    return (
        customer_id,
        device_type,
        brand,
        model,
        problem_description,
        status,
        estimated_cost,
        errors,
    )


@admin_bp.route("/dashboard")
@roles_required("admin")
def dashboard():
    jobs = RepairJob.query.order_by(RepairJob.created_at.desc()).all()
    stats = {
        "total": RepairJob.query.count(),
        "pending": RepairJob.query.filter_by(repair_status="Pending").count(),
        "in_repair": RepairJob.query.filter_by(repair_status="In Repair").count(),
        "ready": RepairJob.query.filter_by(repair_status="Ready for Pickup").count(),
        "completed": RepairJob.query.filter_by(repair_status="Completed").count(),
    }
    return render_template("admin/dashboard.html", jobs=jobs, stats=stats)


@admin_bp.route("/repair-jobs")
@roles_required("admin")
def repair_jobs():
    jobs = RepairJob.query.order_by(RepairJob.created_at.desc()).all()
    return render_template("admin/repair_jobs.html", jobs=jobs)


@admin_bp.route("/repair-jobs/new", methods=["GET", "POST"])
@roles_required("admin")
def create_repair_job():
    customers = User.query.filter_by(role="customer").order_by(User.name.asc()).all()

    if request.method == "POST":
        (
            customer_id,
            device_type,
            brand,
            model,
            problem_description,
            status,
            estimated_cost,
            errors,
        ) = parse_repair_form(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "admin/repair_form.html",
                page_title="Add Repair Job",
                customers=customers,
                device_types=DEVICE_TYPES,
                statuses=REPAIR_STATUSES,
                form=request.form,
            )

        job = RepairJob(
            customer_id=customer_id,
            device_type=device_type,
            brand=brand,
            model=model,
            problem_description=problem_description,
            repair_status=status,
            estimated_cost=estimated_cost,
        )
        db.session.add(job)
        db.session.commit()

        flash(f"Repair Job #{job.id} was created.", "success")
        return redirect(url_for("admin.repair_jobs"))

    return render_template(
        "admin/repair_form.html",
        page_title="Add Repair Job",
        customers=customers,
        device_types=DEVICE_TYPES,
        statuses=REPAIR_STATUSES,
        form={},
    )


@admin_bp.route("/repair-jobs/<int:repair_id>")
@roles_required("admin")
def view_repair_job(repair_id):
    job = db.get_or_404(RepairJob, repair_id)
    return render_template("admin/repair_detail.html", job=job)


@admin_bp.route("/repair-jobs/<int:repair_id>/edit", methods=["GET", "POST"])
@roles_required("admin")
def edit_repair_job(repair_id):
    job = db.get_or_404(RepairJob, repair_id)
    customers = User.query.filter_by(role="customer").order_by(User.name.asc()).all()

    if request.method == "POST":
        (
            customer_id,
            device_type,
            brand,
            model,
            problem_description,
            status,
            estimated_cost,
            errors,
        ) = parse_repair_form(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "admin/repair_form.html",
                page_title=f"Edit Repair Job #{job.id}",
                customers=customers,
                device_types=DEVICE_TYPES,
                statuses=REPAIR_STATUSES,
                form=request.form,
                job=job,
            )

        job.customer_id = customer_id
        job.device_type = device_type
        job.brand = brand
        job.model = model
        job.problem_description = problem_description
        job.repair_status = status
        job.estimated_cost = estimated_cost
        db.session.commit()

        flash(f"Repair Job #{job.id} was updated.", "success")
        return redirect(url_for("admin.repair_jobs"))

    form = {
        "customer_id": str(job.customer_id),
        "device_type": job.device_type,
        "brand": job.brand,
        "model": job.model,
        "problem_description": job.problem_description,
        "repair_status": job.repair_status,
        "estimated_cost": "" if job.estimated_cost is None else str(job.estimated_cost),
    }

    return render_template(
        "admin/repair_form.html",
        page_title=f"Edit Repair Job #{job.id}",
        customers=customers,
        device_types=DEVICE_TYPES,
        statuses=REPAIR_STATUSES,
        form=form,
        job=job,
    )


@admin_bp.route("/repair-jobs/<int:repair_id>/delete", methods=["POST"])
@roles_required("admin")
def delete_repair_job(repair_id):
    job = db.get_or_404(RepairJob, repair_id)
    db.session.delete(job)
    db.session.commit()
    flash(f"Repair Job #{repair_id} was deleted.", "success")
    return redirect(url_for("admin.repair_jobs"))


@admin_bp.route("/customers")
@roles_required("admin")
def customers():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/customers.html", users=users)
