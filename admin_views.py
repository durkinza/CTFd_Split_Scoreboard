import os
from flask import render_template, request, current_app as app
from CTFd.utils import get_config
from CTFd.utils.decorators import admins_only, is_admin
from CTFd.models import db, Teams, Fields

# set views
@app.route('/admin/splitscoreboard', methods=['GET'])
@admins_only
def view_scoreboard():

	attributes = Fields.query.order_by(Fields.id.asc()).all()
	selected_key = get_config("split_scoreboard_attr")
	selected_value = get_config("split_scoreboard_value")
	show_custom = get_config("split_scoreboard_custom")

	matched_title = get_config("split_scoreboard_attr_matched_title")
	unmatched_title = get_config("split_scoreboard_attr_unmatched_title")
	
	return render_template(
		"split_scoreboard_attr.html",
		key = selected_key, 
		value = selected_value,
		custom = show_custom,
		attributes = attributes,
		matched_title = matched_title,
		unmatched_title = unmatched_title,
	)


