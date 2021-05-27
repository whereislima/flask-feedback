from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "mangopudding"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register_user():

    form = RegisterForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        flash('Successfully created your account')
        return redirect(f"/users/{user.username}")
    else:
        flash("failed")
        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_user():

    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password']

        return render_template("login.html", form=form)

@app.route("/users/<username>")
def secret(username):
    
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    all_feedback = Feedback.query.all()

    return render_template("users/detail.html", user=user, all_feedback=all_feedback)
    

@app.route("/logout")
def logout():
    session.pop('username')
    return redirect("/")

@app.route("/users/<username>/delete")
def delete_user(username):

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    db.session.commit.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{feedback.username}")

    return render_template("users/add_feedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    
    return ("update")

@app.route("/feedback/<int:feedback_id>/delete", methods=["GET", "POST"])
def delete_feedback(feedback_id):

    return ("delete")