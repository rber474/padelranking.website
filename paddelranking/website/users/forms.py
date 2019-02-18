from flask_babel import _, lazy_gettext as _l
from flask_login import current_user
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, FieldList, FormField
from wtforms.fields.html5 import IntegerField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from sqlalchemy.sql.expression import not_

from paddelranking.website import portraits
from paddelranking.website.models import User, db, Tournament, Player, MatchResultsByTeam, Match

from wtforms_alchemy import ModelForm as SQLModelForm, ModelFormField, model_form_factory, ModelFieldList

BaseModelForm = model_form_factory(FlaskForm)



class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class EditProfileForm(FlaskForm):
    """ Edit user personal data """

    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    name = StringField(_l('Name'), validators=[DataRequired()])
    surname1 = StringField(_l('Surname 1'), validators=[DataRequired()])
    surname2 = StringField(_l('Surname 2'), validators=[])
    portrait = FileField(_l('Portrait'),
        description=_l("Upload an image file up to 16 MB, better if 300x300 (squared)"),
        validators=[
            FileAllowed(portraits, _l('Images only!'))])

    submit = SubmitField(_l('Save'))
    cancel = SubmitField(_l('Cancel'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user.id != current_user.id:
            raise ValidationError(_l('Please use a different email address.'))


class PlayersForm(ModelForm):
    """ Create a list of players """

    playername = StringField(_l('Player Nick'),
            description=_l("Please, provide a nick lower than 64 characters."),
            validators=[Length(max=64)])

    class Meta:
        # No need for csrf token in this child form
        csrf = False
        model = Player

def possible_players():
    return Player.query.filter_by(createdby=current_user.id)

class BaseTournamentForm(ModelForm):
    class Meta:
        model = Tournament

    submit = SubmitField(_l('Save'))
    cancel = SubmitField(_l('Cancel'))

    name = StringField(_l('Tournament Title'),validators=[DataRequired()])
    point_per_match = IntegerField(_l('Points per match'), validators=[DataRequired()], default=100)
    match_per_round = IntegerField(_l('Matches per round'), validators=[DataRequired()], default=3)
    rounds_qty = IntegerField(_l('Rounds'), validators=[DataRequired()], default=3)
    players = QuerySelectMultipleField(_l('Select the players...'),query_factory=possible_players, get_label='playername')
    players_input = ModelFieldList(FormField(PlayersForm), label=_l("Player"), min_entries=1)
    add_player = SubmitField(_l('Add Player'))


class MatchPointsForm(ModelForm):
    """ Create a list of players """

    set1 = IntegerField(_l('Set 1'))
    set2 = IntegerField(_l('Set 2'))
    set3 = IntegerField(_l('Set 3'))


    class Meta:
        # No need for csrf token in this child form
        csrf = False
        model = MatchResultsByTeam

        all_fields_optional = True
        assign_required = False
        exclude = ['winner', 'score', '_matchpoints', 'gamepoints']
        include_foreign_keys = False



class MatchForm(ModelForm):

    class Meta:
        model = Match
        all_fields_optional = True
        assign_required = False

    matchdate = DateField(_l('Match Date'))
    results = ModelFieldList(FormField(MatchPointsForm), label=_l("Match Score"), min_entries=2, max_entries=2)

    submit = SubmitField(_l('Save'))
    cancel = SubmitField(_l('Cancel'))