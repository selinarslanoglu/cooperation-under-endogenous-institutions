import itertools
import random
from os import environ
from collections import Counter

PLAYERS_PER_SUPER_GROUP = 4
NUM_PARTICIPANTS = 4
SUPER_GROUPS = []

PARTICIPANT_FIELDS = ['treatment', 'actionhistory', 'modified', 'iban']
SESSION_FIELDS = []
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
DEMO_PAGE_INTRO_HTML = """ """
SECRET_KEY = '4677711907399'

SESSION_CONFIGS = [
    dict(
        name='session_voting',
        app_sequence=['pd', 'voting', 'coord', 'pd2', 'goodbye'],
        num_demo_participants=NUM_PARTICIPANTS,
        num_participants=NUM_PARTICIPANTS,
        players_per_super_group=PLAYERS_PER_SUPER_GROUP,
        treatment='voting'
    ),
    dict(
        name='session_leadership',
        app_sequence=['pd', 'leadership', 'coord', 'pd2', 'goodbye'],
        num_demo_participants=NUM_PARTICIPANTS,
        num_participants=NUM_PARTICIPANTS,
        players_per_super_group=PLAYERS_PER_SUPER_GROUP,
        treatment='leadership'
    )
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01,
    participation_fee=0.00,
    doc=""
)


def my_group_randomly(subsession):
    group_matrix = subsession.get_group_matrix()
    sizes = [len(group) for group in group_matrix]
    if sizes and any(size != sizes[0] for size in sizes):
        raise ValueError('This algorithm does not work with unevenly sized groups')
    ppg = sizes[0]

    for sg in SUPER_GROUPS:
        random.shuffle(sg)

    shuffled_pls = list(itertools.chain.from_iterable(SUPER_GROUPS))

    group_matrix = []
    for i in range(0, len(shuffled_pls), ppg):
        group_matrix.append(shuffled_pls[i: i + ppg])

    subsession.set_group_matrix(group_matrix)


def init_super_groups(subsession, ppg):
    global SUPER_GROUPS
    SUPER_GROUPS.clear()
    group_matrix = subsession.get_group_matrix()
    num_groups = int(subsession.session.num_participants / ppg)
    num_groups_in_super_group = int(PLAYERS_PER_SUPER_GROUP / ppg)

    for k in range(0, num_groups, ppg):
        super_group = []
        for j in range(k, k + num_groups_in_super_group):
            super_group = super_group + group_matrix[j]
        SUPER_GROUPS.append(super_group)


def get_super_group_by_participant_id(participant_id):
    for sg in SUPER_GROUPS:
        for p in sg:
            if participant_id == p:
                sg.sort()
                return sg
    return []


def action_history(player):
    print("player_id: " + str(player.id) + "id_in_session: " + str(player.participant.id_in_session))
    sgp = get_super_group_by_participant_id(player.participant.id_in_session)
    participant_dict = {p.id_in_session: p for p in player.group.subsession.session.get_participants()}
    round_size = len(player.participant.actionhistory)
    group_size = len(sgp)

    rows, cols = (round_size + 3, group_size + 1)
    act_hist = [[0 for _ in range(cols)] for _ in range(rows)]

    perc_a = [0 for _ in range(cols)]
    perc_b = [0 for _ in range(cols)]
    perc_a[0] = "Percentage of A"
    perc_b[0] = "Percentage of B"
    for i in range(0, group_size):
            ahist = participant_dict[sgp[i]].actionhistory
            size = len(ahist)
            perc_a[i+1] = '{:.2f}%'.format((ahist.count('A') / size) * 100)
            perc_b[i+1] = '{:.2f}%'.format((ahist.count('B') / size) * 100)

    for i in range(0, rows-2):
        for j in range(0, cols):
            if i == 0:
                if j == 0:
                    act_hist[i][j] = "Round"
                else:
                    act_hist[i][j] = 'Participant ' + str(sgp[j - 1])
            else:
                if j == 0:
                    act_hist[i][j] = str(i)
                else:
                    act_hist[i][j] = participant_dict[sgp[j - 1]].actionhistory[i - 1]

    act_hist[rows-2] = perc_a
    act_hist[rows-1] = perc_b

    return dict(ah=act_hist, header=act_hist[0])


def pick_most_common_randomly(lst):
    mc = Counter(lst).most_common()
    for i in range(len(mc)-1):
        if mc[i][1] != mc[i+1][1]:
            return random.choice(mc[:i+1])[0]
    return random.choice(mc)[0]
