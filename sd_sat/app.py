
from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread

app = Flask(__name__)

# Database simulation
jobs = [
    {"id": 1, "title": "Python Developer"},
    {"id": 2, "title": "Java Developer"}
]
applications = []

# Cache and message queue
cache = {}
messages = Queue()


# Job Service
@app.route('/api/jobs', methods=['GET'])
def search_jobs():
    if "jobs" not in cache:
        cache["jobs"] = jobs
        print("Fetching jobs from database")
    else:
        print("Fetching jobs from cache")
    return jsonify(cache["jobs"]), 200


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def job_details(job_id):
    for job in jobs:
        if job["id"] == job_id:
            return jsonify(job), 200
    return jsonify({"error": "Job not found"}), 404


# Application Service
@app.route('/api/jobs/<int:job_id>/applications',
           methods=['POST'])
def apply_job(job_id):
    if not any(j["id"] == job_id for j in jobs):
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json(silent=True) or {}
    if not data.get("userId"):
        return jsonify({"error": "userId required"}), 400

    application = {
        "applicationId": len(applications) + 1,
        "userId": data["userId"],
        "jobId": job_id,
        "status": "SUBMITTED"
    }

    applications.append(application)
    messages.put(application)

    return jsonify(application), 201


# Application Status
@app.route('/api/applications/<int:app_id>/status',
           methods=['GET'])
def application_status(app_id):
    for application in applications:
        if application["applicationId"] == app_id:
            return jsonify({
                "status": application["status"]
            }), 200
    return jsonify({"error": "Application not found"}), 404


# Application History
@app.route('/api/users/<int:user_id>/applications',
           methods=['GET'])
def application_history(user_id):
    result = [
        a for a in applications if a["userId"] == user_id
    ]
    return jsonify(result), 200


# Notification Service
def notification_service():
    while not messages.empty():
        application = messages.get()
        print(
            "Notification sent for application:",
            application["applicationId"]
        )
        messages.task_done()


@app.route('/api/notifications/process', methods=['POST'])
def process_notifications():
    worker = Thread(target=notification_service)
    worker.start()
    worker.join()
    return jsonify({"message": "Notifications processed"}), 200
@app.route('/')
def home():
    return """
    <h1>Online Job Recruitment Platform</h1>
    <p><a href="/api/jobs">View All Jobs</a></p>
    <p><a href="/api/jobs/1">View Job Details</a></p>
    """


if __name__ == '__main__':
    app.run(debug=True)
