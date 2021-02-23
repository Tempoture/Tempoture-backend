from flask import Flask
# import Flask-APScheduler
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
@scheduler.task('interval', id='test_job', seconds=15, misfire_grace_time=300)
def job1():
    print('Testing flask-APScheduler for Tempoture!')

if __name__ == '__main__':
    app.run()