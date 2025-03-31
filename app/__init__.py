import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import threading
from .models import db 
from .routes import bp as main_bp
from .job_queue import job_worker

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static")
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(main_bp)

    thread = threading.Thread(target=job_worker(app), daemon=True)
    thread.start()

    return app