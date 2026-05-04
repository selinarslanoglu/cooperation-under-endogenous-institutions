from otree.api import *
from iban_validator import *
from settings import *

doc = """
Goodbye
"""

PPG = 4
MODE_MATCH_BONUS = 100

NORMS_CHOICES = [[1, 'Very socially inappropriate'],
                 [2, 'Somewhat socially inappropriate'],
                 [3, 'Somewhat socially appropriate'],
                 [4, 'Very socially appropriate']]
NORMS_LABEL_A = 'Given these payoffs, please rate the social appropriateness of <strong>Action A</strong> ' \
                'as either “very socially inappropriate”, “somewhat socially inappropriate”, “somewhat socially appropriate”, or “very socially appropriate”.'
NORMS_LABEL_B = 'Given these payoffs, please rate the social appropriateness of <strong>Action B</strong> ' \
                'as either “very socially inappropriate”, “somewhat socially inappropriate”, “somewhat socially appropriate”, or “very socially appropriate”.'
NORMS_FIELDS = {False: dict(payoff=60, actions=['norms_a', 'norms_b']),
                True: dict(payoff=48, actions=['norms_mod_a', 'norms_mod_b'])}


class C(BaseConstants):
    NAME_IN_URL = 'goodbye'
    PLAYERS_PER_GROUP = PPG
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


# enable this for fast-forwarding to goodbye app
# def creating_session(subsession: Subsession):
#     for pl in subsession.get_players():
#         pl.participant.modified = False


class Player(BasePlayer):
    iban1 = models.StringField(label='Please enter your International Bank Account Number (IBAN).')
    iban2 = models.StringField(label='Please re-enter your International Bank Account Number (IBAN).')
    age = models.IntegerField(label='Please enter your age.')
    gender = models.StringField(
        choices=['Male', 'Female', 'Other', 'I prefer not to say.'],
        label='Please select your gender.',
        widget=widgets.RadioSelect
    )
    inclusion = models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        label='By selecting the appropriate number, please indicate which picture best describes your connection with your group in the experiment.',
        widget=widgets.RadioSelectHorizontal
    )
    legitimacy = models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        label='To what extent do you agree with the following statement: <em>"The outcome of the vote represented my group’s preferences well."</em> <br> 1 means “strongly disagree” and 7 means “strongly agree”.',
        widget=widgets.RadioSelectHorizontal
    )
    norms_a = models.IntegerField(choices=NORMS_CHOICES, label=NORMS_LABEL_A, widget=widgets.RadioSelect)
    norms_b = models.IntegerField(choices=NORMS_CHOICES, label=NORMS_LABEL_B, widget=widgets.RadioSelect)
    norms_mod_a = models.IntegerField(choices=NORMS_CHOICES, label=NORMS_LABEL_A, widget=widgets.RadioSelect)
    norms_mod_b = models.IntegerField(choices=NORMS_CHOICES, label=NORMS_LABEL_B, widget=widgets.RadioSelect)


class FinalResults(Page):
    pass


class Survey(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'inclusion', 'legitimacy']


class InstructionsForSurveyCont(Page):
    pass


class SurveyCont(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return get_norms_fields(player)

    @staticmethod
    def vars_for_template(player: Player):
        return get_norms_payoff(player)


class PaymentInfo(Page):
    form_model = 'player'
    form_fields = ['iban1', 'iban2']

    @staticmethod
    def error_message(player, values):
        if values['iban1'] != values['iban2']:
            return 'IBANs do not match'

        iban = re.sub(r'\s+', '', values['iban1'])
        if not is_valid_iban(iban):
            return 'Invalid IBAN'

        player.participant.iban = iban


class WaitForOthers(WaitPage):

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        fields = get_norms_fields(players[0])
        a_or_b = random.getrandbits(1)
        norm_field = fields[a_or_b]
        appropriateness_ranks = [getattr(p, norm_field) for p in players]
        appropriateness_mode = pick_most_common_randomly(appropriateness_ranks)

        for p in players:
            if getattr(p, norm_field) == appropriateness_mode:
                p.payoff = MODE_MATCH_BONUS


def get_norms_fields(player):
    return NORMS_FIELDS[player.participant.modified]['actions']


def get_norms_payoff(player):
    return NORMS_FIELDS[player.participant.modified]


class GoodbyePage(Page):
    pass


class LastPart(Page):
    pass


page_sequence = [LastPart, Survey, InstructionsForSurveyCont, SurveyCont, PaymentInfo, WaitForOthers, FinalResults, GoodbyePage]
