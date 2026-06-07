import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATA_FILE = Path(os.environ.get("TASKHUB_DATA", "data/tasks.json"))


def load_tasks():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save_tasks(tasks):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(tasks, indent=2))


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks())


@app.route("/api/tasks", methods=["POST"])
def create_task():
    tasks = load_tasks()
    data = request.get_json()
    task = {
        "id": next_id(tasks),
        "title": data.get("title", "").strip(),
        "done": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if not task["title"]:
        return jsonify({"error": "Title is required"}), 400
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    tasks = load_tasks()
    data = request.get_json()
    for task in tasks:
        if task["id"] == task_id:
            if "title" in data:
                title = data["title"].strip()
                if not title:
                    return jsonify({"error": "Title cannot be empty"}), 400
                task["title"] = title
            if "done" in data:
                task["done"] = bool(data["done"])
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Task not found"}), 404
    save_tasks(new_tasks)
    return jsonify({"deleted": task_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
