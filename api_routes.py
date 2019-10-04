from flask_restplus import Namespace, Resource
from flask import session, jsonify, request, abort

from CTFd.models import Solves, Awards, Teams
from CTFd.cache import cache, make_cache_key
from CTFd.utils import get_config
from CTFd.utils.user import get_current_team, authed, is_admin
from CTFd.utils.modes import generate_account_url, get_mode_as_word, TEAMS_MODE
from CTFd.utils.decorators import (
    during_ctf_time_only,
	admins_only,
	is_admin
)
from CTFd.utils.decorators.visibility import (
	check_account_visibility
)
from CTFd.utils.config.visibility import (
    accounts_visible
)
from sqlalchemy.sql import or_, and_, any_

from CTFd.plugins.CTFd_Team_Attributes.db_tables import db, Attributes, IntersectionTeamAttr
from CTFd.plugins.CTFd_Team_Attributes.schemas import AttributesSchema, IntersectionTeamAttrSchema
from .scores import get_unmatched_standings, get_matched_standings, get_custom_standings

split_scores_namespace = Namespace('split scoreboard', description="Endpoint to retrieve Team Attributes")

def standings_to_string(standings):
    response = []
    mode = get_config("user_mode")
    account_type = get_mode_as_word()
    if mode == TEAMS_MODE:
        team_ids = []
        for team in standings:
            team_ids.append(team.account_id)
        teams = Teams.query.filter(Teams.id.in_(team_ids)).all()
        teams = [next(t for t in teams if t.id == id) for id in team_ids]
    for i, x in enumerate(standings):
        entry = {
            "pos": i + 1,
            "account_id": x.account_id,
            "account_url": generate_account_url(account_id=x.account_id),
            "account_type": account_type,
            "oauth_id": x.oauth_id,
            "name": x.name,
            "score": int(x.score),
        }

        if mode == TEAMS_MODE:
            members = []
            for member in teams[i].members:
                members.append(
                    {
                        "id": member.id,
                        "oauth_id": member.oauth_id,
                        "name": member.name,
                        "score": int(member.score),
                    }
                )

            entry["members"] = members

        response.append(entry)
    return response


@split_scores_namespace.route('')
class SplitScoresList(Resource):
    @check_account_visibility
    def get(self):
        mode = get_config("user_mode")
        team_ids = session.get('teams_watching')
        if team_ids == None:
            team_ids = []
        if request.method == 'POST':
            team_ids = [int(e) for e in request.form.getlist('teams') if str(e).isdigit()]
            if(all(isinstance(item, int) for item in team_ids)):
                session['teams_watching'] = team_ids
 
        if is_admin():
            matched_standings = get_matched_standings()		# student
            unmatched_standings = get_unmatched_standings() # general
            custom_standings = get_custom_standings(team_ids=team_ids)		# selected
        else:
            matched_standings = get_matched_standings()		# student
            unmatched_standings = get_unmatched_standings() # general
            custom_standings = get_custom_standings(team_ids=team_ids)		# selected

        standings = {
            "matched": standings_to_string(matched_standings),
            "unmatched": standings_to_string(unmatched_standings),
            "custom": standings_to_string(custom_standings)
        }

        response = {
            'success':True,
            'data': standings
        }
        return response
