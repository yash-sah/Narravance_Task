import time
from queue import Queue
from .models import db, Task, Record
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
                print(f"🛠️ Got task ID: {task.id}")

                try:
                    time.sleep(2)
                    task.status = "in progress"
                    db.session.commit()
                    print(f"🚧 Task {task.id} is now in progress")

                    time.sleep(2)
                    filters = task.filters
                    print(f"🔎 Filters: {filters}")

                    # Fetch raw data
                    a_data = get_data_from_source_a(filters["start"], filters["end"])
                    b_data = get_data_from_source_b(filters["start"], filters["end"], filters["companies"])

                    print(f"📦 Source A: {len(a_data)} records, Source B: {len(b_data)} records")

                    # Normalize and filter
                    companies_set = set(c.strip().lower() for c in filters["companies"])
                    filtered_data = [
                        item for item in a_data + b_data
                        if item["company"].lower() in companies_set
                    ]

                    print(f"🔍 Filtered valid records: {len(filtered_data)}")

                    # Early exit if no matching records
                    if not filtered_data:
                        print(f"⚠️ No matching records. Marking Task {task.id} as completed.")
                        task.status = "completed"
                        db.session.commit()
                        db.session.remove()
                        task_queue.task_done()
                        continue

                    # Insert records
                    print(f"📥 Inserting {len(filtered_data)} records for Task {task.id}...")

                    records = [
                        Record(
                            task_id=task.id,
                            company=item["company"],
                            model=item["model"],
                            sale_date=item["sale_date"],
                            price=float(item["price"])
                        )
                        for item in filtered_data
                    ]

                    db.session.add_all(records)
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
