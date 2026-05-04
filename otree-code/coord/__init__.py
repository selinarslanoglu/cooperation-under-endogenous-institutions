from otree.api import *

from settings import *

doc = """
Coordination
"""

PPG = 2


class C(BaseConstants):
    NAME_IN_URL = 'coord'
    PLAYERS_PER_GROUP = PPG
    NUM_ROUNDS = 10
    PAYOFF_MUTUAL_C = 50
    PAYOFF_MUTUAL_D = 40
    PAYOFF_TEMPTATION = 48
    PAYOFF_SUCKER = 10


class Group(BaseGroup):
    pass


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    my_group_randomly(subsession)


class Player(BasePlayer):
    cooperate = models.BooleanField(
        label="Please choose Action A or Action B.",
        choices=[
            [True, "A"],
            [False, "B"],
        ]
    )

    def is_cooperated(self):
        return 'A' if self.cooperate is True else 'B'


def get_partner(player: Player):
    return player.get_others_in_group()[0]


class Part2(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Decision(Page):
    form_model = "player"
    form_fields = ["cooperate"]


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        player_list = group.get_players()
        player_1 = player_list[0]
        player_2 = player_list[1]
        if player_1.cooperate:
            if player_2.cooperate:
                player_1.payoff = C.PAYOFF_MUTUAL_C
                player_2.payoff = C.PAYOFF_MUTUAL_C
            else:
                player_1.payoff = C.PAYOFF_SUCKER
                player_2.payoff = C.PAYOFF_TEMPTATION
        else:
            if player_2.cooperate:
                player_1.payoff = C.PAYOFF_TEMPTATION
                player_2.payoff = C.PAYOFF_SUCKER
            else:
                player_1.payoff = C.PAYOFF_MUTUAL_D
                player_2.payoff = C.PAYOFF_MUTUAL_D


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(partner=get_partner(player))

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.round_number == C.NUM_ROUNDS:
            return "goodbye"


page_sequence = [Part2, Decision, ResultsWaitPage, Results]
