from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Then define your models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    filters = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))
    company = db.Column(db.String(100))
    model = db.Column(db.String(100))
    sale_date = db.Column(db.String(20))
    price = db.Column(db.Float)
