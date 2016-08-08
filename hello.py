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
        self.curr_judges = dict()
        self.votes = dict()
        self.q = queue.PriorityQueue()
        for i in range(num_alts):
            self.votes[i] = 0
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
        return 'Successfully voted'
    def get_results(self):
        return self.votes

########
curr_session = None

@app.route("/init", methods = ['GET'])
def init_judge_session():
    if 'num_alts' in request.args:
        num_alts = request.args['num_alts']
        try:
            num_alts = int(num_alts)
        except ValueError:
            return 'Not an integer num_alts'
        if num_alts <= 0:
            return 'Not a positive num_alts'
        global curr_session
        curr_session = SimpleAlgo(num_alts)
        return 'Success'
    return 'Not enough args'

@app.route('/get_decision', methods = ['GET'])
def get_decision():
    if curr_session is None:
        return 'Need to init first!'
    if 'judge_id' not in request.args:
        return 'Not enough args'
    judge_id = request.args['judge_id']
    a,b = curr_session.get_decision(judge_id)
    return jsonify({'a': a, 'b': b})

@app.route('/perform_decision', methods = ['GET'])
def perform_decision():
    if curr_session is None:
        return 'Need to init first!'
    if 'judge_id' not in request.args or 'favored' not in request.args:
        return 'Not enough args'
    judge_id, favored = request.args['judge_id'], request.args['favored']
    try:
        favored = int(favored)
    except ValueError:
        return 'Not a valid choice!'
    return curr_session.perform_decision(judge_id, favored)

@app.route('/results')
def results():
    if curr_session is None:
        return 'Need to init first!'
    return jsonify(curr_session.get_results())

if __name__ == "__main__":
    app.run()

