import os
from flask import render_template, request, current_app as app
from CTFd.utils import get_config
from CTFd.utils.decorators import admins_only, is_admin
from CTFd.models import db, Teams

from CTFd.plugins.CTFd_Team_Attributes.db_tables import Attributes, IntersectionTeamAttr

# set views
@app.route('/admin/splitscoreboard', methods=['GET'])
@admins_only
def view_scoreboard():

	attributes = Attributes.query.order_by(Attributes.id.asc()).all()
	selected_key = get_config("split_scoreboard_attr")
	selected_value = get_config("split_scoreboard_value")
	
	return render_template(
		"split_scoreboard_attr.html",
		key = selected_key, 
		value = selected_value,
		attributes = attributes
	)


