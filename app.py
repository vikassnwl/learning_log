from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

app.config['SECRET_KEY'] = '0&\x1ab\x1b\x9b\x9b4\x87\x80\xb6\xae\x9c\x0e\xe6\xff\xcf\xcb\x9c\xfb\x06\x01\xfd\xbb'
# def fmt_dt(dt, fmt):
#     return dt.strftime(fmt)

# app.jinja_env.filters['fmt_dt'] = fmt_dt

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:0000@127.0.0.1/blog'
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
            # flash('Duplicate topic')
        return redirect('/topics')
    return render_template('new_topic.html')
    # return redirect('/topics')


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
        # entry.date = datetime.now()
        db.session.commit()
        return redirect('/topics/'+topic)

    return render_template('edit_entry.html', topic=topic, entry=entry)


# @app.route('/topics/', defaults={'topic': None})
# @app.route('/topics/<topic>')

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
        # topic = Topics.query.filter_by(topics=topic).first()
        # db.session.delete(topic)
        # for entry in entries:
        db.session.delete(entry)
        db.session.commit()
        return redirect('/topics/'+topic)

if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()