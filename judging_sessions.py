import queue
from redis_store import RedisStore

CHOICE_A, CHOICE_B = 'CHOICE_A', 'CHOICE_B'
CURR_JUDGES = "curr_judges"
VOTES = "votes"
NUM_TIMES_JUDGED = "num_times_judged"
JUDGE_COUNTS = "judge_counts"

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
        self.store = RedisStore()
        try:
            num_alts = int(num_alts)
        except:
            raise ValueError('Not an integer!')
        if num_alts <= 1:
            raise ValueError('Number of alternates must be greater than 1!')
        self.num_alts = num_alts
        self.q = queue.PriorityQueue()
        for i in range(num_alts):
            self.store.set_hash(VOTES, i, 0)
            self.store.set_hash(NUM_TIMES_JUDGED, i, 0)
            self.q.put((0, i))

    def get_decision(self, judge_id):
        if self.store.key_exists(CURR_JUDGES, judge_id):
            return self.store.get_tuple_hash(CURR_JUDGES, judge_id)
        a,b  = self.q.get()[1], self.q.get()[1]
        self.store.set_tuple_hash(CURR_JUDGES, judge_id, (a,b))
        if not self.store.key_exists(JUDGE_COUNTS, judge_id):
            self.store.set_hash(JUDGE_COUNTS, judge_id, 0)
        return (a,b)

    def perform_decision(self, judge_id, favored):
        if not self.store.key_exists(CURR_JUDGES, judge_id):
            return 'You are currently not judging!'
        if favored not in [CHOICE_A, CHOICE_B]:
            return 'That is not a valid choice!'
        a, b = self.store.get_tuple_hash(CURR_JUDGES, judge_id)
        if favored == CHOICE_A:
            self.store.increment_hash(VOTES, a, 1)
        else:
            self.store.increment_hash(VOTES, b, 1)
        self.store.increment_hash(NUM_TIMES_JUDGED, a, 1)
        self.store.increment_hash(NUM_TIMES_JUDGED, b, 1)
        self.q.put((self.store.get_hash(NUM_TIMES_JUDGED, a), a))
        self.q.put((self.store.get_hash(NUM_TIMES_JUDGED, b), b))
        self.store.delete_hash(CURR_JUDGES, [judge_id])
        self.store.increment_hash(JUDGE_COUNTS, judge_id, 1)
        return ''

    def get_results(self):
        return {'votes': self.store.get_all_hash(VOTES), 
                'judge_counts': self.store.get_all_hash(JUDGE_COUNTS)}


