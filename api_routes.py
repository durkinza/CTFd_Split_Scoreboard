from flask_restx import Namespace, Resource
from flask import session, jsonify, request, abort

from CTFd.models import Solves, Awards, Teams, Fields
from CTFd.cache import cache, make_cache_key
from CTFd.utils import get_config, set_config
from CTFd.utils.user import get_current_team, authed, is_admin
from CTFd.utils.modes import generate_account_url, get_mode_as_word, TEAMS_MODE
from CTFd.utils.dates import unix_time_to_utc, unix_time, isoformat
from CTFd.utils.decorators import (
    during_ctf_time_only,
	admins_only,
	is_admin
)
from CTFd.utils.decorators.visibility import (
	check_score_visibility,
	check_account_visibility
)
from CTFd.utils.config.visibility import (
    accounts_visible
)
from sqlalchemy.sql import or_, and_, any_

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
 
        if is_admin():
            matched_standings = get_matched_standings(admin=True)
            unmatched_standings = get_unmatched_standings(admin=True)
            custom_standings = get_custom_standings(team_ids=team_ids, admin=True)
        else:
            matched_standings = get_matched_standings()
            unmatched_standings = get_unmatched_standings()
            custom_standings = get_custom_standings(team_ids=team_ids)

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

    @check_account_visibility
    def post(self):
        if request.method == 'POST':
            team_ids = [int(e) for e in request.form.getlist('teams') if str(e).isdigit()]
            if(all(isinstance(item, int) for item in team_ids)):
                session['teams_watching'] = team_ids
        response = {
            'success':True,
            'data': team_ids
        }
        return response

@split_scores_namespace.route('/top/<int:count>')
@split_scores_namespace.param('count', 'How many top teams to return')
class SplitScoresListCount(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, count):
        mode = get_config("user_mode")
        team_ids = session.get('teams_watching')
        if team_ids == None:
            team_ids = []

        response = {
            "places_matched": {},
            "places_unmatched":{},
            "places_custom": {}
        }

 
        if is_admin():
            matched_standings = get_matched_standings(admin=True, count=count)
            unmatched_standings = get_unmatched_standings(admin=True, count=count)
            custom_standings = get_custom_standings(team_ids=team_ids, admin=True, count=count)
        else:
            matched_standings = get_matched_standings(count=count)
            unmatched_standings = get_unmatched_standings(count=count)
            custom_standings = get_custom_standings(team_ids=team_ids,count=count)

        matched_team_ids = [team.account_id for team in matched_standings]
        unmatched_team_ids = [team.account_id for team in unmatched_standings]
        custom_team_ids = [team.account_id for team in custom_standings]


        matched_solves = Solves.query.filter(Solves.account_id.in_(matched_team_ids))
        matched_awards = Awards.query.filter(Awards.account_id.in_(matched_team_ids))
        unmatched_solves = Solves.query.filter(Solves.account_id.in_(unmatched_team_ids))
        unmatched_awards = Awards.query.filter(Awards.account_id.in_(unmatched_team_ids))
        custom_solves = Solves.query.filter(Solves.account_id.in_(custom_team_ids))
        custom_awards = Awards.query.filter(Awards.account_id.in_(custom_team_ids))


        freeze = get_config('freeze')

        if freeze:
            matched_solves = matched_solves.filter(Solves.date < unix_time_to_utc(freeze))
            matched_awards = matched_awards.filter(Awards.date < unix_time_to_utc(freeze))
            unmatched_solves = unmatched_solves.filter(Solves.date < unix_time_to_utc(freeze))
            unmatched_awards = unmatched_awards.filter(Awards.date < unix_time_to_utc(freeze))
            custom_solves = custom_solves.filter(Solves.date < unix_time_to_utc(freeze))
            custom_awards = custom_awards.filter(Awards.date < unix_time_to_utc(freeze))

        matched_solves = matched_solves.all()
        matched_awards = matched_awards.all()
        unmatched_solves = unmatched_solves.all()
        unmatched_awards = unmatched_awards.all()
        custom_solves = custom_solves.all()
        custom_awards = custom_awards.all()


        for i, team in enumerate(matched_team_ids):
            response['places_matched'][i + 1] = {
                'id': matched_standings[i].account_id,
                'name': matched_standings[i].name,
                'solves': []
            }
            for solve in matched_solves:
                if solve.account_id == team:
                    response['places_matched'][i + 1]['solves'].append({
                        'challenge_id': solve.challenge_id,
                        'account_id': solve.account_id,
                        'team_id': solve.team_id,
                        'user_id': solve.user_id,
                        'value': solve.challenge.value,
                        'date': isoformat(solve.date)
                    })
            for award in matched_awards:
                if award.account_id == team:
                    response['places_matched'][i + 1]['solves'].append({
                        'challenge_id': None,
                        'account_id': award.account_id,
                        'team_id': award.team_id,
                        'user_id': award.user_id,
                        'value': award.value,
                        'date': isoformat(award.date)
                    })
            response['places_matched'][i + 1]['solves'] = sorted(response['places_matched'][i + 1]['solves'], key=lambda k: k['date'])

        for i, team in enumerate(unmatched_team_ids):
            response['places_unmatched'][i + 1] = {
                'id': unmatched_standings[i].account_id,
                'name': unmatched_standings[i].name,
                'solves': []
            }
            for solve in unmatched_solves:
                if solve.account_id == team:
                    response['places_unmatched'][i + 1]['solves'].append({
                        'challenge_id': solve.challenge_id,
                        'account_id': solve.account_id,
                        'team_id': solve.team_id,
                        'user_id': solve.user_id,
                        'value': solve.challenge.value,
                        'date': isoformat(solve.date)
                    })
            for award in unmatched_awards:
                if award.account_id == team:
                    response['places_unmatched'][i + 1]['solves'].append({
                        'challenge_id': None,
                        'account_id': award.account_id,
                        'team_id': award.team_id,
                        'user_id': award.user_id,
                        'value': award.value,
                        'date': isoformat(award.date)
                    })
            response['places_unmatched'][i + 1]['solves'] = sorted(response['places_unmatched'][i + 1]['solves'], key=lambda k: k['date'])

        for i, team in enumerate(custom_team_ids):
            response['places_custom'][i + 1] = {
                'id': custom_standings[i].account_id,
                'name': custom_standings[i].name,
                'solves': []
            }
            for solve in custom_solves:
                if solve.account_id == team:
                    response['places_custom'][i + 1]['solves'].append({
                        'challenge_id': solve.challenge_id,
                        'account_id': solve.account_id,
                        'team_id': solve.team_id,
                        'user_id': solve.user_id,
                        'value': solve.challenge.value,
                        'date': isoformat(solve.date)
                    })
            for award in custom_awards:
                if award.account_id == team:
                    response['places_custom'][i + 1]['solves'].append({
                        'challenge_id': None,
                        'account_id': award.account_id,
                        'team_id': award.team_id,
                        'user_id': award.user_id,
                        'value': award.value,
                        'date': isoformat(award.date)
                    })
            response['places_custom'][i + 1]['solves'] = sorted(response['places_custom'][i + 1]['solves'], key=lambda k: k['date'])


        return {
            'success': True,
            'data': response
        }
	

@split_scores_namespace.route('/settings')
class SplitScoresList(Resource):
	@admins_only
	def get(self):
		response = {
			'success':True,
			'data': {
				"value":get_config("split_scoreboard_value"),
				"attr":get_config("split_scoreboard_attr"),
				'custom':get_config("split_scoreboard_custom")
			}
		}
		return response

	@admins_only
	def post(self):
		
		req = request.get_json()
		attr = Fields.query.filter_by(id = req['attr_id']).first()
		if( attr.field_type == 'boolean' ):
			if( req['value'] ):
				value = 'true'
			else:
				value = 'false'
		else:
			value = req['value']
			
		set_config("split_scoreboard_value", value)
		set_config("split_scoreboard_attr", req['attr_id'])
		set_config("split_scoreboard_custom", req['custom'])

		response = {
            'success':True,
			'test':'test',
            'data': {
				"value":get_config("split_scoreboard_value"),
				"attr":get_config("split_scoreboard_attr"),
				'custom':get_config("split_scoreboard_custom")
			}
        }
		return response
