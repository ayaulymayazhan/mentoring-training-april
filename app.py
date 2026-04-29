from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for


app = Flask(__name__)
app.config["DATABASE"] = Path(__file__).with_name("training.db")
app.config["SECRET_KEY"] = "dev-secret-key"


MODULE_SEED = [
    {
        "id": 1,
        "title": "Roles & Responsibilities (??? ????? ???????)",
        "description": "??????? ?? ?????? ?? ? ?????? ? ????? ?? ? ???????????/?????. ??? ?????? ?? ??????????? ????????, ??? ?????? ? ?????? ????????. ?????? ?? ???? ???????, ?????? ?? ? ??????????? ? ????. ??? ?? ?????? ????? ????, ??? ??????? ? ?????????? ????? ???, ??? ?? ??????????? ????????? ?????? ????? ??????? ? ???????? ???????. ???? ??????? ?????? ? ?? ??? ??? ??????????? ??????? ? ??????????????? ??????.",
        "content": [
            "Transition mindset from individual contributor to supervisor and coach.",
            "Use a daily routine: morning sync, live monitoring, approval loop, and final calibration.",
            "Teach core values: self-study, curiosity, proactivity, discipline, and adaptability.",
            "Follow the workflow: Newbie Draft -> Mentor Review -> Newbie Fix -> Confirmation.",
        ],
        "quiz": [
            {
                "question": "What is the mentor's primary role in this program?",
                "options": [
                    "To close all tickets personally",
                    "To bridge theory with real work and coach learners",
                    "To only run end-of-day reports",
                ],
                "correct_answer": "To bridge theory with real work and coach learners",
            },
            {
                "question": "Which sequence reflects the recommended workflow?",
                "options": [
                    "Mentor Review -> Confirmation -> Newbie Draft",
                    "Newbie Draft -> Mentor Review -> Newbie Fix -> Confirmation",
                    "Confirmation -> Newbie Fix -> Mentor Review",
                ],
                "correct_answer": "Newbie Draft -> Mentor Review -> Newbie Fix -> Confirmation",
            },
        ],
    },
    {
        "id": 2,
        "title": "The Morning Training (??? ??????? ?? ??????)",
        "description": "??? ????????? ???????? ?????? ?? Duplicates, Wrong Emails ? Background Checks.",
        "content": [
            "Cover high-frequency scenarios: Duplicates, Wrong Emails, and Background Checks.",
            "Prepare practical examples and case-based exercises before each session.",
            "Prevent one-way lectures by asking targeted questions and checking understanding.",
            "Create psychological safety so newbies ask questions early and often.",
        ],
        "quiz": [
            {
                "question": "Which format is recommended for morning sessions?",
                "options": [
                    "Case-based practical training",
                    "Only reading policy documents",
                    "Silent self-study with no discussion",
                ],
                "correct_answer": "Case-based practical training",
            },
            {
                "question": "Why should mentors build trust with each newbie?",
                "options": [
                    "To avoid all formal communication",
                    "To reduce questions and speed up meetings",
                    "To make it easier for learners to ask questions and escalate quickly",
                ],
                "correct_answer": "To make it easier for learners to ask questions and escalate quickly",
            },
        ],
    },
    {
        "id": 3,
        "title": "Newbie Management",
        "description": "???????? ?? ?????????? ????????, ????? ? ???? 3-4 ???????.",
        "content": [
            "Prioritize status management and pace control when quality drops.",
            "Treat 20 minutes of silence as a red flag and check in proactively.",
            "Define emergency communication channels during onboarding.",
            "Enforce break protocol updates in team chat to keep visibility.",
        ],
        "quiz": [
            {
                "question": "What should a mentor do when a newbie is silent for 20 minutes?",
                "options": [
                    "Ignore and wait for end-of-day sync",
                    "Escalate immediately to HR",
                    "Treat it as a red flag and proactively check in",
                ],
                "correct_answer": "Treat it as a red flag and proactively check in",
            },
            {
                "question": "Why is break protocol important?",
                "options": [
                    "It helps maintain visibility and coordination",
                    "It eliminates the need for schedules",
                    "It replaces performance reviews",
                ],
                "correct_answer": "It helps maintain visibility and coordination",
            },
        ],
    },
    {
        "id": 4,
        "title": "The Criteria & Grading (??????????? ??????)",
        "description": "??? ??????? ????? ?? 1 ?? 5 ???, ????? ??? ???? fair ? ?????????.",
        "content": [
            "Apply fair scoring from 1 to 5 with shared interpretation.",
            "Calibrate mentors against the same rubric and quality examples.",
            "Track performance consistently in mentoring files.",
            "Write actionable feedback with proof tickets and concrete next steps.",
        ],
        "quiz": [
            {
                "question": "What improves grading consistency across mentors?",
                "options": [
                    "Skipping written criteria",
                    "Rubric calibration and shared definitions",
                    "Using only gut feeling",
                ],
                "correct_answer": "Rubric calibration and shared definitions",
            },
            {
                "question": "What makes feedback high quality?",
                "options": [
                    "Generic praise only",
                    "Actionable steps with evidence tickets",
                    "Very short comments without context",
                ],
                "correct_answer": "Actionable steps with evidence tickets",
            },
        ],
    },
    {
        "id": 5,
        "title": "High-Quality Feedback (Human Firewall)",
        "description": "??? ?????? ?????? ?? ???????, ?? ??????????? ???????",
        "content": [
            "Explain not only what to change, but why it matters for values and security.",
            "Use a 3-revision rule, then switch to synchronous coaching instead of rewriting work.",
            "Maintain brand voice and empathy while enforcing quality standards.",
            "Use reusable feedback templates for frequent mistakes.",
        ],
        "quiz": [
            {
                "question": "What should happen after three weak revisions?",
                "options": [
                    "Mentor rewrites the ticket",
                    "Close the task without feedback",
                    "Escalate to a call/huddle for guided correction",
                ],
                "correct_answer": "Escalate to a call/huddle for guided correction",
            },
            {
                "question": "What is the key feedback principle in this module?",
                "options": [
                    "Focus on why the correction matters",
                    "Only mark answers as wrong",
                    "Avoid discussing business impact",
                ],
                "correct_answer": "Focus on why the correction matters",
            },
        ],
    },
]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                content TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                FOREIGN KEY(module_id) REFERENCES modules(id)
            );

            CREATE TABLE IF NOT EXISTS progress (
                user_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                completion_status TEXT NOT NULL DEFAULT 'not_started',
                score REAL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, module_id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(module_id) REFERENCES modules(id)
            );
            """
        )

        user_count = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
        if user_count == 0:
            conn.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                ("Demo Mentor", "mentor@example.com", "demo-password"),
            )

        module_count = conn.execute("SELECT COUNT(*) AS total FROM modules").fetchone()["total"]
        if module_count == 0:
            for module in MODULE_SEED:
                conn.execute(
                    """
                    INSERT INTO modules(id, title, description, content)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        module["id"],
                        module["title"],
                        module["description"],
                        json.dumps(module["content"]),
                    ),
                )
                for quiz in module["quiz"]:
                    conn.execute(
                        """
                        INSERT INTO quizzes(module_id, question, options, correct_answer)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            module["id"],
                            quiz["question"],
                            json.dumps(quiz["options"]),
                            quiz["correct_answer"],
                        ),
                    )


def module_payload(module_row: sqlite3.Row, include_answers: bool = False) -> dict[str, Any]:
    with get_db() as conn:
        quiz_rows = conn.execute(
            "SELECT id, question, options, correct_answer FROM quizzes WHERE module_id = ? ORDER BY id",
            (module_row["id"],),
        ).fetchall()

    quizzes = []
    for row in quiz_rows:
        item = {
            "id": row["id"],
            "question": row["question"],
            "options": json.loads(row["options"]),
        }
        if include_answers:
            item["correct_answer"] = row["correct_answer"]
        quizzes.append(item)

    return {
        "id": module_row["id"],
        "title": module_row["title"],
        "description": module_row["description"],
        "content": json.loads(module_row["content"]),
        "quizzes": quizzes,
    }


def calculate_progress(user_id: int) -> dict[str, Any]:
    with get_db() as conn:
        total_modules = conn.execute("SELECT COUNT(*) AS total FROM modules").fetchone()["total"]
        completed_modules = conn.execute(
            "SELECT COUNT(*) AS total FROM progress WHERE user_id = ? AND completion_status = 'completed'",
            (user_id,),
        ).fetchone()["total"]
        rows = conn.execute(
            """
            SELECT m.id, m.title, COALESCE(p.completion_status, 'not_started') AS completion_status, p.score
            FROM modules m
            LEFT JOIN progress p ON m.id = p.module_id AND p.user_id = ?
            ORDER BY m.id
            """,
            (user_id,),
        ).fetchall()

    percentage = 0 if total_modules == 0 else round((completed_modules / total_modules) * 100, 1)
    return {
        "user_id": user_id,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "completion_percentage": percentage,
        "modules": [dict(row) for row in rows],
    }


def is_module_unlocked(user_id: int, module_id: int) -> bool:
    if module_id <= 1:
        return True

    with get_db() as conn:
        prev = conn.execute(
            """
            SELECT completion_status
            FROM progress
            WHERE user_id = ? AND module_id = ?
            """,
            (user_id, module_id - 1),
        ).fetchone()
    return bool(prev and prev["completion_status"] == "completed")


def build_module_cards(user_id: int) -> list[dict[str, Any]]:
    with get_db() as conn:
        modules = conn.execute("SELECT id, title, description FROM modules ORDER BY id").fetchall()
        progress_rows = conn.execute(
            """
            SELECT module_id, completion_status
            FROM progress
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchall()

    progress_by_module = {row["module_id"]: row["completion_status"] for row in progress_rows}
    cards = []
    for module in modules:
        module_id = module["id"]
        cards.append(
            {
                "id": module_id,
                "title": module["title"],
                "description": module["description"],
                "completion_status": progress_by_module.get(module_id, "not_started"),
                "is_unlocked": is_module_unlocked(user_id, module_id),
            }
        )
    return cards


def get_workflow_slides() -> list[dict[str, str]]:
    root = Path(__file__).resolve().parent
    captions = [
        "\U0001F4E9 \u041f\u043e\u0441\u0442\u0443\u043f\u0430\u0435\u0442 \u0442\u0438\u043a\u0435\u0442 -> Newbie \u0441\u043e\u0441\u0442\u0430\u0432\u043b\u044f\u0435\u0442 \u0441\u0432\u043e\u0439 draft \u043e\u0442\u0432\u0435\u0442\u0430",
        "\U0001F50D Mentor Review and give feedback",
        "\U0001F527 Newbie \u0432\u043d\u043e\u0441\u0438\u0442 \u043f\u0440\u0430\u0432\u043a\u0438",
        "\u2705 Mentor \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442, \u043e\u0442\u0432\u0435\u0442 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u0435\u0442\u0441\u044f",
    ]
    slides: list[dict[str, str]] = []
    for idx, caption in enumerate(captions, start=1):
        if idx == 1:
            candidates = [
                "Screenshot 2026-04-26 at 19.58.55.png",
                "Screenshot 2026-04-25 at 23.24.06.png",
                f"workflow-{idx}.png",
                f"workflow-{idx}.jpg",
                f"workflow-{idx}.jpeg",
                f"workflow-{idx}.webp",
            ]
        elif idx == 2:
            candidates = [
                "Screenshot 2026-04-26 at 20.08.22.png",
                "Screenshot 2026-04-25 at 23.24.13.png",
                f"workflow-{idx}.png",
                f"workflow-{idx}.jpg",
                f"workflow-{idx}.jpeg",
                f"workflow-{idx}.webp",
            ]
        elif idx == 3:
            candidates = [
                "Screenshot 2026-04-26 at 20.06.58.png",
                "Screenshot 2026-04-26 at 20.03.52.png",
                "Screenshot 2026-04-25 at 23.24.13.png",
                f"workflow-{idx}.png",
                f"workflow-{idx}.jpg",
                f"workflow-{idx}.jpeg",
                f"workflow-{idx}.webp",
            ]
        else:
            candidates = [
                "Screenshot 2026-04-26 at 20.06.43.png",
                "Screenshot 2026-04-26 at 20.04.02.png",
                "Screenshot 2026-04-25 at 23.24.06.png",
                f"workflow-{idx}.png",
                f"workflow-{idx}.jpg",
                f"workflow-{idx}.jpeg",
                f"workflow-{idx}.webp",
            ]
        found_name = None
        for name in candidates:
            if (root / name).exists():
                found_name = name
                break
        if found_name:
            slides.append(
                {
                    "image_url": url_for("workflow_media", filename=found_name),
                    "caption": caption,
                }
            )
        else:
            slides.append(
                {
                    "image_url": "",
                    "caption": caption,
                }
            )
    return slides


def grade_quiz(module_id: int, answers_by_quiz_id: dict[int, str]) -> dict[str, Any]:
    with get_db() as conn:
        quiz_rows = conn.execute(
            "SELECT id, question, correct_answer FROM quizzes WHERE module_id = ? ORDER BY id",
            (module_id,),
        ).fetchall()

    if not quiz_rows:
        return {"score": 0, "total": 0, "correct": 0, "results": []}

    results = []
    correct = 0
    for row in quiz_rows:
        given_answer = answers_by_quiz_id.get(row["id"], "")
        is_correct = given_answer == row["correct_answer"]
        if is_correct:
            correct += 1
        results.append(
            {
                "quiz_id": row["id"],
                "question": row["question"],
                "selected_answer": given_answer,
                "correct_answer": row["correct_answer"],
                "is_correct": is_correct,
            }
        )

    total = len(quiz_rows)
    score = round((correct / total) * 100, 1)
    return {"score": score, "total": total, "correct": correct, "results": results}


@app.route("/")
def landing_page():
    user_id = int(request.args.get("user_id", "1"))
    module_cards = build_module_cards(user_id)
    progress = calculate_progress(user_id)
    return render_template("index.html", modules=module_cards, progress=progress)


@app.get("/assets/shifu-photo")
def shifu_photo():
    return send_file(Path(__file__).with_name("Shifu-43.webp"), mimetype="image/webp")


@app.get("/assets/module-fun-gif")
def module_fun_gif():
    return send_file(Path(__file__).with_name("1cN.mp4"), mimetype="video/mp4")


@app.get("/assets/topic-icon")
def topic_icon():
    return send_file(Path(__file__).with_name("images.png"), mimetype="image/png")


@app.get("/assets/topic-icon-2")
def topic_icon_2():
    return send_file(Path(__file__).with_name("images (1).png"), mimetype="image/png")


@app.get("/assets/topic-icon-3")
def topic_icon_3():
    return send_file(Path(__file__).with_name("focus-icon-design-free-vector.jpg"), mimetype="image/jpeg")


@app.get("/assets/topic-icon-4")
def topic_icon_4():
    return send_file(Path(__file__).with_name("auu.png"), mimetype="image/png")


@app.get("/assets/workflow-media/<path:filename>")
def workflow_media(filename: str):
    safe_name = Path(filename).name
    return send_file(Path(__file__).with_name(safe_name))


@app.get("/assets/module4-topic-image")
def module4_topic_image():
    image_path = Path.home() / "Downloads" / "image (2).png"
    if not image_path.exists():
        return "Module 4 image not found", 404
    return send_file(image_path, mimetype="image/png")


@app.get("/assets/module5-sandwich-image")
def module5_sandwich_image():
    image_path = Path.home() / "Downloads" / "ai-generated-sandwich-with-ham-cheese-tomatoes-and-lettuce-isolated-on-transparent-background-png.webp"
    if not image_path.exists():
        return "Module 5 sandwich image not found", 404
    return send_file(image_path, mimetype="image/webp")


@app.route("/course/module/<int:module_id>")
def module_page(module_id: int):
    user_id = int(request.args.get("user_id", "1"))
    if not is_module_unlocked(user_id, module_id):
        return redirect(url_for("landing_page", user_id=user_id))

    with get_db() as conn:
        module_row = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()

    if not module_row:
        return "Module not found", 404

    module = module_payload(module_row)
    module_tabs = build_module_cards(user_id)
    workflow_slides = get_workflow_slides() if module_id == 1 else []
    return render_template(
        "module.html",
        module=module,
        user_id=user_id,
        workflow_slides=workflow_slides,
        module_tabs=module_tabs,
    )


@app.route("/course/module/<int:module_id>/quiz", methods=["POST"])
def submit_quiz_page(module_id: int):
    user_id = int(request.form.get("user_id", "1"))
    if not is_module_unlocked(user_id, module_id):
        return redirect(url_for("landing_page", user_id=user_id))

    answers_by_quiz_id: dict[int, str] = {}
    for key, value in request.form.items():
        if key.startswith("quiz_"):
            quiz_id = int(key.replace("quiz_", ""))
            answers_by_quiz_id[quiz_id] = value

    result = grade_quiz(module_id, answers_by_quiz_id)
    completion_status = "completed" if result["score"] >= 70 else "in_progress"
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO progress(user_id, module_id, completion_status, score, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, module_id) DO UPDATE SET
                completion_status = excluded.completion_status,
                score = excluded.score,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, module_id, completion_status, result["score"]),
        )

    return render_template("quiz_result.html", result=result, module_id=module_id, user_id=user_id)


@app.route("/course/module/<int:module_id>/next", methods=["POST"])
def complete_and_next_module(module_id: int):
    user_id = int(request.form.get("user_id", "1"))
    if not is_module_unlocked(user_id, module_id):
        return redirect(url_for("landing_page", user_id=user_id))

    confirmed = request.form.get("material_completed")
    if confirmed != "yes":
        return redirect(url_for("module_page", module_id=module_id, user_id=user_id))

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO progress(user_id, module_id, completion_status, score, updated_at)
            VALUES (?, ?, 'completed', COALESCE((SELECT score FROM progress WHERE user_id = ? AND module_id = ?), NULL), CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, module_id) DO UPDATE SET
                completion_status = 'completed',
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, module_id, user_id, module_id),
        )
        next_row = conn.execute(
            "SELECT id FROM modules WHERE id > ? ORDER BY id LIMIT 1",
            (module_id,),
        ).fetchone()

    if next_row:
        return redirect(url_for("module_page", module_id=next_row["id"], user_id=user_id))
    return redirect(url_for("progress_page", user_id=user_id))


@app.route("/progress")
def progress_page():
    user_id = int(request.args.get("user_id", "1"))
    progress = calculate_progress(user_id)
    return render_template("progress.html", progress=progress)


@app.get("/modules")
def get_modules():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM modules ORDER BY id").fetchall()
    payload = [module_payload(row) for row in rows]
    return jsonify(payload)


@app.get("/module/<int:module_id>")
def get_module(module_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if not row:
        return jsonify({"error": "Module not found"}), 404
    return jsonify(module_payload(row))


@app.post("/progress")
def post_progress():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    module_id = payload.get("module_id")
    completion_status = payload.get("completion_status", "in_progress")

    if not user_id or not module_id:
        return jsonify({"error": "user_id and module_id are required"}), 400

    if completion_status not in {"not_started", "in_progress", "completed"}:
        return jsonify({"error": "completion_status must be not_started, in_progress, or completed"}), 400

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO progress(user_id, module_id, completion_status, score, updated_at)
            VALUES (?, ?, ?, NULL, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, module_id) DO UPDATE SET
                completion_status = excluded.completion_status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, module_id, completion_status),
        )

    return jsonify({"message": "Progress updated"}), 200


@app.post("/quiz")
def post_quiz():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    module_id = payload.get("module_id")
    answers = payload.get("answers", [])

    if not user_id or not module_id:
        return jsonify({"error": "user_id and module_id are required"}), 400
    if not isinstance(answers, list):
        return jsonify({"error": "answers must be a list"}), 400

    answers_by_quiz_id: dict[int, str] = {}
    for answer in answers:
        if "quiz_id" not in answer or "answer" not in answer:
            return jsonify({"error": "Each answer must include quiz_id and answer"}), 400
        answers_by_quiz_id[int(answer["quiz_id"])] = str(answer["answer"])

    result = grade_quiz(int(module_id), answers_by_quiz_id)
    completion_status = "completed" if result["score"] >= 70 else "in_progress"

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO progress(user_id, module_id, completion_status, score, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, module_id) DO UPDATE SET
                completion_status = excluded.completion_status,
                score = excluded.score,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, module_id, completion_status, result["score"]),
        )

    return jsonify(
        {
            "message": "Quiz evaluated",
            "module_id": module_id,
            "user_id": user_id,
            "score": result["score"],
            "correct_answers": result["correct"],
            "total_questions": result["total"],
            "results": result["results"],
        }
    )


@app.route("/reset-demo")
def reset_demo():
    user_id = int(request.args.get("user_id", "1"))
    with get_db() as conn:
        conn.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
    return redirect(url_for("landing_page", user_id=user_id))


if __name__ == "__main__":
    init_db()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5055"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
