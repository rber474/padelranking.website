from datetime import datetime
from hashlib import md5
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, UserMixin
login_manager = LoginManager()


migrate = Migrate()
db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(120), index=False, unique=False)
    surname1 = db.Column(db.String(120), index=False, unique=False)
    surname2 = db.Column(db.String(120), index=False, unique=False)
    players = db.relationship('Player', backref='aliases', lazy='dynamic', foreign_keys='Player.userid')
    players_created = db.relationship('Player', backref='owner', lazy='dynamic', foreign_keys='Player.createdby')
    tournaments = db.relationship('Tournament', backref='userid', lazy='dynamic', foreign_keys='Tournament.createdby')

    last_login = db.Column(db.DateTime, index=False)
    register_date = db.Column(db.DateTime, index=False)
    last_modified = db.Column(db.DateTime, index=False,
            default=datetime.utcnow)
    filename = db.Column(db.String(120), index=False, unique=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def fullname(self):
        nombre = self.name or None
        ape1 = self.surname1 or ''
        ape2 = self.surname2 or ''
        if not nombre:
            return self.username
        return '{} {} {}'.format(nombre, ape1, ape2)

    def portrait_hash(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return digest

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playername = db.Column(db.String(64), index=True, unique=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdby = db.Column(db.Integer, db.ForeignKey('user.id'))

    teams = db.relationship('Team', primaryjoin="or_(Player.id==Team.player1, Player.id==Team.player2)", lazy='dynamic')


    points = db.relationship("MatchResultsByTeam",
                   secondary=
                   "join(Team, MatchResultsByTeam, or_(Team.id==MatchResultsByTeam.team,Team.id==MatchResultsByTeam.team))."
                   "join(Match, or_(Match.team1==MatchResultsByTeam.team,Match.team2==MatchResultsByTeam.team))",

                   primaryjoin="or_(Team.player1==Player.id, Team.player2==Player.id)",
                   secondaryjoin="or_(MatchResultsByTeam.team==Team.id, MatchResultsByTeam.team==Team.id)",
                   uselist=True,
                   viewonly=True)

    @hybrid_property
    def total_score(self):
        return sum(matchresult.matchpoints for matchresult in self.points)

    @hybrid_property
    def points_score(self):
        return sum(matchresult.gamepoints for matchresult in self.points)

    @hybrid_property
    def matches_played(self):
        return len(self.points)

    @hybrid_property
    def matches_won(self):
        return len([matchresult for matchresult in self.points if matchresult.winner==1])

    @hybrid_property
    def matches_lost(self):
        return len([matchresult for matchresult in self.points if matchresult.winner==0])



    def __repr__(self):
        return '<Player {} from user {}>'.format(self.playername, self.userid) 

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.Integer, db.ForeignKey('player.id'))
    player2 = db.Column(db.Integer, db.ForeignKey('player.id'))

    matches = db.relationship('Match', primaryjoin="or_(Team.id==Match.team1, Team.id==Match.team2)", lazy='dynamic')

    def __repr__(self):
        return '<Team {} - Player 1: {} - Player 2: {}>'.format(self.id,
                                                                self.player1,
                                                                self.player2)



PlayersByTournament = db.Table('PlayersByTournament',
    db.Column('tournament_id',db.Integer, db.ForeignKey('tournament.id'), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'),
        primary_key=True)
    )

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=False)
    point_per_match = db.Column(db.Integer, default=100)
    match_per_round = db.Column(db.Integer, default=3)
    rounds_qty = db.Column(db.Integer, default=3)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    closed = db.Column(db.Boolean)
    createdby = db.Column(db.Integer, db.ForeignKey('user.id'))
    matches = db.relationship('Match', backref='tournament', lazy=True)
    rounds = db.relationship('Round', backref='tournament', lazy=True)
    players = db.relationship('Player', secondary=PlayersByTournament,
                    primaryjoin=(PlayersByTournament.c.tournament_id == id),
                    lazy='dynamic',
                    backref=db.backref('tournaments', lazy='dynamic'))

    def __repr__(self):
        return '<Tournament {}>'.format(self.id)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour = db.Column(db.Integer, db.ForeignKey('tournament.id'),
        )
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    matches = db.relationship('Match', backref='round',
        lazy='dynamic')
    def __repr__(self):
        return '<Round {} for Tournament {}>'.format(self.id, self.tour)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matchdate = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tour = db.Column(db.Integer, db.ForeignKey('tournament.id'), index=True)
    team1 = db.Column(db.Integer, db.ForeignKey('team.id'), index=True)
    team2 = db.Column(db.Integer, db.ForeignKey('team.id'), index=True)
    roundid = db.Column(db.Integer, db.ForeignKey('round.id'))
    doubles = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer)
    played = db.Column(db.Boolean, default=False)
    results = db.relationship('MatchResultsByTeam', backref='match',
        lazy='dynamic')

    points = db.relationship('MatchResultsByTeam', 
        primaryjoin="Match.id==MatchResultsByTeam.match_id",
        secondary="match_results_by_team",
        secondaryjoin="or_(match_results_by_team.c.team==Match.team1, match_results_by_team.c.team==Match.team2)", 
        backref="matches", 
        lazy='dynamic')



    def __repr__(self):
        return '<Match {}, Date {}, Team1 {}, Team2 {}, Tour {}>'.format(
                                                        self.id,
                                                        self.matchdate,
                                                        self.team1,
                                                        self.team2,
                                                        self.tour)

class MatchResultsByTeam(db.Model):
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'),primary_key=True)
    team = db.Column(db.Integer, db.ForeignKey('team.id'),primary_key=True)
    set1 = db.Column(db.Integer)
    set2 = db.Column(db.Integer)
    set3 = db.Column(db.Integer)
    score = db.Column(db.Integer)
    gamepoints = db.Column(db.Integer)
    _matchpoints = db.Column(db.Integer)

    winner = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<MatchResults for team {}>'.format(self.team)

    def get_score(self):
        return dict(set1=self.set1, set2=self.set2, set3=self.set3)

    @hybrid_property
    def matchpoints(self):
        return self._matchpoints

    @matchpoints.setter
    def matchpoints(self, value):
        self._matchpoints = value
        if value > 50:
            self.winner = True
        else:
            self.winner = False
