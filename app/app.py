"""
Student Data Management System — Flask Application
Reads all DB credentials from environment variables (never hard-coded).
"""
import os
import pymysql
import pymysql.cursors
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sms-docker-secret-key-2024")


# ── Database helper ────────────────────────────────────────────────────────────

def get_db():
    """Return a new PyMySQL connection using environment variables."""
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "smsuser"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "studentdb"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM students")
            student_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM courses")
            course_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM enrollments")
            enrollment_count = cur.fetchone()["cnt"]
            cur.execute(
                "SELECT student_id, first_name, last_name, department, status "
                "FROM students ORDER BY created_at DESC LIMIT 5"
            )
            recent_students = cur.fetchall()
    finally:
        conn.close()
    return render_template(
        "dashboard.html",
        student_count=student_count,
        course_count=course_count,
        enrollment_count=enrollment_count,
        recent_students=recent_students,
    )


# ── Students ───────────────────────────────────────────────────────────────────

@app.route("/students")
def students_list():
    q = request.args.get("q", "").strip()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if q:
                like = f"%{q}%"
                cur.execute(
                    "SELECT * FROM students "
                    "WHERE first_name LIKE %s OR last_name LIKE %s "
                    "   OR national_id LIKE %s OR department LIKE %s "
                    "ORDER BY last_name, first_name",
                    (like, like, like, like),
                )
            else:
                cur.execute("SELECT * FROM students ORDER BY last_name, first_name")
            students = cur.fetchall()
    finally:
        conn.close()
    return render_template("students/list.html", students=students, q=q)


@app.route("/students/add", methods=["GET", "POST"])
def students_add():
    if request.method == "POST":
        f = request.form
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO students "
                    "(first_name,last_name,national_id,email,date_of_birth,"
                    " gender,department,enrollment_date,gpa,status) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        f["first_name"], f["last_name"], f["national_id"],
                        f["email"], f["date_of_birth"], f["gender"],
                        f["department"], f["enrollment_date"],
                        f.get("gpa") or 0.00, f["status"],
                    ),
                )
            conn.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for("students_list"))
        except pymysql.err.IntegrityError as e:
            flash(f"Database error: {e.args[1]}", "danger")
        finally:
            conn.close()
    return render_template("students/form.html", student=None, action="Add")


@app.route("/students/<int:sid>/edit", methods=["GET", "POST"])
def students_edit(sid):
    conn = get_db()
    try:
        if request.method == "POST":
            f = request.form
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE students SET "
                    "first_name=%s,last_name=%s,national_id=%s,email=%s,"
                    "date_of_birth=%s,gender=%s,department=%s,"
                    "enrollment_date=%s,gpa=%s,status=%s "
                    "WHERE student_id=%s",
                    (
                        f["first_name"], f["last_name"], f["national_id"],
                        f["email"], f["date_of_birth"], f["gender"],
                        f["department"], f["enrollment_date"],
                        f.get("gpa") or 0.00, f["status"], sid,
                    ),
                )
            conn.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for("students_list"))
        else:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
                student = cur.fetchone()
            if not student:
                flash("Student not found.", "danger")
                return redirect(url_for("students_list"))
            return render_template("students/form.html", student=student, action="Edit")
    except pymysql.err.IntegrityError as e:
        flash(f"Database error: {e.args[1]}", "danger")
        return redirect(url_for("students_list"))
    finally:
        conn.close()


@app.route("/students/<int:sid>/delete", methods=["POST"])
def students_delete(sid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE student_id=%s", (sid,))
        conn.commit()
        flash("Student deleted (and all their enrollments).", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("students_list"))


@app.route("/students/<int:sid>/enrollments")
def student_enrollments(sid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
            student = cur.fetchone()
            cur.execute(
                "SELECT e.enrollment_id, e.grade, e.letter_grade, e.enrolled_at, "
                "       c.course_code, c.course_name, c.credit_hours "
                "FROM enrollments e "
                "JOIN courses c ON e.course_id=c.course_id "
                "WHERE e.student_id=%s ORDER BY e.enrolled_at DESC",
                (sid,),
            )
            enrollments = cur.fetchall()
    finally:
        conn.close()
    return render_template(
        "students/enrollments.html", student=student, enrollments=enrollments
    )


# ── Courses ────────────────────────────────────────────────────────────────────

@app.route("/courses")
def courses_list():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM courses ORDER BY course_code")
            courses = cur.fetchall()
    finally:
        conn.close()
    return render_template("courses/list.html", courses=courses)


@app.route("/courses/add", methods=["GET", "POST"])
def courses_add():
    if request.method == "POST":
        f = request.form
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO courses "
                    "(course_code,course_name,credit_hours,instructor_name,"
                    " department,semester,academic_year) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (
                        f["course_code"], f["course_name"], f["credit_hours"],
                        f["instructor_name"], f["department"],
                        f["semester"], f["academic_year"],
                    ),
                )
            conn.commit()
            flash("Course added successfully!", "success")
            return redirect(url_for("courses_list"))
        except pymysql.err.IntegrityError as e:
            flash(f"Database error: {e.args[1]}", "danger")
        finally:
            conn.close()
    return render_template("courses/form.html", course=None, action="Add")


@app.route("/courses/<int:cid>/edit", methods=["GET", "POST"])
def courses_edit(cid):
    conn = get_db()
    try:
        if request.method == "POST":
            f = request.form
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE courses SET "
                    "course_code=%s,course_name=%s,credit_hours=%s,"
                    "instructor_name=%s,department=%s,semester=%s,academic_year=%s "
                    "WHERE course_id=%s",
                    (
                        f["course_code"], f["course_name"], f["credit_hours"],
                        f["instructor_name"], f["department"],
                        f["semester"], f["academic_year"], cid,
                    ),
                )
            conn.commit()
            flash("Course updated successfully!", "success")
            return redirect(url_for("courses_list"))
        else:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM courses WHERE course_id=%s", (cid,))
                course = cur.fetchone()
            if not course:
                flash("Course not found.", "danger")
                return redirect(url_for("courses_list"))
            return render_template("courses/form.html", course=course, action="Edit")
    except pymysql.err.IntegrityError as e:
        flash(f"Database error: {e.args[1]}", "danger")
        return redirect(url_for("courses_list"))
    finally:
        conn.close()


@app.route("/courses/<int:cid>/delete", methods=["POST"])
def courses_delete(cid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM courses WHERE course_id=%s", (cid,))
        conn.commit()
        flash("Course deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("courses_list"))


# ── Enrollments ────────────────────────────────────────────────────────────────

@app.route("/enrollments")
def enrollments_list():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT e.enrollment_id, e.grade, e.letter_grade, e.enrolled_at, "
                "       s.student_id, s.first_name, s.last_name, "
                "       c.course_id, c.course_code, c.course_name "
                "FROM enrollments e "
                "JOIN students s ON e.student_id=s.student_id "
                "JOIN courses  c ON e.course_id=c.course_id "
                "ORDER BY e.enrolled_at DESC"
            )
            enrollments = cur.fetchall()
    finally:
        conn.close()
    return render_template("enrollments/list.html", enrollments=enrollments)


@app.route("/enrollments/add", methods=["GET", "POST"])
def enrollments_add():
    conn = get_db()
    try:
        if request.method == "POST":
            f = request.form
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO enrollments (student_id, course_id) VALUES (%s,%s)",
                    (f["student_id"], f["course_id"]),
                )
            conn.commit()
            flash("Student enrolled successfully!", "success")
            return redirect(url_for("enrollments_list"))
        with conn.cursor() as cur:
            cur.execute(
                "SELECT student_id, first_name, last_name FROM students ORDER BY last_name"
            )
            students = cur.fetchall()
            cur.execute(
                "SELECT course_id, course_code, course_name FROM courses ORDER BY course_code"
            )
            courses = cur.fetchall()
        return render_template(
            "enrollments/form.html",
            enrollment=None, students=students, courses=courses, action="Enroll",
        )
    except pymysql.err.IntegrityError as e:
        flash(f"Error: {e.args[1]}", "danger")
        return redirect(url_for("enrollments_list"))
    finally:
        conn.close()


@app.route("/enrollments/<int:eid>/edit", methods=["GET", "POST"])
def enrollments_edit(eid):
    conn = get_db()
    try:
        if request.method == "POST":
            f = request.form
            grade = f.get("grade") or None
            letter_grade = f.get("letter_grade") or None
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE enrollments SET grade=%s,letter_grade=%s "
                    "WHERE enrollment_id=%s",
                    (grade, letter_grade, eid),
                )
            conn.commit()
            flash("Grade updated!", "success")
            return redirect(url_for("enrollments_list"))
        else:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT e.*, s.first_name, s.last_name, "
                    "       c.course_code, c.course_name "
                    "FROM enrollments e "
                    "JOIN students s ON e.student_id=s.student_id "
                    "JOIN courses  c ON e.course_id=c.course_id "
                    "WHERE e.enrollment_id=%s",
                    (eid,),
                )
                enrollment = cur.fetchone()
            if not enrollment:
                flash("Enrollment not found.", "danger")
                return redirect(url_for("enrollments_list"))
            return render_template(
                "enrollments/form.html",
                enrollment=enrollment, students=None, courses=None, action="Edit Grade",
            )
    finally:
        conn.close()


@app.route("/enrollments/<int:eid>/delete", methods=["POST"])
def enrollments_delete(eid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM enrollments WHERE enrollment_id=%s", (eid,))
        conn.commit()
        flash("Student dropped from course.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for("enrollments_list"))


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
