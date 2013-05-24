from flask import Blueprint, render_template, session, redirect, url_for, \
    request, flash, g, jsonify, abort
from movietimes.database import Users, ResetTokens
from movietimes.database import UserAlreadyRegistered
from movietimes.forms import LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm
from movietimes import login_manager
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
mod = Blueprint('usermgmt', __name__, template_folder='templates')

#TODOS:
    # send a reset email!!! use the url 'token_url'
    # log out all other sessions when password is changed.
    # salt hash for passwords/logins
    # unit test for forgot/reset/change password flows
    # trap errors in registration (look for "pass")

class User(UserMixin):
    def __init__(self, name, uid, active=True):
        self.name = name
        self.uid = uid
        self.active = active

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.uid
    
    def is_active(self):
        return self.active

@mod.route('/me.json')
def me():
    if current_user.is_anonymous() or not current_user.is_authenticated():
        return jsonify(user=None)
    return jsonify(user=dict(email=current_user.name))

@login_required
@mod.route('/changepw', methods=['GET','POST'])
def change_password():
    if request.method == 'GET':
        return render_template("change_password.html",form=ResetPasswordForm())
    if request.method == 'POST':
        form = ResetPasswordForm(request.form)
        if not form.validate():
            return render_template("change_password.html", form=form)
        Users.reset_password(current_user.get_id(), form.password.data)
        flash('Password has been reset successfully.')
        return redirect(url_for('usermgmt.hello_world'))

@mod.route('/reset/<token>')
def reset(token):
    result = ResetTokens.use_token(token)
    if result:
        dbuser = Users.get_by_email(result['email'])
        user = User(dbuser['email'], dbuser['token'])
        if user and login_user(user, remember=True):
            flash("Logged in!")
            return redirect(url_for('usermgmt.hello_world'))
    else:
        flash('Reset link is incorrect, or it expired - enter your email to get a new link.')
        return forgot()

@mod.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'GET':
        return render_template('forgot.html', form=ForgotPasswordForm())
    if request.method == 'POST':
        form = ForgotPasswordForm(request.form)
        if not form.validate():
            return render_template('forgot.html', form=form)
        token = ResetTokens.setup_forgot_token(form.email.data)
        token_url = url_for('usermgmt.reset', token=token)
        print "reset password url:", token_url
        #TODO - send a reset email!!! use the url 'token_url'
        flash('A link to reset your password has been set to your e-mail address.')
        return redirect(url_for('usermgmt.forgot'))

@mod.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html", form=LoginForm())
    if request.method == "POST":
        form = LoginForm(request.form)
        if not form.validate():
            return render_template("login.html", form=form)

        dbuser = Users.get_by_email_pw(form.email.data, form.password.data)
        user = None
        if dbuser:
            user = User(dbuser['email'], dbuser['token'])

        if user and login_user(user, remember=True):
            flash("Logged in!")
            return redirect(url_for('usermgmt.hello_world'))
            #return render_template("index.html", form=form)
        else:
            form.password.errors.append("Incorrect email/password combination.")
            return render_template("login.html", form=form)
    return render_template("login.html")

@mod.route("/logout")
@login_required
def logout():
    if not current_user.is_anonymous() or current_user.is_authenticated():
        logout_user()
    return redirect(url_for('usermgmt.hello_world'))

@mod.route("/register", methods=["GET","POST"])
def register():
    if not current_user.is_anonymous() and current_user.is_authenticated():
        pass
    if request.method=='GET':
        return render_template("register.html", form=RegisterForm())
    else:
        form = RegisterForm(request.form)
        if not form.validate():
            return render_template("register.html", form=form)
        try:
            new_user = Users.register_user(form.email.data, form.password.data)
            if new_user:
                user = User(new_user['email'], new_user['token'])
                login_result = login_user(user, remember=True)
                if login_result:
                    return redirect(url_for("usermgmt.hello_world"))
                else:
                    pass
            else:
                pass
        except UserAlreadyRegistered:
            form.email.errors.append("This email has already been registered.")
            return render_template("register.html", form=form)

@login_manager.user_loader
def load_user(uid):
    u = Users.get_by_token(uid)
    if u:
        return User(u['email'], u['token'])
