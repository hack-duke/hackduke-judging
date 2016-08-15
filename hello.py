from flask import Flask, request, jsonify, g
from judging_sessions import SimpleSession
from redis_store import RedisStore

app = Flask(__name__)

store = RedisStore()

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
                g.curr_session = SimpleSession(num_alts)
                store.save_session(g.curr_session, g.session_name)
        except Exception as e:
            result['error'] = str(e)
        else:
            result['error'] = ''

    return jsonify(result)

@app.route('/get_decision', methods = ['POST'])
def get_decision():
    result = dict()
    json_args = request.get_json()
    if 'judge_id' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id = json_args['judge_id']
    a,b = g.curr_session.get_decision(judge_id)
    result['choice_a'] = a
    result['choice_b'] = b
    store.save_session(g.curr_session, g.session_name)
    return jsonify(result)

@app.route('/perform_decision', methods = ['POST'])
def perform_decision():
    result = dict()
    json_args = request.get_json()
    if 'judge_id' not in json_args or 'favored' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id, favored = json_args['judge_id'], json_args['favored']
    result['error'] = g.curr_session.perform_decision(judge_id, favored)
    store.save_session(g.curr_session, g.session_name)
    return jsonify(result)

@app.route('/results', methods = ['POST'])
def results():
    result = dict()
    json_args = request.get_json()
    result.update(g.curr_session.get_results())
    result['error'] = ''
    return jsonify(result)

@app.before_request
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
    g.curr_session = store.get_curr_session(g.session_name)
    if g.curr_session is None:
        result['error'] = 'Need to init first!'
        return jsonify(result)

if __name__ == "__main__":
    app.run()
