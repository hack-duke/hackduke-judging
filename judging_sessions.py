import operator, sys
sys.path.append('gavel/gavel')
import crowd_bt
from random import shuffle

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
        self.curr_judges, self.votes, self.num_times_judged, self.judge_counts = {}, {}, {}, {}
        for i in range(num_alts):
            self.votes[i] = 0
            self.num_times_judged[i] = 0

    def get_decision(self, judge_id):
        if judge_id in self.curr_judges:
            self.judge_counts[judge_id] += 1
            return self.curr_judges[judge_id]
        sorted_x = sorted(self.num_times_judged.items(), key=operator.itemgetter(1), reverse=True)
        a,b  = sorted_x[0][0], sorted_x[1][0]
        self.curr_judges[judge_id] = (a, b)
        if judge_id not in self.judge_counts:
            self.judge_counts[judge_id] = 0
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
        self.curr_judges.pop(judge_id)
        self.judge_counts[judge_id] += 1
        return ''

    def get_results(self):
        ranking = sorted(self.votes, key=lambda x: -self.votes[x])
        return {
                'ranking': ranking,
                'votes': self.votes,
                'judge_counts': self.judge_counts,
                'num_times_judged': self.num_times_judged,
                'curr_judges': self.curr_judges
                }

class CrowdBTSession(JudgingSession):
    def __init__(self, num_alts):
        try:
            num_alts = int(num_alts)
        except:
            raise ValueError('Not an integer!')
        if num_alts <= 1:
            raise ValueError('Number of alternates must be greater than 1!')

        self.judges, self.alts, self.num_judges, self.num_alts = {}, {}, 0, 0
        self.update_alts(list(range(num_alts)))

    def update_judges(self, judge_list):
        for judge_name in judge_list:
            if judge_name not in self.judges:
                self.judges[judge_name] = {
                        'alpha' : crowd_bt.ALPHA_PRIOR,
                        'beta' : crowd_bt.BETA_PRIOR,
                        'next_alt' : None,
                        'prev_alt' : None,
                        'num_times_voted' : 0,
                        'ignored_alt_ids' : []
                        }
                self.num_judges += 1

    def update_alts(self, alts_list):
        for alt in alts_list:
            if alt not in self.alts:
                self.alts[alt] = {
                        'mu' : crowd_bt.MU_PRIOR,
                        'sigma_sq' : crowd_bt.SIGMA_SQ_PRIOR,
                        'num_times_judged' : 0
                        }
                self.num_alts += 1

    def get_next_alt(self, judge_id):
        judge = self.judges[judge_id]
        # If it's never judged anything before, just pick the least viewed:
        if judge['prev_alt'] is None:
            alt_ids = list(self.alts.keys()); shuffle(alt_ids)
            alt_ids = sorted(alt_ids,
                    key=lambda alt_id: self.alts[alt_id]['num_times_judged'])
            curr_alt = alt_ids[0]

        # If we already have a prev, grab a new one that's never seen before
        else:
            alt_ids = [i for i in self.alts.keys() if i not in judge['ignored_alt_ids']]
            if not alt_ids: # You already judged every alternative, so reset the ignored IDs
                judge['ignored_alt_ids'] = []
                alt_ids = self.alts.keys()

            shuffle(alt_ids)
            curr_alt = crowd_bt.argmax(lambda alt_id: \
                        crowd_bt.expected_information_gain(
                        judge['alpha'], judge['beta'],
                        self.alts[judge['prev_alt']]['mu'],
                        self.alts[judge['prev_alt']]['sigma_sq'],
                        self.alts[alt_id]['mu'], self.alts[alt_id]['sigma_sq']
                    ), alt_ids)

        judge['ignored_alt_ids'].append(curr_alt)
        return curr_alt

    def get_decision(self, judge_id):
        if judge_id not in self.judges:
            self.update_judges([judge_id])
        judge = self.judges[judge_id]
        if judge['prev_alt'] is None:
            judge['prev_alt'] = self.get_next_alt(judge_id)
        if judge['next_alt'] is None:
            judge['next_alt'] = self.get_next_alt(judge_id)
        return judge['prev_alt'], judge['next_alt']

    def perform_decision(self, judge_id, favored):
        if judge_id not in self.judges:
            return 'You are not a judge!'
        judge = self.judges[judge_id]
        if judge['prev_alt'] is None or judge['next_alt'] is None:
            return 'You are currently not judging!'
        if favored not in [CHOICE_A, CHOICE_B]:
            return 'That is not a valid choice!'
        a, b = judge['prev_alt'], judge['next_alt']
        if favored == CHOICE_A:
            winner, loser = self.alts[a], self.alts[b]
        else:
            winner, loser = self.alts[b], self.alts[a]
        u_alpha, u_beta, u_winner_mu, u_winner_sigma_sq, u_loser_mu, u_loser_sigma_sq = crowd_bt.update(
            judge['alpha'],
            judge['beta'],
            winner['mu'],
            winner['sigma_sq'],
            loser['mu'],
            loser['sigma_sq']
        )
        judge['alpha'], judge['beta'] = u_alpha, u_beta
        winner['mu'], winner['sigma_sq'] = u_winner_mu, u_winner_sigma_sq
        loser['mu'], loser['sigma_sq'] = u_loser_mu, u_loser_sigma_sq
        judge['prev_alt'], judge['next_alt'] = judge['next_alt'], None
        judge['num_times_voted'] += 1
        winner['num_times_judged'] += 1; loser['num_times_judged'] += 1
        return ''

    def get_results(self):
        ranking = sorted(self.alts.keys(), key=\
                lambda alt_id: -self.alts[alt_id]['mu'])
        votes = [self.alts[alt]['mu'] for alt in self.alts]
        judge_counts = [{judge: self.judges[judge]['num_times_voted']} for judge in self.judges]
        num_times_judged = [self.alts[alt]['num_times_judged'] for alt in self.alts]
        curr_judges = [judge_id for judge_id in self.judges\
                if self.judges[judge_id]['next_alt'] is not None]
        return {
                'ranking': ranking,
                'votes': votes,
                'judge_counts': judge_counts,
                'num_times_judged': num_times_judged,
                'curr_judges': curr_judges
                }


