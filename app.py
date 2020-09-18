from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import json
import os
import re

app = Flask(__name__)

def markdown(s):

    # markdown for bold text
    regex_bold = re.compile(r'\*(.+)\*')
    s = regex_bold.sub(r'<b>\1</b>', s)

    # markdown for italic text
    regex_italic = re.compile(r'\_(.+)\_')
    s = regex_italic.sub(r'<i>\1</i>', s)

    # markdown for strike text
    regex_s = re.compile(r'- (.+)')
    s = regex_s.sub(r'<s>\1</s>', s)

    # markdown for heading
    regex_h = re.compile(r'(#+) (.+\n?)')
    regex_match = re.findall(regex_h, s)
    for match in regex_match:
        regex = re.compile(r''+match[0]+' '+match[1]+'')
        s = regex.sub(r'<h'+str(len(match[0]))+'>'+match[1]+'</h'+str(len(match[0]))+'>', s)

    # handling new line
    s = s.replace('\n', '<br>')

    # handling spaces
    regex_space = re.compile(r'(\s)')
    s = regex_space.sub(r'&nbsp;', s)
    return s

app.jinja_env.filters['markdown'] = markdown

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
    entries = db.relationship('Entries', backref='tpcs')
    date = db.Column(db.DateTime, nullable=False)


class Entries(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    entries = db.Column(db.String, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.sno'))
    date = db.Column(db.DateTime, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/topics/', defaults={'topic': None})
@app.route('/topics/<topic>')
def topics(topic):
    if topic:
        topics = Topics.query.filter_by(topics=topic).first()
        entries = Entries.query.filter_by(topic_id=topics.sno).order_by(Entries.date.desc()).all()
        return render_template('topic.html', topic=topic, entries=entries)

    topics = Topics.query.order_by(Topics.date.desc()).all()
    return render_template('topics.html', logs=topics)


@app.route('/new_topic', methods=['GET', 'POST'])
def new_topic():
    if request.method == 'POST':
        topic = request.form.get('new_topic')
        if local_server:
            date = datetime.now()
        else:
            date = datetime.now()+timedelta(hours=5, minutes=30)
        entry = Topics(topics=topic, date=date)
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
        if local_server:
            date = datetime.now()
        else:
            date = datetime.now()+timedelta(hours=5, minutes=30)
        topics = Topics.query.filter_by(topics=topic).first()
        entry = Entries(entries=entry, tpcs=topics, date=date)
        db.session.add(entry)
        db.session.commit()
        return redirect('/topics/'+topic)

    text = request.args.get('jsdata')
    if not text:
        text = ''
    print(text, 'this is text')
    return render_template('new_entry.html', topic=topic, text=text)


@app.route('/edit_topic/<topic>', methods=['GET', 'POST'])
def edit_topic(topic):
    topics = Topics.query.filter_by(topics=topic).first()
    entries = Entries.query.filter_by(topic_id=topics.sno).all()
    if request.method == 'POST':
        edited_topic = request.form.get('edit_topic')
        topics.topics = edited_topic
        for entry in entries:
            entry.topics = edited_topic
        db.session.commit()
        return redirect('/topics')

    return render_template('edit_topic.html', topic=topic)


with open('emojis.json') as f:
    emojis_dict = json.load(f)

@app.route('/edit_entry/<topic>/<sno>', methods=['GET', 'POST'])
def edit_entry(topic, sno):
    entry = Entries.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        entry.entries = request.form.get('edit_entry')
        db.session.commit()
        return redirect('/topics/'+topic)


    emoji = request.args.get('jsdata')
    emojis_list = []
    if emoji:
        for key, value in emojis_dict.items():
            if emoji in key:
                emojis_list.append(value)

    return render_template('edit_entry.html', topic=topic, entry=entry, emojis_list=emojis_list)


@app.route('/delete/<topic>/', defaults={'sno': None})
@app.route('/delete/<topic>/<sno>')
def delete(topic, sno):
    if not sno:
        topic = Topics.query.filter_by(topics=topic).first()
        entries = Entries.query.filter_by(topic_id=topic.sno).all()
        
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


@app.route('/render_emojis')
def render_emojis():
    emojis_list = []
    text = request.args.get('jsdata')
    input_data = request.args.get('input_data')
    for key, value in emojis_dict.items():
        if text in key:
            emojis_list.append(value)
    return render_template('render_emojis.html', emojis_list=emojis_list, input_data=input_data)


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
