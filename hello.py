from flask import Flask, request, jsonify, g
from judging_sessions import CrowdBTSession
from redis_store import RedisStore
import os

app = Flask(__name__)
app.config.from_object('default_settings')
app.config.from_object('curr_settings')

redis_retry_limit = 3
store = RedisStore()

######## Authentication
# Taken and modified from http://flask.pocoo.org/snippets/8/

from functools import wraps
from flask import Response

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['USER'] and password == app.config['PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

######## App

redis_retry_limit = 3
store = RedisStore()

######## Authentication
# Taken and modified from http://flask.pocoo.org/snippets/8/

from functools import wraps
from flask import Response

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == os.getenv('USER') and password == os.getenv('PASSWORD')

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

######## App

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/init", methods = ['POST'])
def init_judge_session():
    result = dict()
    json_args = request.get_json()
    if 'num_alts' not in json_args:
        result['error'] = 'Not enough args'
    else:
        num_alts = json_args['num_alts']
        try:
            if g.curr_session is None:
                g.curr_session = CrowdBTSession(num_alts)
                store.save_session(g.curr_session, g.session_name)
        except Exception as e:
            result['error'] = str(e)
        else:
            result['error'] = ''
    return jsonify(result)

@app.route('/get_decision', methods = ['POST'])
def get_decision(num=0):
    success = dict()
    error = dict()
    json_args = request.get_json()
    if 'num_alts' not in json_args:
        result['error'] = 'Need num alts'
        return jsonify(result)
    else:
        g.curr_session.update_alts(list(range(json_args['num_alts'])))
    if 'judge_id' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id = json_args['judge_id']
    a,b = g.curr_session.get_decision(judge_id)
    success['choice_a'] = a
    success['choice_b'] = b
    error['error'] = 'Server overloaded, try again later'
    return save_session(success, error, get_decision, num)

@app.route('/perform_decision', methods = ['POST'])
def perform_decision(num=0):
    result = dict()
    json_args = request.get_json()
    if 'judge_id' not in json_args or 'favored' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id, favored = json_args['judge_id'], json_args['favored']
    result['error'] = g.curr_session.perform_decision(judge_id, favored)
    return save_session(result, result, perform_decision, num)

@app.route('/perform_overwrite_decision', methods = ['POST'])
def perform_overwrite_decision(num=0):
    result = dict()
    json_args = request.get_json()
    if 'judge_id' not in json_args\
            or 'winner_id' not in json_args\
            or 'loser_id' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id, winner_id, loser_id = json_args['judge_id'], json_args['winner_id'], json_args['loser_id']
    result['error'] = g.curr_session.perform_decision(judge_id, favored)
    return save_session(result, result, perform_overwrite_decision, num)

@app.route('/results', methods = ['POST'])
def results():
    result = dict()
    json_args = request.get_json()
    if 'num_alts' not in json_args:
        result['error'] = 'Need num alts'
        return jsonify(result)
    else:
        g.curr_session.update_alts(list(range(json_args['num_alts'])))
    result.update(g.curr_session.get_results())
    result['error'] = ''
    return jsonify(result)

@app.before_request
@requires_auth
def before_request():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return jsonify(result)
    json_args = request.get_json()
    if 'session_name' not in json_args:
        result['error'] = 'Need session name'
        return jsonify(result)
    g.session_name = json_args['session_name']
    update_session()
    if g.curr_session is None and not request.path == '/init':
        result['error'] = 'Need to init first!'
        return jsonify(result)

def update_session():
    g.curr_session = store.get_curr_session(g.session_name)

def save_session(success, error, route, num):
    if store.save_session(g.curr_session, g.session_name) is None:
        if num > redis_retry_limit:
            return jsonify(error)
        update_session()
        return route(num+1)
    else:
        return jsonify(success)

if __name__ == "__main__":
    app.run()
