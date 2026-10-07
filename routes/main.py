from flask import Blueprint, render_template
from models.repair_job import RepairJob
from models.user import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    services = [
        ("Laptop Repair", "Diagnosis, hardware replacement, and performance fixes."),
        ("Computer Repair", "Desktop troubleshooting, upgrades, and maintenance."),
        ("Cellphone Repair", "Screen, battery, charging-port, and software repairs."),
        ("Screen Replacement", "Broken or cracked display replacement service."),
        ("Battery Replacement", "Battery testing and replacement for supported devices."),
        ("OS Installation", "Clean operating-system installation and setup."),
        ("Virus Removal", "Malware cleanup and basic security checks."),
        ("Hardware Diagnosis", "Identify device faults before repair work begins."),
        ("Data Backup & Recovery", "Help protect and recover important files."),
        ("Computer Cleaning", "Dust removal and basic thermal maintenance."),
    ]
    return render_template("index.html", services=services)


@main_bp.route("/repair/<int:repair_id>")
def repair_detail_public_route(repair_id):
    # This route is intentionally blocked unless an authenticated route
    # grants access. Keeping the actual detail route in the protected
    # role blueprints avoids exposing customer information publicly.
    from flask import abort
    abort(403)


@main_bp.app_context_processor
def utility_processor():
    def status_badge(status):
        mapping = {
            "Pending": "text-bg-warning",
            "Diagnosing": "text-bg-info",
            "Waiting for Parts": "text-bg-secondary",
            "In Repair": "text-bg-primary",
            "Ready for Pickup": "text-bg-success",
            "Completed": "text-bg-success",
            "Cancelled": "text-bg-danger",
        }
        return mapping.get(status, "text-bg-secondary")
    return {"status_badge": status_badge}
