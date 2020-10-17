import os

import flask
from flask_cors import CORS
from spotipy import SpotifyOauthError
from werkzeug.middleware.proxy_fix import ProxyFix

from spottools import SpotUserActions, get_auth_manager
from store import User
from webservice.config import get_config

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
    for envfield in ('SPOTIPY_CLIENT_SECRET', 'SPOTIPY_CLIENT_ID'):
        # pass some config to the env - for spotipy
        if envfield in config:
            os.environ[envfield] = config[envfield]

    CORS(app)
    if proxied:
        app.wsgi_app = ProxyFix(app.wsgi_app)

    @app.route(f'{api_prefix}/logout', methods=('POST',))
    def logout():
        if 'uid' in flask.session:
            del flask.session['uid']
            return dict(status='ok')
        else:
            return dict(status='not logged in'), 400

    def get_redirect_uri():
        absolute_host = config['EXT_HOSTNAME']
        redirect_uri = f"{absolute_host}{flask.url_for('connect')}"
        return redirect_uri

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

    if False:  # let's skip the catchall in the api - we serve via a frontend proxy
        @app.route("/", defaults={"url": ""})
        @app.route('/<path:url>')
        def catch_all(url):
            """ Handle the page-not-found - apply some backward-compatibility redirect """
            ext = os.path.splitext(url)[-1]
            if ext in SERVED_EXTENSIONS:
                return flask.send_from_directory('ui/dist', url)
            return flask.render_template("index.html")

    @app.route(f'{api_prefix}/')
    def root():
        return flask.render_template("index.html")

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
