from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, EditForm
from models import Users, ROLE_USER, ROLE_ADMIN, bestfriend
from sqlalchemy.sql.expression import select, exists
from sqlalchemy import exc


@lm.user_loader
def load_user(id):

    if id is None or id == 'None':
        id = -1
    
    return Users.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    


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
    
    password = request.form['password']
    
    registered_user = Users.query.filter_by(
        username=username, password=password).first()
    

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
    users = Users.query.all()
    #bestfriendsval = Users.query.filter_by(bestfriend.c.id)
    
    if user == None:

        return redirect(url_for('index'))
    posts = [
        {'user': 'email', 'body': ''},
        {'user': 'age', 'body': '23'},
        {'user': user, 'body': ''}
    ]
    return render_template('user.html',
                           user=user,
                           users=users,
                           #bestfriendsval=bestfriendsval,
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
    #user = Users.query.all()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t friend yourself!')
        return redirect(url_for('user', username=username))
    # for userid in user:
    
    u = g.user.follow(user)
    
    if u is None:
        #flash('Cannot be friend %(username)s.', username = username)
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    #flash('You are now friend with %(username)s!', username = username)
    return redirect(url_for('user', username=username))


@app.route('/bestfriend/<username>')
@login_required
def bestfriendfun(username):
    print username
    user = Users.query.filter_by(username=username).first()
    if user == None:
        flash('bestfriend not found.')
        return redirect(url_for('index'))
    print user
    u = g.user.friend(user)
    
    if u is None:
        #flash('Cannot be friend %(username)s.', username = username)
        return redirect(url_for('user', username=username))
    
    try:
        db.session.add(u)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        flash('you already have best friend')
    except:
        flash('There is some issue in adding best friend')
        raise
    else:
        flash('Your bestfriend has been added.')
    return redirect(url_for('user', username=username))


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    
    user = Users.query.get(id)
    if user == None:
        flash('user not found.')
        return redirect(url_for('index'))

    db.session.delete(user)
    db.session.commit()
    flash('Your user has been deleted.')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
