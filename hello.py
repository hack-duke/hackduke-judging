from flask import Flask, request, jsonify
app = Flask(__name__)

########

@app.route("/")
def hello():
    return "Hello World!"

curr_session = None

########

import queue

class JudgingAlgo():
    def __init__(self, num_alts):
        self.num_alts = num_alts
    def get_decision(self):
        raise NotImplementedError
    def perform_decision(self):
        raise NotImplementedError
    def get_results(self):
        raise NotImplementedError

class SimpleAlgo(JudgingAlgo):
    def __init__(self, num_alts):
        self.num_alts = num_alts
        self.curr_judges, self.votes, self.num_times_judged = {}, {}, {}
        self.q = queue.PriorityQueue()
        for i in range(num_alts):
            self.votes[i] = 0
            self.num_times_judged[i] = 0
            self.q.put((0, i))
    def get_decision(self, judge_id):
        if judge_id in self.curr_judges:
            return self.curr_judges[judge_id]
        a,b  = self.q.get()[1], self.q.get()[1]
        self.curr_judges[judge_id] = (a, b)
        return (a,b)
    def perform_decision(self, judge_id, favored):
        if judge_id not in self.curr_judges:
            return 'You are currently not judging!'
        if favored not in self.curr_judges[judge_id]:
            return 'That is not a valid choice!'
        a, b = self.curr_judges[judge_id]
        self.votes[favored] += 1
        self.q.put((self.votes[a], a))
        self.q.put((self.votes[b], b))
        self.curr_judges.pop(judge_id)
        return ''
    def get_results(self):
        return self.votes

########

curr_session = None

@app.route("/init", methods = ['POST'])
def init_judge_session():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return result
    json_args = request.get_json()

    if 'num_alts' not in json_args:
        result['error'] = 'Not enough args'
    else:
        num_alts = json_args['num_alts']
        try:
            num_alts = int(num_alts)
        except ValueError:
            result['error'] = 'Not an integer num_alts'
            return jsonify(result)
        if num_alts <= 0:
            result['error'] = 'Not a positive num_alts'
            return jsonify(result)
        global curr_session
        curr_session = SimpleAlgo(num_alts)
        result['error'] = ''
    return jsonify(result)

@app.route('/get_decision', methods = ['POST'])
def get_decision():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return result
    json_args = request.get_json()
    if curr_session is None:
        result['error'] = 'Need to init first!'
        return jsonify(result)
    if 'judge_id' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id = json_args['judge_id']
    a,b = curr_session.get_decision(judge_id)
    result['choice_a'] = a
    result['choice_b'] = b
    return jsonify(result)

@app.route('/perform_decision', methods = ['POST'])
def perform_decision():
    result = dict()
    if not request.is_json:
        result['error'] = 'Not JSON input'
        return result
    json_args = request.get_json()

    if curr_session is None:
        result['error'] = 'Need to init first!'
        return jsonify(result)
    if 'judge_id' not in json_args or 'favored' not in json_args:
        result['error'] = 'Not enough args'
        return jsonify(result)
    judge_id, favored = json_args['judge_id'], json_args['favored']
    try:
        favored = int(favored)
    except ValueError:
        result['error'] = 'Not a valid choice!'
        return jsonify(result)
    result['error'] = curr_session.perform_decision(judge_id, favored)
    return jsonify(result)

@app.route('/results')
def results():
    result = dict()
    if curr_session is None:
        result['error'] = 'Need to init first!'
    result['votes'] = curr_session.get_results()
    result['error'] = ''
    return jsonify(result)

if __name__ == "__main__":
    app.run()

