from otree.api import *

from settings import *

doc = """
PD
"""

PPG = 2



class C(BaseConstants):
    NAME_IN_URL = 'pd'
    PLAYERS_PER_GROUP = PPG
    NUM_ROUNDS = 10
    PAYOFF_MUTUAL_C = 50
    PAYOFF_MUTUAL_D = 40
    PAYOFF_TEMPTATION = 60
    PAYOFF_SUCKER = 10
    VALIDATION = dict(
        mypayoffifCC=PAYOFF_MUTUAL_C,
        partnerpayoffifDD=PAYOFF_MUTUAL_D,
        mypayoffifCD=PAYOFF_SUCKER,
        partnerpayoffifCD=PAYOFF_TEMPTATION
    )


class Group(BaseGroup):
    pass


class Subsession(BaseSubsession):
    pass


class Player(BasePlayer):
    mypayoffifCC = models.IntegerField(
        label="What will be your payoff if both you and the other participant you are matched with choose A?"
    )
    partnerpayoffifDD = models.IntegerField(
        label="What will be the other participant's payoff if both of you choose B?"
    )
    mypayoffifCD = models.IntegerField(
        label="What will be your payoff if you choose A and the other participant you are matched with chooses B?"
    )
    partnerpayoffifCD = models.IntegerField(
        label="What will be the other participant's payoff if you choose A and the other participant you are matched with chooses B?"
    )
    cooperate = models.BooleanField(
        label='Please choose Action A or Action B.',
        choices=[
            [True, 'A'],
            [False, 'B'],
        ]
    )
    terminal = models.IntegerField(
        label="Please enter the terminal number."
    )

    def is_cooperated(self):
        return 'A' if self.cooperate is True else 'B'


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for player in subsession.get_players():
            player.participant.treatment = subsession.session.config['treatment']
            player.participant.vars.setdefault('actionhistory', [])
        init_super_groups(subsession, PPG)
    my_group_randomly(subsession)


def get_partner(player: Player):
    return player.get_others_in_group()[0]


class Welcome(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    form_model = 'player'
    form_fields = ['terminal']


class SessionStart(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Part1WaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Part1Start(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        player_list = group.get_players()
        for p in player_list:
            p.participant.actionhistory.append(p.is_cooperated())

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


class Part1(Page):
    errors = []

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    form_model = 'player'
    form_fields = ['mypayoffifCC', 'partnerpayoffifDD', 'mypayoffifCD', 'partnerpayoffifCD']

    @staticmethod
    def error_message(self, values):
        Part1.errors = []
        error_messages = dict()
        for field_name in C.VALIDATION:
            if values[field_name] != C.VALIDATION[field_name]:
                Part1.errors.append(field_name)
                error_messages[field_name] = 'Wrong answer! Please read the instructions again.'

        return error_messages

    @staticmethod
    def js_vars(player):
        return dict(
            errors=Part1.errors
        )


page_sequence = [Welcome, SessionStart, Introduction, Part1, Part1WaitPage, Part1Start, Decision, ResultsWaitPage, Results]
