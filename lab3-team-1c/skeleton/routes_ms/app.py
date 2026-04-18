from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_conn():
    return mysql.connector.connect(
        host='routes_db',
        user='root',
        password='root',
        database='routes_db'
    )

@app.route('/health')
def health():
    return jsonify(status='ok', service='routes_ms')

@app.route('/records')
def get_records():
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM records")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(records=rows)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/records', methods=['POST'])
def create_record():
    try:
        data = request.json or {}
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO records (name) VALUES (%s)",
            (data.get('name', 'unknown'),)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(status='created'), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
