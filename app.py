from flask import Flask
from flask_babel import Babel

from routes.main import main_bp
from routes.clubs import clubs_bp
from routes.teams import teams_bp
from routes.calendars import calendars_bp

from utils.language import get_locale
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1
)

app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(
    app,
    locale_selector=get_locale
)

app.jinja_env.globals['get_locale'] = get_locale


app.register_blueprint(main_bp)
app.register_blueprint(clubs_bp)
app.register_blueprint(teams_bp)
app.register_blueprint(calendars_bp)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )