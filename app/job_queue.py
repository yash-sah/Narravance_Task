# from queue import Queue
# import time
# from .models import db, Task, Record
# from .utils.source_a import get_data_from_source_a
# from .utils.source_b import get_data_from_source_b

# task_queue = Queue()

# def job_worker(app):
#     def _run():
#         print("⚙️ Background worker started!")

#         with app.app_context():
#             while True:
#                 task_stub = task_queue.get()
#                 task = db.session.get(Task, task_stub.id) 
#                 print(f"🛠️ Got task ID: {task.id}")

#                 try:
#                     task.status = "in progress"
#                     db.session.commit()

#                     filters = task.filters
#                     a_data = get_data_from_source_a(filters["start"], filters["end"])
#                     b_data = get_data_from_source_b(filters["start"], filters["end"], filters["companies"])
#                     unified = a_data + b_data

#                     print(f"📥 Inserting {len(unified)} records for Task {task.id}...")

#                     for item in unified:
#                         db.session.add(Record(
#                             task_id=task.id,
#                             company=item["company"],
#                             model=item["model"],
#                             sale_date=item["sale_date"],
#                             price=float(item["price"])
#                         ))

#                     task.status = "completed"
#                     db.session.commit()
#                     print(f"✅ Task {task.id} completed successfully.")

#                 except Exception as e:
#                     print(f"❌ Error processing task {task.id}: {e}")
#                     db.session.rollback()

#                 finally:
#                     db.session.remove()  # 🔥 This clears out stale connections/sessions
#                     task_queue.task_done()
#     return _run
import time
from .models import db, Task, Record
from queue import Queue
from .utils.source_a import get_data_from_source_a
from .utils.source_b import get_data_from_source_b

task_queue = Queue()

def job_worker(app):
    def _run():
        print("⚙️ Background worker started!")

        with app.app_context():
            while True:
                task_stub = task_queue.get()
                task = db.session.get(Task, task_stub.id)

                try:
                    # 💤 Simulate delay before processing
                    time.sleep(5)

                    task.status = "in progress"
                    db.session.commit()
                    print(f"🚧 Task {task.id} is now in progress")

                    # 💤 Simulate processing time
                    time.sleep(5)

                    filters = task.filters
                    a_data = get_data_from_source_a(filters["start"], filters["end"])
                    b_data = get_data_from_source_b(filters["start"], filters["end"], filters["companies"])
                    unified = a_data + b_data

                    print(f"📥 Inserting {len(unified)} records for Task {task.id}...")

                    for item in unified:
                        db.session.add(Record(
                            task_id=task.id,
                            company=item["company"],
                            model=item["model"],
                            sale_date=item["sale_date"],
                            price=float(item["price"])
                        ))

                    task.status = "completed"
                    db.session.commit()
                    print(f"✅ Task {task.id} completed successfully.")

                except Exception as e:
                    print(f"❌ Error processing task {task.id}: {e}")
                    db.session.rollback()

                finally:
                    db.session.remove()
                    task_queue.task_done()

    return _run
