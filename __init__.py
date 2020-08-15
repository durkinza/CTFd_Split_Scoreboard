import os
from flask import Blueprint
from flask_restx import Api
from CTFd.plugins import register_plugin_assets_directory, register_admin_plugin_script
from CTFd.utils.plugins import override_template

from . import admin_views
from .views import view_split_scoreboard
from .api_routes import split_scores_namespace

def load(app):
	# get plugin location
	dir_path = os.path.dirname(os.path.realpath(__file__))
	register_plugin_assets_directory(app, base_path="/plugins/CTFd_Split_Scoreboard/assets/")

	# Admin Pages 
	override_template('split_scoreboard_attr.html', open(os.path.join(dir_path, 'assets/admin/split_scoreboard_attr.html')).read())

	# Admin Modals
	override_template('admin_ss_form.html', open(os.path.join(dir_path, 'assets/admin/modals/admin_ss_form.html')).read())


	# Team settings page override
	override_template('scoreboard.html', open(os.path.join(dir_path, 'assets/teams/scoreboard.html')).read())

	# Team Modals
	app.view_functions['scoreboard.listing'] = view_split_scoreboard

	# Blueprint used to access the static_folder directory.
	blueprint = Blueprint(
		"split_scores", __name__, template_folder="templates", static_folder="assets"
	)

	api = Blueprint("split_scoreboard_api", __name__, url_prefix="/api/v1")
	Split_Scores_API_v1 = Api(api, version="v1", doc=app.config.get("SWAGGER_UI"))
	Split_Scores_API_v1.add_namespace(split_scores_namespace, "/split_scores")
	app.register_blueprint(api)
