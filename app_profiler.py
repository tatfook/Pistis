#
from werkzeug.contrib.profiler import ProfilerMiddleware
from pistis import app

app.config['PROFILE'] = True
app.config['SCHEDULER_API_ENABLED'] = False

app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir='.')
app.run(debug = True)
