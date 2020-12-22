import json
import os
import traceback

import flask
import requests
from flask_cors import CORS
from spotipy import SpotifyOauthError
from werkzeug.exceptions import NotFound
from werkzeug.middleware.proxy_fix import ProxyFix

from spottools import SpotUserActions, get_auth_manager
from store import User, Message
from webservice.config import get_config, activate_config

try:
    import bjoern
except ImportError:
    bjoern = None

SERVED_EXTENSIONS = {'.jpg', '.ico', '.png', '.map', '.js', '.svg',
                     '.json', '.css', '.txt'}


def get_app(config):
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = config['SECRET_KEY']
    proxied = config.get("PROXIED", True)
    api_prefix = config.get("API_PREFIX", "/api")
    activate_config(config)
    error_log_endpoint = config.get('WEBHOOK_LOGGER')
    error_log_session = requests.session() if error_log_endpoint else None

    def log_error(message):
        if not error_log_endpoint:
            return
        error_log_session.post(
            error_log_endpoint,
            headers={"Content-type": "application/json"},
            json={"text": message}
        )

    CORS(app)
    if proxied:
        app.wsgi_app = ProxyFix(app.wsgi_app)

    def login_required(func):
        """ Wrapper to ensure user is logged """

        def wrapper(*args, **kwargs):
            if not current_user():
                return dict(error='Not logged in'), 401
            func(*args, **kwargs)

        return wrapper

    def current_user():
        uid = flask.session.get('uid')
        if uid:
            return User.get_by_id(uid)

    @login_required
    @app.route(f'{api_prefix}/logout', methods=('POST',))
    def logout():
        del flask.session['uid']
        return dict(status='ok')

    def get_redirect_uri():
        absolute_host = config['EXT_HOSTNAME']
        redirect_uri = f"{absolute_host}{flask.url_for('connect')}"
        return redirect_uri

    @app.route(f'{api_prefix}/status')
    def get_status():
        return {"status": "OK"}

    @app.route(f'{api_prefix}/user')
    def get_current_user():
        uid = flask.session.get('uid')
        if not uid:
            act = SpotUserActions(user=None, connect=False,
                                  redirect_uri=get_redirect_uri())
            return dict(  # not a user
                spotify_connect_url=act.auth_manager.get_authorize_url(),
            ), 401
        else:
            user = User.get_by_id(uid)
            # act = SpotUserActions(user=user)
            return dict(
                id=user.id,
                name=user.name,
                email=user.email,
                picture=user.picture,
            )

    @app.route(f'{api_prefix}/connect')
    def connect():
        code = flask.request.args.get("code")
        redirect_uri = get_redirect_uri()
        try:
            auth_manager = get_auth_manager(None, redirect_uri=redirect_uri)
            auth_manager.get_access_token(code, check_cache=False)
            act = SpotUserActions(user=None, auth_manager=auth_manager)
            flask.session['uid'] = act.user.id
            # return act.user.as_json()
            return flask.redirect('/')
        except SpotifyOauthError as e:
            return {"message": str(e)}, 400

    @app.route(f'{api_prefix}/redirect')
    def redir():
        return flask.redirect('/')

    @app.errorhandler(400)
    @app.errorhandler(500)
    def handle_errors(e):
        return {"error": e.name, "description": e.description}, e.code

    if False:  # let's skip the catchall in the api - we serve via a frontend proxy
        @app.route("/", defaults={"url": ""})
        @app.route('/<path:url>')
        def catch_all(url):
            """ Handle the page-not-found - apply some backward-compatibility redirect """
            ext = os.path.splitext(url)[-1]
            if ext in SERVED_EXTENSIONS:
                return flask.send_from_directory('ui/dist', url)
            return flask.render_template("index.html")

    @login_required
    @app.route(f"{api_prefix}/events")
    def events():
        page = flask.request.args.get('page', 1)
        items = flask.request.args.get('items', 30)
        messages = current_user().messages.select() \
            .order_by(Message.date.desc()).paginate(page, items)
        return {
            "items": [
                dict(
                    id=message.id,
                    message=message.message,
                    date=message.date)
                for message in messages
            ]
        }

    @app.route(f'{api_prefix}/')
    def root():
        return flask.render_template("index.html")

    @app.errorhandler(Exception)
    def handle_500(e):
        if not isinstance(e, NotFound):
            error_tb = traceback.format_exc()
            log_error(f"Error or {flask.request.path} - user {current_user()}: {e}\n"
                      f"```{error_tb}```")
        return app.finalize_request(e, from_error_handler=True)

    return app


def run_api(config):
    host = config.get('HOST', 'localhost')
    port = config.get('PORT', 4000)
    if not config.get('DEVSERVER', True):
        print(f"Running production server as "
              f"{'bjoern' if bjoern else 'Flask'}"
              f" on http://{host}:{port}")
        if bjoern:
            bjoern.run(app, host, port)
        else:
            app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)
    else:
        print("Running in Flask debug mode")
        app.run(host=host, port=port, debug=True)


environment = os.environ.get('ENV', 'dev')
app = get_app(get_config(environment))

if __name__ == '__main__':
    print(f"Running as {environment}")
    run_api(get_config(environment))
