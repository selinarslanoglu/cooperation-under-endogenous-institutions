import random

from otree.api import *

from settings import *

doc = """
Voting
"""

PPG = 4


class C(BaseConstants):
    NAME_IN_URL = 'voting'
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
    votes_for_coord = models.IntegerField()
    is_game_modified = models.BooleanField()
    is_votes_considered = models.BooleanField()

    def game_modified(self):
        return "Yes" if self.is_game_modified else "No"

    def votes_considered(self):
        return "Yes" if self.is_votes_considered else "No"


class Player(BasePlayer):
    groupvotes = models.BooleanField(
        label="First, all group members will vote to modify the payoffs or not.",
        choices=[True, False]
    )
    computeroverrules = models.BooleanField(
        label="The computer will overrule the rules for sure.",
        choices=[True, False]
    )
    outcomewhenoverruled = models.BooleanField(
        label="If the computer overrules the votes, it will randomly decide whether or not to modify the payoffs.",
        choices=[True, False]
    )
    outcomewhenconsidered = models.BooleanField(
        label="If the votes are considered, then the majority wins.",
        choices=[True, False]
    )
    outcomewhentied = models.BooleanField(
        label="In case of a tie, the payoffs will be modified.",
        choices=[True, False]
    )
    mypayoffifCCmod = models.IntegerField(
        label="What will be your payoff if both you and the other participant you are matched with choose A under the modified payoffs?",
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
    vote_for_coord = models.BooleanField(
        label="Do you want to modify the payoffs?",
        choices=[
            [True, "Yes"],
            [False, "No"],
        ]
    )


def creating_session(subsession: Subsession):
    my_group_randomly(subsession)


def evaluate_votes(group: Group):
    players = group.get_players()
    votes_for_coord = [p.vote_for_coord for p in players]
    group.votes_for_coord = votes_for_coord.count(True)

    if group.votes_for_coord == PPG / 2:
        group.is_game_modified = random_dec()
    else:
        group.is_game_modified = group.votes_for_coord > PPG / 2

    group.is_votes_considered = True
    if random_dec():
        group.is_votes_considered = False
        group.is_game_modified = random_dec()

    for p in players:
        p.participant.modified = group.is_game_modified


def random_dec():
    return bool(random.getrandbits(1))


class WaitForOthers(WaitPage):
    wait_for_all_groups = True


class VotePage(Page):
    form_model = "player"
    form_fields = ["vote_for_coord"]

    @staticmethod
    def vars_for_template(player: Player):
        return action_history(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = evaluate_votes


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
                   "outcomewhentied", "mypayoffifCCmod", "partnerpayoffifDDmod", "mypayoffifCDmod", "partnerpayoffifCDmod"]

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
