import datetime
from flask import *
import jwt
from requests import session
import psycopg2 as pg
app = Flask(__name__)
app.config["JWT_SECRET"] = "5y5Pr0c10r1ng"
app.config["CONSUMER_SECRET"] = "5y5Pr0c10r1ng"

def generate_jwt(payload):
    payload['exp'] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
    token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        abort(401, description='Token has expired')
    except jwt.InvalidTokenError:
        abort(401, description='Invalid token')

@app.route('/api/auth/lti', methods=['POST'])
def lti_auth():

    consumer_key = request.form.get('oauth_consumer_key')
    signature = request.form.get('oauth_signature')
    user_id = request.form.get('user_id')
    roles = request.form.get('roles', '')
    full_name = request.form.get('lis_person_name_full', 'Unknown User')
    email = request.form.get('lis_person_contact_email_primary', 'unknown@example.com')

    # TODO: Validate LTI OAuth signature (placeholder)
    # if not verify_lti_signature(request.form, app.config['LTI_CONSUMER_SECRET']):
    #     return jsonify({"error": "Invalid LTI signature"}), 401

    # Determine user role from the "roles" field
    user_role = 'teacher' if 'Instructor' in roles else 'student'

    # TODO: Find or create user in your DB
    # user = find_or_create_user_in_db(
    #     canvas_user_id=user_id,
    #     name=full_name,
    #     email=email,
    #     role=user_role
    # )

    token_payload = {
        "sub": user_id,      
        "name": full_name,
        "email": email,
        "role": user_role
    }

    token = generate_jwt(token_payload)

    return jsonify({
        "token": token,
        "user": {
            "id": user_id,
            "role": user_role,
            "name": full_name,
            "email": email
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    """
    Decodes the JWT from the 'Authorization' header and returns user info.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401, description='Missing or invalid Authorization header')

    token = auth_header.split(' ')[1]
    decoded = decode_jwt(token)

    return jsonify({
        "id": decoded.get('sub'),
        "role": decoded.get('role'),
        "name": decoded.get('name'),
        "email": decoded.get('email')
    }), 200


@app.route('/api/exams', methods=['GET', 'POST'])
def exams():
    
    if request.method == "POST":
        data = request.get_json()
        client = pg.connect("")
        cur = client.cursor()
        cur.execute("INSERT INTO exams (name, course, creator, created_at, status, startTime, endTime) VALUES (%s, %s, %s, %s, %s, %s, %s)", (data.get("name"), data.get("course"), data.get("creator"), datetime.datetime.now(), data.get("status"), data.get("startTime"), data.get("endTime")))
        client.commit()
        cur.close()
        client.close()
        return jsonify({"message": "Exam created successfully"}), 201
    elif request.method == "GET":
        client = pg.connect("")
        cur = client.cursor()
        cur.execute("SELECT * FROM exams WHERE creator = %s ORDER BY id", (data.get("teacher_id")))
        response = cur.fetchall()
        mod = []
        if response:
            mod = [{
                "id": row[0],
                "name": row[1],
                "course": row[2],
                "creator": row[3],
                "created_at": row[4].strftime("%Y-%m-%d %H:%M:%S"),
                "status": row[5],
                "startTime": row[6],
                "endTime": row[7]
            } for row in response]
        cur.close()
        client.close()
        return mod
    
    
@app.route('/api/exams/<int:exam_id>', methods=['GET'])
def exam(exam_id):
    client = pg.connect("")
    cur = client.cursor()
    cur.execute("SELECT * FROM exams WHERE id = %s", (exam_id))
    response = cur.fetchone()
    mod = {}
    if response:
        mod = {
                "id": response[0],
                "name": response[1],
                "course": response[2],
                "creator": response[3],
                "created_at": response[4].strftime("%Y-%m-%d %H:%M:%S"),
                "status": response[5],
                "startTime": response[6],
                "endTime": response[7]
            }
    cur.close()
    client.close()
    return jsonify(mod)

@app.route('/api/exams/<int:exam_id>/start', methods=['POST'])
def start_exam(exam_id):
    data = {

    }
    client = pg.connect("")
    cur = client.cursor()
    cur.execute("SELECT * FROM exams WHERE id = %s", (exam_id))
    response = cur.fetchone()
    if response:
        data = {col: response[i] for i, col in zip([n for n in range(len(response))], cur.description)}
        if response[5] == "started":
            data['status'] = "in_progress"
        else:
            cur.execute("UPDATE exams SET status = 'started' WHERE id = %s", (exam_id))
            client.commit()
            cur.close()
            client.close()
        
        return jsonify(data), 200
    else:
        return jsonify({"message": "Exam not found"}), 404
    
@app.route('/api/exams/<int:exam_id>/submit', methods=['POST'])
def submit_exam(exam_id):
    client = pg.connect("")
    cur = client.cursor()
    
    # Check if exam exists and is started
    cur.execute("SELECT * FROM exams WHERE id = %s", (exam_id,))
    exam = cur.fetchone()
    if not exam:
        cur.close()
        client.close()
        return jsonify({"message": "Exam not found"}), 404
        
    if exam[5] != "started":
        cur.close() 
        client.close()
        return jsonify({"message": "Exam not started"}), 400

    # Create session record
    cur.execute("""
        INSERT INTO sessions (exam_id, status, end_time) 
        VALUES (%s, 'completed', NOW()) 
        RETURNING id, exam_id, status, end_time
    """, (exam_id,))
    client.commit()
    
    session = cur.fetchone()
    cur.close()
    client.close()
    
    return jsonify({
        "sessionId": session[0],
        "examId": session[1], 
        "status": session[2],
        "endTime": session[3].strftime("%Y-%m-%d %H:%M:%S")
    })
if __name__ == '__main__':
    app.run(debug=True)