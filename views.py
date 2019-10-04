from flask import render_template, Blueprint, redirect, url_for, request, session, current_app as app

from CTFd.utils import config
from CTFd.utils import get_config
from CTFd.utils.decorators.visibility import check_score_visibility
from CTFd.models import Teams
from CTFd.schemas.teams import TeamSchema
from .scores import get_unmatched_standings, get_matched_standings, get_custom_standings
import copy


@app.route('/scoreboard', methods=['GET', 'POST'])
@check_score_visibility
def view_split_scoreboard():
    team_ids = session.get('teams_watching')
    if team_ids == None:
        team_ids = []
    if request.method == 'POST':
        team_ids = [int(e) for e in request.form.getlist('teams') if str(e).isdigit()]
        if(all(isinstance(item, int) for item in team_ids)):
            session['teams_watching'] = team_ids
    matched_standings = get_matched_standings()		# student
    unmatched_standings = get_unmatched_standings() # general
    custom_standings = get_custom_standings(team_ids=team_ids)		# selected
    teams = Teams.query.filter_by(banned=False)
    watching = session.get('teams_watching')
    return render_template(
       'scoreboard.html',
        teams = teams,
        watching = watching,
        matched_standings = matched_standings,
        unmatched_standings = unmatched_standings,
        custom_standings = custom_standings,
        score_frozen=config.is_scoreboard_frozen()
    )
    

