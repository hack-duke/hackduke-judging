import queue

CHOICE_A, CHOICE_B = 'CHOICE_A', 'CHOICE_B'

class JudgingSession():

    def __init__(self, num_alts):
        self.num_alts = num_alts

    def get_decision(self):
        raise NotImplementedError

    def perform_decision(self):
        raise NotImplementedError

    def get_results(self):
        raise NotImplementedError

class SimpleSession(JudgingSession):

    def __init__(self, num_alts):
        try:
            num_alts = int(num_alts)
        except:
            raise ValueError('Not an integer!')
        if num_alts <= 1:
            raise ValueError('Number of alternates must be greater than 1!')
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
        if favored not in [CHOICE_A, CHOICE_B]:
            return 'That is not a valid choice!'
        a, b = self.curr_judges[judge_id]
        if favored == CHOICE_A:
            self.votes[a] += 1
        else:
            self.votes[b] += 1
        self.num_times_judged[a] += 1; self.num_times_judged[b] += 1
        self.q.put((self.num_times_judged[a], a)); self.q.put((self.num_times_judged[b], b))
        self.curr_judges.pop(judge_id)
        return ''

    def get_results(self):
        return self.votes


