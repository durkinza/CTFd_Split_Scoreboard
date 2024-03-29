from flask import render_template, Blueprint, redirect, url_for, request, session, current_app as app

from CTFd.utils import config
from CTFd.utils import get_config
from CTFd.utils.decorators.visibility import check_score_visibility
from CTFd.models import Teams, Fields
from CTFd.schemas.teams import TeamSchema
from .scores import get_unmatched_standings, get_matched_standings, get_custom_standings

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
    matched_standings = get_matched_standings()
    unmatched_standings = get_unmatched_standings()
    custom_standings = get_custom_standings(team_ids=team_ids)
    teams = Teams.query.filter_by(banned=False)
    watching = session.get('teams_watching')


    selected_value = get_config("split_scoreboard_value") if get_config("split_scoreboard_value") != None else 1
    selected_attr_id = get_config("split_scoreboard_attr") if get_config("split_scoreboard_attr") != None else -1
    selected_attr_matched_title = get_config("split_scoreboard_attr_matched_title") if get_config("split_scoreboard_attr_matched_title") != None else "matched"
    selected_attr_unmatched_title = get_config("split_scoreboard_attr_unmatched_title") if get_config("split_scoreboard_attr_unmatched_title") != None else "unmatched"

	
    if int(selected_attr_id) > 0:
        attr_name = Fields.query.filter_by(id=selected_attr_id).first_or_404()
        attr_name = attr_name.name
    elif int(selected_attr_id) == -1:
        attr_name = "Team Size is "+str(selected_value)
    elif int(selected_attr_id) == -2:
        attr_name = "Team Size is less than "+str(selected_value)
    elif int(selected_attr_id) == -3:
        attr_name = "Team Size is greater than "+str(selected_value)
	
    show_custom = get_config("split_scoreboard_custom")
    return render_template(
       'scoreboard.html',
		custom = show_custom,
        teams = teams,
		matched_title = selected_attr_matched_title,
		unmatched_title = selected_attr_unmatched_title,
        watching = watching,
        matched_standings = matched_standings,
        unmatched_standings = unmatched_standings,
        custom_standings = custom_standings,
        score_frozen=config.is_scoreboard_frozen()
    )
    

