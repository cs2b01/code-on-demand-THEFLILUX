from flask import Flask,render_template, request, session, Response, redirect
from sqlalchemy import or_
from database import connector
from model import entities
import time
import json

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

@app.route('/authenticate', methods = ['POST'])
def authenticate():
    time.sleep(1)
    message = json.loads(request.data)
    username = message['username']
    password = message['password']

    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User
            ).filter(entities.User.username == username
            ).filter(entities.User.password == password
            ).one()
        session['logged_user'] = user.id
        message = {'message': 'Authorized'}
        return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=200, mimetype='applcation/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(json.dumps(message, cls=connector.AlchemyEncoder), status=401, mimetype='applcation/json')

@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/create_test_users', methods = ['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"


@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'


@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "Deleted User"


@app.route('/messages', methods = ['GET'])
def get_Message():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []
    for messages in dbResponse:
        data.append(messages)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/messages', methods = ['POST'])
def create_Message():
    c = json.loads(request.form['values'])
    message = entities.Message(
        content=c['content'],
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id'],
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    return 'Created Message'

@app.route('/messages', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"

@app.route('/messages', methods = ['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    messages = session.query(entities.Message).filter(entities.Message.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(messages, key, c[key])
    session.add(messages)
    session.commit()
    return 'Updated messages'


@app.route('/create_test_messages', methods = ['GET'])
def create_test_messages():
    db_session = db.getSession(engine)
    message = entities.Message(content="Another message", user_from_id="2", user_to_id="4")
    db_session.add(message)
    db_session.commit()
    return "Test message created!"

@app.route('/current', methods = ["GET"])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id == session['logged_user']
        ).first()
    return Response(json.dumps(
            user,
            cls=connector.AlchemyEncoder),
            mimetype='application/json'
        )


@app.route('/current_chat/', methods=["POST"])
def current_chat():
    db_session = db.getSession(engine)
    id_data = json.loads(request.data)
    other_user = id_data['id']
    curr_id = session['logged_user']
    messages = db_session.query(entities.Message)\
        .filter(or_((entities.Message.user_from_id == curr_id) & (entities.Message.user_to_id == other_user),
                (entities.Message.user_from_id == other_user) & (entities.Message.user_to_id == curr_id)))
    data = []
    for msg in messages:
        data.append(msg)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/send_message', methods=['POST'])
def send_message():
    msg_data = json.loads(request.data)
    curr_id = session['logged_user']
    message = entities.Message(
        content=msg_data['content'],
        user_from_id=curr_id,
        user_to_id=msg_data['user_to_id'],
    )
    de_session = db.getSession(engine)
    de_session.add(message)
    de_session.commit()
    print('ok')
    return Response(status=200)


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))