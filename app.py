from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import (
    init_database, get_all_questions, get_forms, get_topics,
    add_question, update_question, delete_question,
    add_form, add_topic, delete_form, delete_topic,
    get_question
)
from classifier import classify_question

app = Flask(__name__)
init_database()

@app.route("/")
def index():
    questions = get_all_questions()
    forms = get_forms()
    topics = get_topics()
    return render_template(
        "index.html",
        questions=questions,
        forms=forms,
        topics=topics
    )


@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("questions", "")
    selected_form_id = request.form.get("form_id", "").strip()
    selected_topic_id = request.form.get("topic_id", "").strip()

    for line in text.splitlines():
        question = line.strip()
        if not question:
            continue

        # Nếu người dùng chọn Form/Topic thì ưu tiên lựa chọn đó.
        # Nếu để Auto thì hệ thống tự phân loại.
        result = classify_question(question)

        form_id = int(selected_form_id) if selected_form_id else result["form_id"]
        topic_id = int(selected_topic_id) if selected_topic_id else result["topic_id"]

        add_question(question, form_id, topic_id)

    return redirect(url_for("index"))


@app.route("/edit/<int:question_id>", methods=["POST"])
def edit(question_id):
    question = request.form.get("question", "").strip()
    form_id = request.form.get("form_id", "").strip()
    topic_id = request.form.get("topic_id", "").strip()

    if question and form_id and topic_id:
        update_question(question_id, question, int(form_id), int(topic_id))

    return redirect(url_for("index"))


@app.route("/delete/<int:question_id>", methods=["POST"])
def delete(question_id):
    delete_question(question_id)
    return redirect(url_for("index"))


@app.route("/forms/add", methods=["POST"])
def create_form():
    name = request.form.get("name", "").strip()
    if name:
        add_form(name)
    return redirect(url_for("index"))


@app.route("/topics/add", methods=["POST"])
def create_topic():
    name = request.form.get("name", "").strip()
    if name:
        add_topic(name)
    return redirect(url_for("index"))


@app.route("/forms/delete/<int:form_id>", methods=["POST"])
def remove_form(form_id):
    delete_form(form_id)
    return redirect(url_for("index"))


@app.route("/topics/delete/<int:topic_id>", methods=["POST"])
def remove_topic(topic_id):
    delete_topic(topic_id)
    return redirect(url_for("index"))


@app.route("/api/questions")
def api_questions():
    return jsonify([
        {
            "id": q["id"],
            "question": q["question"],
            "form_id": q["form_id"],
            "form": q["form_name"],
            "topic_id": q["topic_id"],
            "topic": q["topic_name"]
        }
        for q in get_all_questions()
    ])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
