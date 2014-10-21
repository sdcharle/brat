from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, PostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post, AccessEvent
from datetime import datetime
from config import POSTS_PER_PAGE
from config import USERS_PER_PAGE

from app import babel
from config import LANGUAGES

from guess_language import guessLanguage

from flask import jsonify
from translate import microsoft_translate

from flask.ext.sqlalchemy import get_debug_queries
from config import DATABASE_QUERY_TIMEOUT

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    g.locale = 'en'
# it does this for every damn request
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
    form = PostForm()
    if form.validate_on_submit():
        language = guessLanguage(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        
        post = Post(body = form.post.data,
                    timestamp = datetime.utcnow(),
                    author = g.user,
                    language = language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
        title = 'Home',
        form = form,
        posts = posts)  

@app.route('/user_list', methods = ['GET', 'POST'])
@app.route('/user_list/<int:page>')
@oid.loginhandler
def user_list(page = 1):
  
    users = User.query.order_by(User.nickname)
    users = users.paginate(page, USERS_PER_PAGE, False)
    return render_template('user_list.html',
                           title = "Users",
                           users = users
                           )


@app.route('/access_list/', methods = ['GET', 'POST'])
@app.route('/access_list/<int:page>')
@oid.loginhandler
def access_list(page = 1):
# add, handle 'sailing off edge of world'  
     access_events = AccessEvent.query.order_by(AccessEvent.event_date.desc())
     access_events = access_events.paginate(page, POSTS_PER_PAGE, False)
     print "got some shit"
     return render_template('access_list.html',
                           title = "Accesses",
                           access_events = access_events
                           )

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
 
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None) # hmm what is?
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = user.sorted_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
        user = user,
        posts = posts)


# note add option to edit OTHER users but only if admin
@app.route('/edit', methods = ['GET', 'POST'])
@app.route('/edit/<nickname>', methods = ['GET', 'POST'])
@login_required
def edit(nickname = None): 
#   wait a min. How about if no nick create new dude?
    if not nickname:
        user = User()
#        nickname = g.nickname
    else:
        user = User.query.filter_by(nickname = nickname).first()
        if user == None:
            flash('User ' + nickname + ' not found.')
            return redirect(url_for('index'))    
    
    form = EditForm(user.nickname)
    if form.validate_on_submit():
        user.nickname = form.nickname.data
        user.about_me = form.about_me.data
        user.rfid_access = form.rfid_access.data
        user.rfid_tag = form.rfid_tag.data
 
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_active = form.is_active.data
        
        db.session.add(user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit', nickname = user.nickname))
    else:
        form.nickname.data = user.nickname 
        form.about_me.data = user.about_me 
        form.rfid_access.data = user.rfid_access 
        form.rfid_tag.data = user.rfid_tag
        form.is_active.data = user.is_active
        
    
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        
    return render_template('edit.html',
        form = form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname = nickname))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))


@app.route('/translate', methods = ['POST'])
@login_required
def translate():
    
    return jsonify({ 
        'text': microsoft_translate(
            request.form['text'], 
            request.form['sourceLang'], 
            request.form['destLang']) })

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response
