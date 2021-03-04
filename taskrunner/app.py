from flask import Flask
# import Flask-APScheduler
import requests
from flask_apscheduler import APScheduler

# set configuration values
class Config(object):
    SCHEDULER_API_ENABLED = True

# create app
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

# interval example
@scheduler.task('interval', id='Call_Store', seconds=30, misfire_grace_time=300)
def store():
    auth_header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        resp = requests.get("http://127.0.0.1:5000/store_tracks", headers=auth_header)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERR:" + str(err))

if __name__ == '__main__':
    app.run(port=8080)