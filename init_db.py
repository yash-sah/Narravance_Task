from app import create_app, db
from app.models import Task, Record  # This is required so SQLAlchemy knows about models

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database initialized successfully.")
