import os
from datetime import datetime
import functools
from flask import (
    flash, g, redirect, render_template, request, url_for, current_app
)
from flask_babel import _
from werkzeug.exceptions import abort
from werkzeug import secure_filename
from flask_login import login_required, current_user

from paddelranking.website import portraits
from paddelranking.website.utils import is_current_user, fixtures
from paddelranking.website.models import User, db, Tournament, Player, Match, Round, Team, MatchResultsByTeam
from paddelranking.website.users import blueprint
from paddelranking.website.users.forms import EditProfileForm, BaseTournamentForm, MatchPointsForm, MatchForm


def get_portrait_url():
    """ Gets the path to user's portrait image """
    old_portrait_name = current_user.filename or ''

    filepath = os.path.join(
        os.path.join(
            current_app.config['UPLOADED_PORTRAITS_DEST'],
        ),
        old_portrait_name)

    return filepath

@blueprint.route('/')
@login_required
def users():
    if current_user.is_authenticated:
        return redirect(url_for('users.user', username=current_user.username))
    return redirect(url_for('index'))

@blueprint.route('/<username>/')
@login_required
@is_current_user
def user(username):
    # Evitamos que otro usuario intente acceder a un perfil distinto del suyo

    user = User.query.filter_by(username=username).first_or_404()

    return render_template('users/user.html', user=user, title='My control panel')

@blueprint.route('/<username>/profile.html', methods=('GET', 'POST'))
@login_required
@is_current_user
def edit_profile(username):

    user = User.query.filter_by(id=current_user.id).first()
    form = EditProfileForm(obj=user)
    if form.is_submitted():
        if form.cancel.data:
            flash(_('Changes canceled!'))
            return redirect(url_for('users.user', username=username))

        if form.validate_on_submit():

                form.populate_obj(user)
                user.last_modified = datetime.utcnow()

                if 'portrait' in request.files:
                    # Eliminamos la imagen
                    filepath = get_portrait_url()
                    if os.path.exists(filepath) and user.filename:
                        os.remove(filepath)

                    # Preparamos la nueva imagen
                    portrait = request.files.get('portrait')
                    filename, ext = str(portrait.filename).split('.')
                    portrait.filename = '{}.{}'.format(user.portrait_hash(), ext)
                    filename = portraits.save(portrait)
                    user.filename = filename
                db.session.add(user)
                db.session.commit()
                flash(_('Changes saved!'))

        if form.errors:
            flash(_('Please, correct errors found!'))

    return render_template('/users/edit_profile.html', title=_('Edit my profile'), form=form, filename=user.filename)

@blueprint.route('/<username>/profile/delete', methods=('GET',))
@login_required
def remove_profile_image(username):
    if current_user.username != username:
        flash('You cannot access a control panel other than yours', 'error')
        return redirect(url_for('users.user', username=current_user.username))

    user = User.query.filter_by(id=current_user.id).first()
    filepath = get_portrait_url()
    if os.path.exists(filepath):
        os.remove(filepath)
        user.filename = ''
        db.session.add(user)
        db.session.commit()
        flash('Portrait deleted.')
    return redirect(url_for('users.edit_profile', username=current_user.username))

@blueprint.context_processor
def utility_processor():
    filepath = get_portrait_url()

    if os.path.exists(filepath) and current_user.filename:
        original_image_url = url_for('users.static', filename='uploads/portraits/' + current_user.filename, _external=True)
        url_imagen = current_app.resize(original_image_url, '300x300',fill=1)
    else:
        url_imagen = url_for('static', filename='images/user.png', _external=True)

    return dict(profile_imagen=url_imagen)

@blueprint.route('/<username>/my-tournaments.html')
@login_required
@is_current_user
def my_tournaments(username):

    user = User.query.filter_by(username=username).first_or_404()
    tours = Tournament.query.filter_by(createdby=current_user.id).order_by(Tournament.closed,Tournament.created.desc())
    return render_template('users/my_tournaments.html', user=user, tours=tours, title='My tournaments')

@blueprint.route('/<username>/create-tournament.hmtl', methods=['POST', 'GET'])
@login_required
@is_current_user
def create_tournament(username):

    tour = Tournament()
    form = BaseTournamentForm(request.form)

    form.players.min_entries=4

    if form.add_player.data:
        getattr(form,'players_input').append_entry()
        return render_template('/users/create_tournament.html', title='Create new tournament', form=form)

    if form.is_submitted():
        if form.cancel.data:
            flash('Changes canceled!')
            return redirect(url_for('users.my_tournaments', username=username))

        if form.validate_on_submit():
            newplayers = []
            for newplayer in form.players_input.data:
                if newplayer.get('playername'):
                    player = Player(**newplayer)

                    player.createdby = current_user.id
                    newplayers.append(player)

            form.populate_obj(tour)
            tour.closed = False
            tour.players.extend(newplayers)
            tour.createdby = current_user.id
            db.session.add(tour)
            db.session.commit()
            flash('Changes saved!')
            return redirect(url_for('users.my_tournaments', username=username))

        if form.errors:
            flash('Please, correct errors found!')

    return render_template('/users/create_tournament.html', title='Create new tournament', form=form)

@blueprint.route('/<username>/process_add_member', methods=['POST'])
@login_required
@is_current_user
def add_player(username):

    form = TournamentForm()
    getattr(form,'players_input').append_entry()

    return render_template('/users/players.html', form=form)

@blueprint.route('/<username>/tour-<int:id>.hmtl', methods=['POST', 'GET'])
@login_required
@is_current_user
def tournament(username, id):
    user = User.query.filter_by(username=username).first_or_404()
    tour = Tournament.query.filter_by(id=id).first_or_404()

    return render_template('users/tournament.html', user=user, tour=tour)

@blueprint.route('/<username>/tour-<int:tourid>/match-<int:matchid>.hmtl', methods=['POST', 'GET'])
@login_required
@is_current_user
def edit_match(username, tourid, matchid):
    user = User.query.filter_by(username=username).first_or_404()
    tour = Tournament.query.filter_by(id=tourid).first_or_404()
    match = Match.query.filter_by(id=matchid).first_or_404()

    results = match.results
    form = MatchForm(request.form, obj=match, results=results.all())


    if form.is_submitted():
        if form.cancel.data:
            flash('Changes canceled!')
            return redirect(url_for('users.tournament', username=username, id=tour.id))

        if form.validate_on_submit():
            scores = []
            teams = (match.team1, match.team2)

            for idx, score in enumerate(form.results.data):
                # Set score, game points and match points
                gamepoints = 0
                for key, value in score.items(): 
                    gamepoints+= value>=6 and  value*2 or value
                
                score['gamepoints'] = gamepoints
                if not results.all():
                    matchresult = MatchResultsByTeam(**score)
                    matchresult.match_id = match.id
                    matchresult.team = teams[idx]
                else:
                    matchresult = results[idx]
                    for key, value in score.items():
                        setattr(matchresult, key, value)

                scores.append(matchresult)


            match.matchdate = form.matchdate.data
            match.played = True
            match.results.extend(scores)
            import pdb; pdb.set_trace()
            games = match.results.all()
            score1 = games[0]
            score2 = games[1]
            
            score1.matchpoints = round(score1.gamepoints / (score1.gamepoints+score2.gamepoints)*tour.point_per_match)
            score2.matchpoints = round(score2.gamepoints / (score1.gamepoints+score2.gamepoints)*tour.point_per_match)
            
            db.session.add(match)
            db.session.commit()

            flash('Changes saved!')
            return redirect(url_for('users.tournament', username=username, id=tour.id))

        if form.errors:
            flash('Please, correct errors found!', 'error')
    return render_template('/users/edit_match.html', title=_('Edit match'), form=form, tour=tour, match=match)

@blueprint.route('/<username>/tour-<int:id>/create-matches', methods=['POST', 'GET'])
@login_required
@is_current_user
def create_matches(username, id):
    tour = Tournament.query.filter_by(id=id).first_or_404()
    user = User.query.filter_by(username=username).first_or_404()
    players = tour.players.all()
    rounds = tour.rounds_qty
    matches_per_round = tour.match_per_round

    single_matches = list(fixtures(players))

    is_singles=False
    if len(single_matches[0]) % 2:
        is_singles = True
    for single_match in single_matches:
        round = Round(tour=tour.id)

        db.session.add(round)
        db.session.commit()

        round_id = round.id
        if not is_singles:
            p1, p2 = single_match[0]
            p3, p4 = single_match[1]
            team1 = Team(player1=p1.id, player2=p2.id)
            team2 = Team(player1=p3.id, player2=p4.id)
        else:
            player1, player2 = single_match[0]
            team1 = Team(player1=player1.id)
            team2 = Team(player1=player2.id)
        db.session.add_all([team1, team2])
        db.session.commit()
        for idx in range(matches_per_round):
            
            data = {
                'tour': tour.id,
                'team1': team1.id,
                'team2': team2.id,
                'roundid': round_id,
                'order': idx+1,
            }
            if is_singles:
                data['doubles'] = False
            match = Match(**data)
            db.session.add(match)
            db.session.commit()

    flash(_('All matches created.'))
    return redirect(url_for('users.tournament', username=current_user.username, id=tour.id))

@blueprint.context_processor
def utility_processor():
    def team_players(teamid):
        team = Team.query.get(teamid)
        player1 = Player.query.get(team.player1)
        player2 = Player.query.get(team.player2 or '')
        if player2:
            return (player1, player2)
        return player1,
    return dict(team_players=team_players)

@blueprint.context_processor
def utility_processor():
    def match_points(matchid, teamid):
        points = MatchResultsByTeam.query.filter_by(match_id=matchid,team=teamid).first()
        return points
    return dict(match_points=match_points)