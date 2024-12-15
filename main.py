from flask import Flask, jsonify, request, render_template
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection function
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Official1996*',
        db='llc_tax_management',
        cursorclass=pymysql.cursors.DictCursor  # Return results as dictionaries for easier access
    )

# Helper function to fetch all tax records
def fetch_all_records():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tax_payments")
            records = cursor.fetchall()
        return records
    finally:
        connection.close()

# Route: Render the main HTML page
@app.route('/')
def index():
    records = fetch_all_records()  # Fetch all records to display on the page
    return render_template('index.html', records=records)

# Route: Add a tax record
@app.route('/add_tax_record', methods=['POST'])
def add_tax_record():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Extract data from the request
    company = data.get('company')
    amount = data.get('amount')
    payment_date = data.get('payment_date')
    status = data.get('status')
    due_date = data.get('due_date')

    # Check for missing required fields
    if not all([company, amount, status, due_date]):
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Insert the new record into the database
            sql = """
                INSERT INTO tax_payments (company, amount, payment_date, status, due_date)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (company, amount, payment_date, status, due_date))
            connection.commit()

            # Fetch the newly added record
            record_id = cursor.lastrowid
            cursor.execute("SELECT * FROM tax_payments WHERE id = %s", (record_id,))
            new_record = cursor.fetchone()

        return jsonify({'message': 'Record added successfully', 'record': new_record})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

# Route to delete a record
@app.route('/delete_tax_record/<int:id>', methods=['DELETE'])
def delete_tax_record(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM tax_payments WHERE id = %s"
            cursor.execute(sql, (id,))
            connection.commit()
        return jsonify({'message': 'Record deleted successfully'})
    finally:
        connection.close()


@app.route('/edit/<int:record_id>')
def edit_record(record_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tax_payments WHERE id = %s", (record_id,))
            record = cursor.fetchone()
        return render_template('edit.html', record=record)
    finally:
        connection.close()


@app.route('/update_tax_record/<int:record_id>', methods=['PUT'])
def update_tax_record(record_id):
    data = request.json
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE tax_payments
                SET company = %s, amount = %s, payment_date = %s, status = %s, due_date = %s
                WHERE id = %s
            """
            cursor.execute(sql, (data['company'], data['amount'], data['payment_date'], data['status'], data['due_date'], record_id))
            connection.commit()
        return jsonify({'message': 'Record updated successfully'})
    finally:
        connection.close()

@app.route('/filter_records/<due_date>', methods=['GET'])
def filter_records(due_date):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tax_payments WHERE due_date = %s", (due_date,))
            records = cursor.fetchall()
        return jsonify({'records': records})
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
