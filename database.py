import sqlite3
from pathlib import Path

DATABASE = Path(__file__).with_name("questions.db")


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    conn = get_connection()

    # Bảng mới
    conn.execute("""
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            form_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE RESTRICT,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE RESTRICT
        )
    """)

    seed_forms = [
        "What", "When", "Where", "Why", "Who", "How",
        "Do / Does / Did", "Is / Are / Was / Were",
        "Can / Could", "Have / Has", "Would",
        "Tell Me About", "Describe", "Other"
    ]

    seed_topics = [
        "Family", "Travel", "Food", "Education", "Work",
        "Free Time", "Hometown", "Technology", "Shopping",
        "Weather", "Other"
    ]

    for name in seed_forms:
        conn.execute("INSERT OR IGNORE INTO forms (name) VALUES (?)", (name,))

    for name in seed_topics:
        conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (name,))

    conn.commit()

    # Tự nâng cấp database V1 cũ:
    # V1 có questions(question, form, topic), còn V2 dùng form_id/topic_id.
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(questions)").fetchall()
    }

    if "form" in columns and "topic" in columns and "form_id" not in columns:
        old_rows = conn.execute(
            "SELECT id, question, form, topic, created_at FROM questions"
        ).fetchall()

        conn.execute("ALTER TABLE questions RENAME TO questions_old")

        conn.execute("""
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                form_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (form_id) REFERENCES forms(id) ON DELETE RESTRICT,
                FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE RESTRICT
            )
        """)

        form_map = {
            row["name"].lower(): row["id"]
            for row in conn.execute("SELECT id, name FROM forms")
        }
        topic_map = {
            row["name"].lower(): row["id"]
            for row in conn.execute("SELECT id, name FROM topics")
        }

        other_form_id = form_map["other"]
        other_topic_id = topic_map["other"]

        for row in old_rows:
            form_id = form_map.get(str(row["form"]).lower(), other_form_id)
            topic_id = topic_map.get(str(row["topic"]).lower(), other_topic_id)

            conn.execute("""
                INSERT INTO questions (id, question, form_id, topic_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row["id"],
                row["question"],
                form_id,
                topic_id,
                row["created_at"]
            ))

        conn.execute("DROP TABLE questions_old")
        conn.commit()

    conn.close()


def get_forms():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM forms ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


def get_topics():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM topics ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


def get_all_questions():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            q.id,
            q.question,
            q.form_id,
            q.topic_id,
            q.created_at,
            f.name AS form_name,
            t.name AS topic_name
        FROM questions q
        JOIN forms f ON q.form_id = f.id
        JOIN topics t ON q.topic_id = t.id
        ORDER BY q.id DESC
    """).fetchall()
    conn.close()
    return rows


def get_question(question_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT q.*, f.name AS form_name, t.name AS topic_name
        FROM questions q
        JOIN forms f ON q.form_id = f.id
        JOIN topics t ON q.topic_id = t.id
        WHERE q.id = ?
    """, (question_id,)).fetchone()
    conn.close()
    return row


def add_question(question, form_id, topic_id):
    conn = get_connection()
    conn.execute("""
        INSERT INTO questions (question, form_id, topic_id)
        VALUES (?, ?, ?)
    """, (question, form_id, topic_id))
    conn.commit()
    conn.close()


def update_question(question_id, question, form_id, topic_id):
    conn = get_connection()
    conn.execute("""
        UPDATE questions
        SET question = ?, form_id = ?, topic_id = ?
        WHERE id = ?
    """, (question, form_id, topic_id, question_id))
    conn.commit()
    conn.close()


def delete_question(question_id):
    conn = get_connection()
    conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


def add_form(name):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO forms (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def add_topic(name):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def delete_form(form_id):
    conn = get_connection()
    used = conn.execute(
        "SELECT COUNT(*) AS count FROM questions WHERE form_id = ?",
        (form_id,)
    ).fetchone()["count"]

    # Không xóa nếu đang có câu hỏi dùng Form này.
    if used == 0:
        conn.execute("DELETE FROM forms WHERE id = ?", (form_id,))
        conn.commit()

    conn.close()


def delete_topic(topic_id):
    conn = get_connection()
    used = conn.execute(
        "SELECT COUNT(*) AS count FROM questions WHERE topic_id = ?",
        (topic_id,)
    ).fetchone()["count"]

    # Không xóa nếu đang có câu hỏi dùng Topic này.
    if used == 0:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        conn.commit()

    conn.close()
