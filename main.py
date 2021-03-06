from flask import Flask, render_template, request, abort, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import marshal_with, Api, Resource, fields
import sqlite3
from flask_login import login_user, current_user, logout_user, login_required, LoginManager, UserMixin


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "mysecretkey"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'
login_manager.login_message_category = 'danger'


class UserModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(100), unique=True)
    upasswd = db.Column(db.String(100), nullable=False)

    # Flask-Login integration
    # def is_authenticated(self):
    #     return True
    #
    # def is_active(self):  # line 37
    #     return True
    #
    # def is_anonymous(self):
    #     return False
    #
    # def get_id(self):
    #     return self.id
    #
    # # Required for administrative interface
    # def __unicode__(self):
    #     return self.uname

    def __repr__(self):
        return f"User(uname={self.uname}, upasswd={self.upasswd})"


# @login_manager.user_loader
# def load_user(user_id):
#     # since the user_id is just the primary key of our user table, use it in the query for the user
#     try:
#         return UserModel.query.filter(id=user_id).first()
#     except:
#         return None

@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


resource_fields = {
    'id': fields.Integer,
    'uname': fields.String,
    'upasswd': fields.String
}


class CreateEvent(db.Model):
    ename = db.Column(db.String(500), primary_key=True)
    etype = db.Column(db.String(500), nullable=False)
    eloc = db.Column(db.String(200), nullable=False)
    sdate = db.Column(db.String(100), nullable=False)
    edate = db.Column(db.String(100), nullable=False)
    creator = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'''CreateEvent(ename={self.ename}, etype={self.etype}, eloc={self.eloc}, sdate={self.sdate}, edate={self.edate}, creator={self.creator})'''

resource_fields1 = {

    'ename': fields.String,
    'etype': fields.String,
    'eloc': fields.String,
    'sdate': fields.String,
    'edate': fields.String,
    'creator': fields.String
}



# def dbcondec(dbcon):
#     global con, user_list, cur, cur2, event_list
#     def wrapper():
#         with sqlite3.connect('mydb.db', check_same_thread=False, timeout=10) as con:
#             cur = con.cursor()
#             cur2 = con.cursor()
#             cur.execute("SELECT * FROM create_event;")
#             event_list = cur.fetchall()
#             cur2.execute("SELECT * FROM user_model;")
#             user_list = cur2.fetchall()
#         val = dbcon()
#         cur.close()
#         cur2.close()
#         return val
#     return wrapper




@app.route('/register')
def register():
    return render_template('registerpage.html')


@app.route('/')
def loginpage():
    return render_template('loginpage.html')


@app.route('/main')
@login_required
def main():
    if current_user.is_authenticated:
        con = sqlite3.connect('mydb.db')
        cur = con.cursor()
        cur2 = con.cursor()
        cur.execute("SELECT * FROM create_event;")
        event_list = cur.fetchall()
        cur2.execute("SELECT * FROM user_model;")
        user_list = cur2.fetchall()
        query = UserModel.query.filter_by(uname=current_user.uname).first()
        if query:
            return render_template('mainpage.html', content=current_user.uname, data=event_list, data2=user_list)
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))


@app.route('/submitaction', methods=["GET", "POST"])
# @marshal_with(resource_fields)
def submitact():
    con = sqlite3.connect('mydb.db')
    cur = con.cursor()
    cur2 = con.cursor()
    cur.execute("SELECT * FROM create_event;")
    event_list = cur.fetchall()
    cur2.execute("SELECT * FROM user_model;")
    user_list = cur2.fetchall()
    if request.method == "POST":
        usrname = request.form["username"]
        passwd = request.form["passwd"]
        query = UserModel.query.filter_by(uname=usrname).first()
        if query:
            if query.upasswd == passwd:
                session["user"] = query.uname
                print(type(query))
                login_user(query)
                return render_template('mainpage.html', content=session['user'], data=event_list, data2=user_list)
            else:
                abort(403, "Password is wrong! Please Check!")
        else:
            flash(f'''Unknown User, Please register first!''', 'danger')
            return redirect(url_for('loginpage'))
            # abort(403, "Register First!")

    return redirect(url_for('loginpage'))


@app.route('/registeraction', methods=["POST"])
# @marshal_with(resource_fields)
def registeraction():
    db.create_all()
    reguname = request.form["username"]
    upwd = request.form["passwd"]
    mpwd = request.form["repasswd"]
    if str(upwd) != str(mpwd):
        flash(f'''Passwords do not match , Please Check''', 'danger')
        return redirect(url_for('register'))
    else:
        oname = UserModel.query.filter_by(uname=reguname).first()
        if oname:
            flash(f'''User Already Exists , Please Sign-in''', 'info')
            return redirect(url_for('loginpage'))
        else:
            my_data = UserModel(uname=reguname, upasswd=upwd)
            db.session.add(my_data)
            db.session.commit()
            flash(f'''User Successfully Registered , Please Sign-in''', 'success')
            return redirect(url_for('loginpage'))


@app.route('/registerevent')
def registerevent():
    return render_template('eventform.html', content=session['user'])


@app.route('/createevent', methods=["POST"])
def createevent():
    db.create_all()
    if request.method == "POST":
        evename = request.form["ename"]
        evetype = request.form["etype"]
        eveloc = request.form["eloc"]
        sevedate = request.form["edate"]
        eevedate = request.form["ddate"]
        my_query = CreateEvent.query.filter_by(ename=evename).first()
        if my_query:
            flash(f'''Event name already exists!''', 'info')
            return redirect(url_for('registerevent'))
        else:
            m_data = CreateEvent(ename=evename, etype=evetype, eloc=eveloc, sdate=sevedate, edate=eevedate, creator=current_user.uname)
            db.session.add(m_data)
            db.session.commit()
            con = sqlite3.connect('mydb.db')
            cur = con.cursor()
            cur2 = con.cursor()
            cur.execute("SELECT * FROM create_event;")
            cur2.execute("SELECT * FROM user_model;")
            event_list = cur.fetchall()
            user_list = cur2.fetchall()
            flash(f'''Event Created Successfully!''', 'success')
            return render_template("mainpage.html", data=event_list, data2=user_list)


@app.route('/userevents')
def userevents():
    cur_user = session["user"]
    con = sqlite3.connect('mydb.db')
    cur = con.cursor()
    cur2 = con.cursor()
    cur.execute("SELECT * FROM create_event WHERE creator='"+cur_user+"';")
    usere_list = cur.fetchall()
    cur2.execute("SELECT * FROM user_model;")
    user_list = cur2.fetchall()
    return render_template('userregevent.html', content=cur_user, data=usere_list, data2=user_list)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash(f'''User signed out successfully!''', 'success')
    return redirect(url_for('loginpage'))


@app.errorhandler(403)
def forbiddenerror(e):
    return "Access is denied!"


@app.errorhandler(404)
def resourceerror(e):
    return "Page not found!"


if __name__ == "__main__":
    app.run(debug=True)

