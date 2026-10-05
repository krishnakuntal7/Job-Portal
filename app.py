from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "job_portal_secret_key"


def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        use_pure=True
    )

    return connection


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/jobs")
def jobs():
    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs")

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("jobs.html", jobs=jobs)



@app.route("/job/<int:job_id>")
def job_details(job_id):
    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))

    job = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template("job_details.html", job=job)



@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply_job(job_id):

    if "user_id" not in session:
       return redirect(url_for("login"))

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM jobs WHERE id = %s",
        (job_id,)
    )

    job = cursor.fetchone()

    if request.method == "POST":

        applicant_name = request.form["applicant_name"]
        applicant_email = request.form["applicant_email"]
        resume = request.form["resume"]

        cursor.execute(
            """
            INSERT INTO applications
            (job_id, applicant_name, applicant_email, resume)
            VALUES (%s, %s, %s, %s)
            """,
            (job_id, applicant_name, applicant_email, resume)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/jobs")

    cursor.close()
    connection.close()

    return render_template("apply.html", job=job)


@app.route("/applications")
def applications():

    if "user_id" not in session:
      return redirect(url_for("login"))

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            applications.id,
            applications.applicant_name,
            applications.applicant_email,
            applications.resume,
            applications.applied_at,
            jobs.title AS job_title
        FROM applications
        JOIN jobs
        ON applications.job_id = jobs.id
        ORDER BY applications.applied_at DESC
    """)

    applications = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "applications.html",
        applications=applications
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, password, role)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email = %s AND password = %s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
          session["user_id"] = user["id"]
          session["user_name"] = user["name"]
          session["user_role"] = user["role"]

          return f"Welcome, {user['name']}!"

        return "Invalid email or password"

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
