from otree.api import *
from settings import *

doc = """
Leadership
"""

PPG = 4


class C(BaseConstants):
    NAME_IN_URL = 'leadership'
    PLAYERS_PER_GROUP = PPG
    NUM_ROUNDS = 1
    VALIDATION = dict(
        groupvotes=True,
        computeroverrules=False,
        outcomewhenoverruled=True,
        outcomewhenconsidered=True,
        outcomewhentied=False,
        mypayoffifCCmod=50,
        partnerpayoffifDDmod=40,
        mypayoffifCDmod=10,
        partnerpayoffifCDmod=48
    )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    leader_elected = models.StringField()
    is_leader_decision_considered = models.BooleanField()
    is_game_modified = models.BooleanField()

    def leader(self):
        return self.leader_elected

    def game_modified(self):
        return "Yes" if self.is_game_modified else "No"

    def leader_decision_considered(self):
        return "Yes" if self.is_leader_decision_considered else "No"


class Player(BasePlayer):
    groupvotes = models.BooleanField(
        label="Each group member will vote for another group member to elect a group representative.",
        choices=[True, False]
    )
    computeroverrules = models.BooleanField(
        label="The computer will overrule the representative's decision for sure.",
        choices=[True, False]
    )
    outcomewhenoverruled = models.BooleanField(
        label="If the computer overrules the representative's decision, it will randomly decide whether or not to modify the payoffs.",
        choices=[True, False]
    )
    outcomewhenconsidered = models.BooleanField(
        label="If the votes are considered, then the decision of the representative will be applied.",
        choices=[True, False]
    )
    outcomewhentied = models.BooleanField(
        label="In case of a tie, there will be no representative.",
        choices=[True, False]
    )
    mypayoffifCCmod = models.IntegerField(
        label="What will be your payoff if both you and the other participant you are matched with choose A under the modified payoffs?"
    )
    partnerpayoffifDDmod = models.IntegerField(
        label="What will be the other participant's payoff if both of you choose B under the modified payoffs?"
    )
    mypayoffifCDmod = models.IntegerField(
        label="What will be your payoff if you choose A and the other participant you are matched with chooses B under the modified payoffs?"
    )
    partnerpayoffifCDmod = models.IntegerField(
        label="What will be the other participant's payoff if you choose A and the other participant you are matched with chooses B under the modified payoffs?"
    )

    preference_for_coord = models.BooleanField(
        label="Would you modify the payoffs if you were elected as the representative?",
        choices=[
            [True, "Yes"],
            [False, "No"],
        ]
    )

    vote_for_leader = models.StringField(
        label="Which group member do you want to name to be elected as the representative? (You are not alllowed to vote for yourself.)",
        widget=widgets.RadioSelect
    )


def vote_for_leader_choices(player):
    others = ['P{}'.format(pls.participant.id_in_session) for pls in player.get_others_in_group()]
    others.sort()
    return others


def creating_session(subsession: Subsession):
    my_group_randomly(subsession)


def evaluate_votes_for_leader(group: Group):
    players = group.get_players()
    votes_for_leader = [p.vote_for_leader for p in players]
    group.leader_elected = pick_most_common_randomly(votes_for_leader)

    participant_dict = {p.id_in_session: p for p in group.subsession.session.get_participants()}
    leader_as_participant = participant_dict[int(group.leader_elected[1:])]

    group.is_game_modified = leader_as_participant._get_current_player().preference_for_coord
    group.is_leader_decision_considered = True
    if random_dec():
        group.is_leader_decision_considered = False
        group.is_game_modified = random_dec()

    for p in players:
        p.participant.modified = group.is_game_modified


def random_dec():
    return bool(random.getrandbits(1))


class WaitForOthers(WaitPage):
    wait_for_all_groups = True


class VotePage(Page):
    form_model = "player"
    form_fields = ["preference_for_coord", "vote_for_leader"]

    @staticmethod
    def vars_for_template(player: Player):
        return action_history(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = evaluate_votes_for_leader


class Results(Page):
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return "coord" if player.group.is_game_modified else "pd2"


class Part2(Page):
    errors = []

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    form_model = "player"
    form_fields = ["groupvotes", "computeroverrules", "outcomewhenoverruled", "outcomewhenconsidered",
                   "outcomewhentied", "mypayoffifCCmod", "partnerpayoffifDDmod", "mypayoffifCDmod",
                   "partnerpayoffifCDmod"]

    @staticmethod
    def error_message(self, values):
        Part2.errors = []
        error_messages = dict()
        for field_name in C.VALIDATION:
            if values[field_name] != C.VALIDATION[field_name]:
                Part2.errors.append(field_name)
                error_messages[field_name] = 'Wrong answer! Please read the instructions again.'

        return error_messages

    @staticmethod
    def js_vars(player):
        return dict(
            errors=Part2.errors
        )


class Part2WaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


page_sequence = [WaitForOthers, Part2, Part2WaitPage, VotePage, ResultsWaitPage, Results]
