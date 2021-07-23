from flask import Flask, render_template, session,request, flash, redirect
from helpers import login_required
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash as gen_hash
from werkzeug.security import check_password_hash as check_hash
import sqlite3
from flask_sqlalchemy import *
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret'
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Session(app)

VACCINE_WAIT = 21
POSITIVE_QUARANTINE = 28
VACCINE_EFFECT = 365
NEGATIVE_EFFECT = 2

events = ["Tested Positive", "Tested Negative", "Vaccinated"]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    events = db.relationship("User_history", backref="user")
    parties = db.relationship("Party", backref="user")
    def __repr__(self):
        return '<User %r>' % self.username

class User_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), unique=False, nullable=False)
    event_date_start = db.Column(db.DateTime, unique=False, nullable=False)
    event_date_end = db.Column(db.DateTime, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Event %r>' % self.id

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(120), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    party_date = db.Column(db.DateTime, unique=False, nullable=False)
    host_email = db.Column(db.String(200), unique=False, nullable=False)
    def __repr__(self):
        return '<Party %r>' % self.id



@app.route('/')
@login_required
def index():
    #result_query = User.query.join(User.events)
    user_conn = User.query.filter_by(id=session["user_id"]).first()
    #result_query = result_query.filter_by(id=session["user_id"])
    #user_events = user_conn.join(User.events)
    current_status = "Untested"
    positive_pos = True
    user_events = User_history.query.filter_by(user_id=session["user_id"])
    user_events = user_events.filter(User_history.event_date_start <= datetime.now())
    user_events = user_events.order_by(User_history.event_date_start.desc())
    for event_i in user_events.all():
        print(event_i.event_type)
    for event_i in user_events.all():
        print(event_i.event_type)
        if event_i.event_type == "Tested Negative":
            print("--------")
            print(event_i.event_date_end)
            print(datetime.now())
            print("--------")
            if event_i.event_date_end >= datetime.now():
                current_status = event_i.event_type
                return render_template("index.html", user=user_conn.username, user_curr_status=current_status)
            else:
                positive_pos = False
        elif event_i.event_type == "Vaccinated" and event_i.event_date_end >= datetime.now():
            current_status = event_i.event_type
        elif event_i.event_type == "Tested Positive" and positive_pos == True and event_i.event_date_end >= datetime.now():
            current_status = event_i.event_type
            return render_template("index.html", user=user_conn.username, user_curr_status=current_status)

    #print(user_events.all())
    return render_template("index.html", user=user_conn.username, user_curr_status=current_status)
#User.query.filter_by(id=session["user_id"]).first().username
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        if not request.form.get("username"):
            flash("No username")
            return redirect('/')
        if not request.form.get("password"):
            flash("No password")
            return redirect('/')
        username = request.form.get("username")
        password = request.form.get("password")
        found_user = User.query.filter_by(username=username).first()
        if found_user:
            if check_hash(found_user.password, password):
                session["user_id"] = found_user.id
                session["invites"] = []
                session["date"] = None
                return redirect('/')
            else:
                flash("Password incorrect")
                return redirect('/')
        else:
            flash("Username incorrect")
            return redirect('/')

    else:
        return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session.permanent = True
        if not request.form.get("username"):
            flash("No username")
            return redirect('/register')
        if not request.form.get("password"):
            flash("No password")
            return redirect('/register')
        if not request.form.get("email"):
            return redirect('/register')
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        found_user = User.query.filter_by(username=username).first()
        found_email = User.query.filter_by(email=email).first()
        if found_user or found_email:
            flash("Username / email taken")
            return redirect('/register')
        else:
            pass_hash = gen_hash(password)
            new_user = User(username=username, password=pass_hash, email=email)
            db.session.add(new_user)
            db.session.commit()
            #default_event = User_history(event_type="Untested", event_date_start=datetime.now(), event_date_end=datetime.now() + timedelta(seconds=10), user=new_user)
            #db.session.add(default_event)
            #db.session.commit()
            #session["user_id"] = new_user.id
            print(new_user.id)
            print()
            return redirect('/login')

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('invites', None)
    session.pop('date', None)
    return redirect("/")

@app.route("/status", methods=["GET", "POST"])
@login_required
def status():
    if request.method == "POST":
        if not request.form.get("event"):
            flash("No event")
            return redirect('/status')
        if not request.form.get("event_date"):
            flash("No event date")
            return redirect('/status')
        event_name = request.form.get("event")
        event_date = datetime.strptime(request.form.get("event_date"), '%Y-%m-%d')
        if event_name not in events or event_date > datetime.now():
            return redirect('/status')
        user_conn = User.query.filter_by(id=session["user_id"]).first()
        if event_name == "Tested Positive":
            new_status = User_history(event_type=event_name, event_date_start=event_date, event_date_end=event_date + timedelta(days=POSITIVE_QUARANTINE), user=user_conn)
            db.session.add(new_status)
            db.session.commit()
        elif event_name == "Tested Negative":
            new_status = User_history(event_type=event_name, event_date_start=event_date, event_date_end=event_date + timedelta(days=NEGATIVE_EFFECT), user=user_conn)
            db.session.add(new_status)
            db.session.commit()
        elif event_name == "Vaccinated":
            new_status = User_history(event_type=event_name, event_date_start=event_date + timedelta(days=VACCINE_WAIT), event_date_end=event_date + timedelta(days=VACCINE_EFFECT), user=user_conn)
            db.session.add(new_status)
            db.session.commit()
        return redirect('/')
    else:
        return render_template("status.html", events=events, today=datetime.now().strftime('%Y-%m-%d'))



@app.route('/org', methods=["GET", "POST"])
@login_required
def create_parties():
    
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("party_date")
        if not name or not date:
            return redirect('/org')
        date = datetime.strptime(date, '%Y-%m-%d')
        found = User.query.filter_by(username=name).first()
        if found and name not in session["invites"]:
            session["invites"].append(name)
            session['date'] = date
        return redirect('/org')
    else:
        if session["date"]:
            date_string = session["date"].strftime('%Y-%m-%d')
        else:
            date_string = datetime.now() + timedelta(days=1)
            date_string = date_string.strftime('%Y-%m-%d')
        return render_template("create_parties_input.html", people=session["invites"], today=datetime.now().strftime('%Y-%m-%d'), def_date=date_string)

@app.route('/org_view', methods=['GET', 'POST'])
@login_required
def create_parties_view():
    if request.method == "POST":
        for person in session["invites"]:
            new_party = Party(host=User.query.filter_by(id=session["user_id"]).first().username, user=User.query.filter_by(username=person).first(), party_date=session['date'], host_email=User.query.filter_by(id=session["user_id"]).first().email)
            db.session.add(new_party)
            db.session.commit()
        session.pop('invites', None)
        session.pop('date', None)
        return redirect('/')
    else:
        people_dict = {}
        for person in session["invites"]:
            person_id = User.query.filter_by(username=person).first().id
            current_status = "Untested"
            positive_pos = True
            user_events = User_history.query.filter_by(user_id=person_id)
            user_events = user_events.filter(User_history.event_date_start <= session["date"])
            user_events = user_events.order_by(User_history.event_date_start.desc())
            for event_i in user_events.all():
                
                if event_i.event_type == "Tested Negative":
                    if event_i.event_date_end >= session["date"]:
                        diff = event_i.event_date_end.date() - session["date"].date()
                        current_status = event_i.event_type + " expires in " + str(diff.days) + " days"
                        break
                    else:
                        positive_pos = False
                elif event_i.event_type == "Vaccinated" and event_i.event_date_end >= session["date"]:
                    diff = event_i.event_date_end.date() - session["date"].date()
                    current_status = event_i.event_type + " expires in " + str(diff.days) + " days"
                elif event_i.event_type == "Tested Positive" and positive_pos == True and event_i.event_date_end >= session["date"]:
                    diff = event_i.event_date_end.date() - session["date"].date()
                    current_status = event_i.event_type + " expires in " + str(diff.days) + " days"
                    break
            people_dict[person] = current_status
        return render_template("create_parties_view.html", people_status=people_dict)

@app.route('/gatherings')
@login_required
def view_parties():
    user_parties = Party.query.filter_by(user_id=session["user_id"]).all()
    party_dict = {}
    for user_party in user_parties:
        party_dict[user_party.host] = [user_party.party_date.strftime('%Y-%m-%d'), user_party.host_email]
    return render_template("invite.html", parties_user=party_dict)


@app.route('/clear_gathering')
@login_required
def clear_gathering():
    session['invites'] = []
    session['date'] = None
    return redirect('/org')

if __name__ == "__main__":
    app.run()


