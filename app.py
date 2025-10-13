import csv, io
from openpyxl import Workbook
from flask import Flask, render_template, request, redirect, url_for, session, Response, send_file
from database import (db_check_user_by_email, db_delete_application, db_export_applications, db_get_application, 
                      db_get_applications, db_get_reports, db_get_user, db_insert_application, db_insert_user, 
                      db_update_application)

app = Flask(__name__)
app.secret_key = "Praveen"

@app.route('/')
def home():
    
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if db_check_user_by_email(email):
            return render_template("register.html", error="Email already exists!")

        db_insert_user(username, email, password)
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db_get_user(email)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('applications'))

        return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/applications')
def applications():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    apps = db_get_applications(session['user_id'], search, status)

    return render_template("applications.html", applications=apps, search=search, status=status)

@app.route('/add_application', methods=['GET', 'POST'])
def add_application():
    if "user_id" not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        company = request.form['company']
        role = request.form['role']
        date_applied = request.form['date_applied']
        status = request.form['status']

        db_insert_application(session['user_id'], company, role, date_applied, status)
        return redirect(url_for('applications'))

    return render_template("add_application.html", edit=False)

@app.route('/update_application/<int:app_id>', methods=['GET', 'POST'])
def update_application(app_id):
    if "user_id" not in session:
        return redirect(url_for('login'))

    app_data = db_get_application(app_id, session['user_id'])
    if not app_data:
        return "Application not found or not yours!", 404

    if request.method == 'POST':
        company = request.form['company']
        role = request.form['role']
        date_applied = request.form['date_applied']
        status = request.form['status']

        db_update_application(app_id, session['user_id'], company, role, date_applied, status)
        return redirect(url_for('applications'))

    return render_template("add_application.html", application=app_data, edit=True)

@app.route('/delete_application/<int:app_id>')
def delete_application(app_id):
    if "user_id" not in session:
        return redirect(url_for('login'))

    db_delete_application(app_id, session['user_id'])
    return redirect(url_for('applications'))

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    stats = db_get_reports(session['user_id'])
    return render_template('reports.html', stats=stats)

@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    rows = db_export_applications(session['user_id'])

    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(('Company', 'Role', 'Date Applied', 'Status'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for row in rows:
            writer.writerow((row['company'], row['role'], row['date_applied'], row['status']))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=applications.csv"})

@app.route('/export/excel')
def export_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    rows = db_export_applications(session['user_id'])

    wb = Workbook()
    ws = wb.active
    ws.title = "Applications"
    ws.append(["Company", "Role", "Date Applied", "Status"])
    for row in rows:
        ws.append([row['company'], row['role'], str(row['date_applied']), row['status']])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="applications.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True)
