from application import app
from application.models.user_item_model import UserItem
from application.models.users_model import User
from flask import render_template, redirect, request, session, flash

def invalidCreds():
    flash('Invalid credentials', 'error_login_inv_creds')
    return redirect('/login')

@app.route('/login')
def showLoginPage():
    if 'logged_user' not in session:
        return render_template('login.html')
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/login/process_login', methods=['POST'])
def processLogin():
    login_token = User.validateLogin(request.form)
    if not login_token:
        return invalidCreds()
    session['logged_user'] = login_token
    return redirect(f'/users/dashboard/{login_token}')

@app.route('/login/process_registration', methods=['POST'])
def processRegistration():
    if User.validateRegist(request.form):
        new_user = User.registerNewUser(request.form)
        if new_user:
            session['logged_user'] = new_user
            return redirect(f'/users/dashboard/{new_user}')
    return redirect('/login')

@app.route('/users/dashboard/<int:id>')
def showDashboard(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if id != session['logged_user']:
        return redirect('/login')
    current_user = User.getUser(id=id)
    all_items = UserItem.getAllItems()
    return render_template('dashboard.html', user=current_user, items=all_items)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')