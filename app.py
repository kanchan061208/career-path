from flask import Flask, render_template, request
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.secret_key = "career_project_key"

DB = Path(__file__).with_name("career.db")

CAREERS = {
    "Software Developer": {
        "skills": ["Python", "Programming", "Problem Solving"],
        "interests": ["Programming", "Technology"],
        "description": "Develops software and applications.",
        "courses": ["Python", "Data Structures", "Git"],
    },
    "Data Analyst": {
        "skills": ["Python", "SQL", "Excel", "Statistics"],
        "interests": ["Data", "Research"],
        "description": "Analyzes data to find useful information.",
        "courses": ["SQL", "Excel", "Power BI"],
    },
    "Web Developer": {
        "skills": ["HTML", "CSS", "JavaScript"],
        "interests": ["Websites", "Design"],
        "description": "Creates websites and web applications.",
        "courses": ["HTML", "CSS", "JavaScript"],
    },
    "Cybersecurity Analyst": {
        "skills": ["Networking", "Linux", "Security"],
        "interests": ["Cybersecurity", "Technology"],
        "description": "Helps protect computer systems and networks.",
        "courses": ["Networking", "Linux", "Cybersecurity Basics"],
    },
    "UI/UX Designer": {
        "skills": ["Design", "Creativity", "Communication"],
        "interests": ["Design", "Creativity"],
        "description": "Designs user-friendly digital experiences.",
        "courses": ["Figma", "UI Design", "UX Research"],
    },
}

SKILLS = sorted({skill for career in CAREERS.values() for skill in career["skills"]})
INTERESTS = sorted({interest for career in CAREERS.values() for interest in career["interests"]})


def connect_db():
    return sqlite3.connect(DB)


def create_table():
    with connect_db() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                course TEXT,
                skills TEXT,
                interests TEXT
            )
            """
        )


def recommend_careers(skills, interests):
    results = []

    for career_name, career in CAREERS.items():
        required_skills = set(career["skills"])
        selected_skills = set(skills)

        matched = selected_skills.intersection(required_skills)
        missing = required_skills.difference(selected_skills)

        skill_score = len(matched) / len(required_skills) if required_skills else 0
        interest_matches = len(set(interests).intersection(career["interests"]))
        interest_score = interest_matches / len(career["interests"]) if career["interests"] else 0

        score = int((skill_score * 0.75 + interest_score * 0.25) * 100)

        results.append(
            {
                "name": career_name,
                "score": score,
                "description": career["description"],
                "matched": sorted(matched),
                "missing": sorted(missing),
                "courses": career["courses"],
            }
        )

    return sorted(results, key=lambda item: item["score"], reverse=True)[:3]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()
        skills = request.form.getlist("skills")
        interests = request.form.getlist("interests")

        if not name or not course or not skills:
            return "Please enter your name, course, and at least one skill."

        with connect_db() as con:
            con.execute(
                """
                INSERT INTO students (name, course, skills, interests)
                VALUES (?, ?, ?, ?)
                """,
                (name, course, ", ".join(skills), ", ".join(interests)),
            )

        recommendations = recommend_careers(skills, interests)
        return render_template("results.html", name=name, recommendations=recommendations)

    return render_template("assessment.html", skills=SKILLS, interests=INTERESTS)


@app.route("/records")
def records():
    with connect_db() as con:
        con.row_factory = sqlite3.Row
        students = con.execute("SELECT * FROM students ORDER BY id DESC").fetchall()

    return render_template("records.html", students=students)


if __name__ == "__main__":
    create_table()
    app.run(debug=True)