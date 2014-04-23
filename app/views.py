from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, EditForm
from models import Users, ROLE_USER, ROLE_ADMIN
from pprint import pprint


@lm.user_loader
def load_user(id):

    if id is None or id == 'None':
        id = -1
    print 'ID: %s, leaving load_user' % (id)
    return Users.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    print 'current_user: %s, g.user: %s, leaving bef_req' % (current_user, g.user)


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': 'Sanjeev'},
            'body': 'World is great!'
        },
        {
            'author': {'nickname': 'Yadav'},
            'body': 'India is in this world'
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm
    if request.method == 'GET':
        return render_template('login.html',
                               title='Sign In',
                               form=form)
    username = request.form['username']
    print 'user: %s, leaving login' % (username)
    password = request.form['password']
    print 'password: %s, leaving login' % (password)
    registered_user = Users.query.filter_by(
        username=username, password=password).first()
    print 'registered_user: %s, leaving login' % (registered_user)

    if registered_user is None:
        flash('Username or Password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = Users(
        request.form['username'], request.form['password'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
@login_required
def user(username):
    user = Users.query.filter_by(username=username).first()
    if user == None:

        return redirect(url_for('index'))
    posts = [
        {'user': 'email', 'body': ''},
        {'user': 'age', 'body': '23'},
        {'user': user, 'body': ''}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = EditForm(g.user.username, g.user.password, g.user.email)
    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.password = form.password.data
        g.user.email = form.email.data
        db.session.add(g.user)
        db.session.commit()

        return redirect(url_for('editprofile'))
    elif request.method != "POST":
        form.username.data = g.user.username
        return render_template('editprofile.html',
                               form=form)


@app.route('/follow/<username>')
def follow(username):
    user = Users.query.filter_by(username=username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t friend yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot be friend %(username)s.', username=username)
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now friend with %(nickname)s!', username=username)
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
def unfollow(username):
    user = Users.query.filter_by(username=username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t Unfriend yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot be Unfriend %(username)s.', username=username)
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now Unfriend with %(nickname)s!', username=username)
    return redirect(url_for('user', username=username))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
