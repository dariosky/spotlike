import os

import flask
from flask_cors import CORS

try:
    import bjoern
except ImportError:
    bjoern = None

SERVED_EXTENSIONS = {'.jpg', '.ico', '.png', '.map', '.js', '.svg',
                     '.json', '.css', '.txt'}


def get_app(production=True):
    app = flask.Flask(__name__)
    CORS(app)

    @app.route("/", defaults={"url": ""})
    @app.route('/<path:url>')
    def catch_all(url):
        """ Handle the page-not-found - apply some backward-compatibility redirect """
        ext = os.path.splitext(url)[-1]
        if ext in SERVED_EXTENSIONS:
            return flask.send_from_directory('ui/build', url)
        return flask.render_template("index.html")

    return app


def run_api(host='127.0.0.1', port=3001,
            production=True):
    app = get_app(production=production)
    if production:
        print(f"Running production server as "
              f"{'bjoern' if bjoern else 'Flask'}"
              f" on http://{host}:{port}")
        if bjoern:
            # apt-get install libev-dev
            # apt-get install python3-dev
            bjoern.run(app, host, port)
        else:
            app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)
    else:
        print("Running in Flask debug mode")
        app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_api(host='localhost', port=4000, production=False)
