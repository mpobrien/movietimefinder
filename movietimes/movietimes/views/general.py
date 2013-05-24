from datetime import datetime
from movietimes import app
from flask import Blueprint, render_template, session, redirect, url_for, \
    request, flash, g, jsonify, abort

mod = Blueprint('general', __name__, url_prefix='/')

with app.app_context():
    db = app.mongo.db


#@mod.route('/')
def hello_world():
    print "here"
    theaters = list(db.theaters.find())
    return render_template("index.html", theaters=theaters)

@mod.route('/')
def get_times():
    day = request.args.get('date', datetime.now().strftime('%m/%d/%y'))
    day_parsed = datetime.strptime(day, '%m/%d/%y')
    showtimes = list()
    theaters_id = {}
    for theater in db.theaters.find():
        theaters_id[theater['_id']] = theater
    for showtime in db.showtimes.find({'_date':day_parsed}):
        theaters_id[showtime['_theater']]['times'] = showtime
        

    return render_template("times.html", theaters=theaters_id)
