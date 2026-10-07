import os
from flask import Flask, render_template
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.customer import customer_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return render_template("500.html"), 500

    with app.app_context():
        # Import models before create_all so SQLAlchemy knows the tables.
        from models.user import User  # noqa: F401
        from models.repair_job import RepairJob  # noqa: F401
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
