from flask import Blueprint, request, jsonify, render_template
from .models import db
from .models import Task, Record
from .job_queue import task_queue

bp = Blueprint("main", __name__)

@bp.route("/")  # 🟢 This is your home page
def index():
    return render_template("index.html")

@bp.route("/create-task", methods=["POST"])
def create_task():
    data = request.get_json()
    print("📩 Incoming task filters:", data)

    task = Task(status="pending", filters=data)
    db.session.add(task)
    db.session.commit()

    print("📌 Task saved to DB with ID:", task.id)

    task_queue.put(task)  # ✅ Enqueue task for background processing
    print("🚚 Task enqueued in task_queue")

    return jsonify({ "task_id": task.id })


@bp.route("/task-status/<int:task_id>")
def task_status(task_id):
    db.session.expire_all()
    task = db.session.get(Task, task_id)
    print(f"📡 Polled task {task_id}: {task.status}")
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"status": task.status})

@bp.route("/analytics/<int:task_id>")
def analytics(task_id):
    records = Record.query.filter_by(task_id=task_id).all()
    if not records:
        return jsonify([])

    return jsonify([
        {
            "company": r.company,
            "model": r.model,
            "sale_date": r.sale_date,
            "price": r.price
        } for r in records
    ])

@bp.route("/tasks")
def all_tasks():
    tasks = Task.query.order_by(Task.id.desc()).all()
    return jsonify([
        {
            "id": t.id,
            "status": t.status,
            "filters": t.filters
        } for t in tasks
    ])

@bp.route("/task-history")
def task_history():
    tasks = Task.query.order_by(Task.id.desc()).limit(20).all()
    return jsonify([{"id": t.id, "status": t.status} for t in tasks])

