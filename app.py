from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import json
import os

app = Flask(__name__)

with open('config.json') as c:
    params = json.load(c)

# chage it to true to connect to local database.
local_server = False

if local_server:
    database_uri = params['database_uri']
    secret_key = params['secret_key']
else:
    database_uri = os.environ.get('DATABASE_URL')
    secret_key = os.environ.get('SECRET_KEY')

app.config['SECRET_KEY'] = secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class Topics(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    topics = db.Column(db.String, unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class Entries(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    topics = db.Column(db.String, nullable=False)
    entries = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/topics/', defaults={'topic': None})
@app.route('/topics/<topic>')
def topics(topic):
    if topic:
        entries = Entries.query.filter_by(topics=topic).order_by(Entries.date.desc()).all()
        return render_template('topic.html', topic=topic, entries=entries)

    topics = Topics.query.order_by(Topics.date.desc()).all()
    return render_template('topics.html', logs=topics)


@app.route('/new_topic', methods=['GET', 'POST'])
def new_topic():
    if request.method == 'POST':
        topic = request.form.get('new_topic')
        entry = Topics(topics=topic, date=datetime.now())
        db.session.add(entry)
        try:
            db.session.commit()
        except:
            flash(topic+' already exists')
        return redirect('/topics')
    return render_template('new_topic.html')


@app.route('/new_entry/<topic>', methods=['GET', 'POST'])
def new_entry(topic):
    if request.method == 'POST':
        entry = request.form.get('new_entry')
        entry = Entries(topics=topic, entries=entry, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        return redirect('/topics/'+topic)
    return render_template('new_entry.html', topic=topic)


@app.route('/edit_entry/<topic>/<sno>', methods=['GET', 'POST'])
def edit_entry(topic, sno):
    entry = Entries.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        entry.entries = request.form.get('edit_entry')
        db.session.commit()
        return redirect('/topics/'+topic)

    return render_template('edit_entry.html', topic=topic, entry=entry)


@app.route('/delete/<topic>/', defaults={'sno': None})
@app.route('/delete/<topic>/<sno>')
def delete(topic, sno):
    if not sno:
        entries = Entries.query.filter_by(topics=topic).all()
        topic = Topics.query.filter_by(topics=topic).first()
        db.session.delete(topic)
        for entry in entries:
            db.session.delete(entry)
        db.session.commit()
        return redirect('/topics')
    else:
        entry = Entries.query.filter_by(sno=sno).first()
        db.session.delete(entry)
        db.session.commit()
        return redirect('/topics/'+topic)


# make it true if you want to automatically create tables into database using above class structure
make_migration = False
# after making it true follow these commands:
    # python3 app.py db init
    # python3 app.py db migrate
    # python3 app.py db upgrade
# after successfully migrating tables to databse, run the app using:
    # python3 app.py


if __name__ == '__main__':
    if make_migration:
        manager.run()
    else:
        app.run(debug=True)
