from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList, FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from sqlalchemy.sql.expression import not_

from paddelranking.website import portraits
from paddelranking.website.models import User, db, Tournament, Player

from wtforms_alchemy import ModelForm, ModelFormField, model_form_factory, ModelFieldList

BaseModelForm = model_form_factory(FlaskForm)



class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class EditProfileForm(FlaskForm):
    """ Edit user personal data """

    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    surname1 = StringField('Surname 1', validators=[DataRequired()])
    surname2 = StringField('Surname 2', validators=[])
    portrait = FileField('Portrait',
        description="Upload an image file up to 16 MB, better if 300x300 (squared)",
        validators=[
            FileAllowed(portraits, 'Images only!')])

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user.id != current_user.id:
            raise ValidationError('Please use a different email address.')


class PlayersForm(ModelForm):
    """ Create a list of players """

    playername = StringField('Player Nick',
            description="Please, provide a nick lower than 64 characters.",
            validators=[Length(max=64)])

    class Meta:
        # No need for csrf token in this child form
        csrf = False
        model = Player

def possible_players():
    return Player.query.filter_by(createdby=current_user.id)


class TournamentForm(ModelForm):
    """ Create or edit tournament"""


    name = StringField('Tournament Title',validators=[DataRequired()])
    point_per_match = IntegerField('Points per match', validators=[DataRequired()], default=100)
    match_per_round = IntegerField('Matchs per round', validators=[DataRequired()], default=3)
    rounds_qty = IntegerField('Rounds', validators=[DataRequired()], default=3)

    player_list = QuerySelectMultipleField('Select the players...',query_factory=possible_players, get_label='playername')

    players = ModelFieldList(FormField(PlayersForm), label="Player", min_entries=1)
    add_player = SubmitField('Add Player')

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

    class Meta:
        model = Tournament

class BaseTournamentForm(ModelForm):
    class Meta:
        model = Tournament

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

    name = StringField('Tournament Title',validators=[DataRequired()])
    players = QuerySelectMultipleField('Select the players...',query_factory=possible_players, get_label='playername')
    players_input = ModelFieldList(FormField(PlayersForm), label="Player", min_entries=1)
    add_player = SubmitField('Add Player')