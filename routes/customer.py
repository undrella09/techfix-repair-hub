from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from extensions import db
from models.repair_job import RepairJob
from routes.auth import get_current_user, roles_required

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

DEVICE_TYPES = ["Laptop", "Desktop Computer", "Cellphone", "Tablet", "Other"]


def customer_form_data(form):
    device_type = form.get("device_type", "").strip()
    brand = form.get("brand", "").strip()
    model = form.get("model", "").strip()
    problem_description = form.get("problem_description", "").strip()
    raw_cost = form.get("estimated_cost", "").strip()
    errors = []
    estimated_cost = None

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

    if raw_cost:
        try:
            estimated_cost = Decimal(raw_cost)
            if estimated_cost < 0:
                errors.append("Estimated cost must be zero or greater.")
        except InvalidOperation:
            errors.append("Estimated cost must be a valid number.")

    return device_type, brand, model, problem_description, estimated_cost, errors


def owned_job_or_403(repair_id):
    job = db.get_or_404(RepairJob, repair_id)
    if job.customer_id != get_current_user().id:
        abort(403)
    return job


@customer_bp.route("/dashboard")
@roles_required("customer")
def dashboard():
    user = get_current_user()
    jobs = RepairJob.query.filter_by(customer_id=user.id).order_by(
        RepairJob.created_at.desc()
    ).all()

    stats = {
        "total": len(jobs),
        "pending": sum(1 for j in jobs if j.repair_status == "Pending"),
        "active": sum(
            1
            for j in jobs
            if j.repair_status in {"Diagnosing", "Waiting for Parts", "In Repair", "Ready for Pickup"}
        ),
        "completed": sum(1 for j in jobs if j.repair_status == "Completed"),
    }
    return render_template("customer/dashboard.html", jobs=jobs, stats=stats)


@customer_bp.route("/repair-jobs")
@roles_required("customer")
def repair_jobs():
    user = get_current_user()
    jobs = RepairJob.query.filter_by(customer_id=user.id).order_by(
        RepairJob.created_at.desc()
    ).all()
    return render_template("customer/repair_jobs.html", jobs=jobs)


@customer_bp.route("/repair-jobs/new", methods=["GET", "POST"])
@roles_required("customer")
def create_repair_job():
    if request.method == "POST":
        (
            device_type,
            brand,
            model,
            problem_description,
            estimated_cost,
            errors,
        ) = customer_form_data(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "customer/repair_form.html",
                page_title="New Repair Request",
                device_types=DEVICE_TYPES,
                form=request.form,
            )

        job = RepairJob(
            customer_id=get_current_user().id,
            device_type=device_type,
            brand=brand,
            model=model,
            problem_description=problem_description,
            repair_status="Pending",
            estimated_cost=estimated_cost,
        )
        db.session.add(job)
        db.session.commit()

        flash(f"Repair request #{job.id} was submitted.", "success")
        return redirect(url_for("customer.repair_jobs"))

    return render_template(
        "customer/repair_form.html",
        page_title="New Repair Request",
        device_types=DEVICE_TYPES,
        form={},
    )


@customer_bp.route("/repair-jobs/<int:repair_id>")
@roles_required("customer")
def view_repair_job(repair_id):
    job = owned_job_or_403(repair_id)
    return render_template("customer/repair_detail.html", job=job)


@customer_bp.route("/repair-jobs/<int:repair_id>/edit", methods=["GET", "POST"])
@roles_required("customer")
def edit_repair_job(repair_id):
    job = owned_job_or_403(repair_id)

    if job.repair_status != "Pending":
        flash("Only Pending repair requests can be edited.", "warning")
        return redirect(url_for("customer.repair_jobs"))

    if request.method == "POST":
        (
            device_type,
            brand,
            model,
            problem_description,
            estimated_cost,
            errors,
        ) = customer_form_data(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "customer/repair_form.html",
                page_title=f"Edit Repair Request #{job.id}",
                device_types=DEVICE_TYPES,
                form=request.form,
                job=job,
            )

        job.device_type = device_type
        job.brand = brand
        job.model = model
        job.problem_description = problem_description
        job.estimated_cost = estimated_cost
        db.session.commit()

        flash(f"Repair request #{job.id} was updated.", "success")
        return redirect(url_for("customer.repair_jobs"))

    form = {
        "device_type": job.device_type,
        "brand": job.brand,
        "model": job.model,
        "problem_description": job.problem_description,
        "estimated_cost": "" if job.estimated_cost is None else str(job.estimated_cost),
    }

    return render_template(
        "customer/repair_form.html",
        page_title=f"Edit Repair Request #{job.id}",
        device_types=DEVICE_TYPES,
        form=form,
        job=job,
    )


@customer_bp.route("/repair-jobs/<int:repair_id>/delete", methods=["POST"])
@roles_required("customer")
def delete_repair_job(repair_id):
    job = owned_job_or_403(repair_id)

    if job.repair_status != "Pending":
        flash("Only Pending repair requests can be deleted.", "warning")
        return redirect(url_for("customer.repair_jobs"))

    db.session.delete(job)
    db.session.commit()
    flash(f"Repair request #{repair_id} was deleted.", "success")
    return redirect(url_for("customer.repair_jobs"))
