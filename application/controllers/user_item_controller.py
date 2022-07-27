from application import app
from application.models.users_model import User
from application.models.user_item_model import UserItem
from flask import render_template, redirect, request, session, flash

@app.route('/items/<int:id>')
def showItem(id):
    current_user = User.getUser(id=session['logged_user']) if 'logged_user' in session else False
    current_item = UserItem.getItem(id)
    return render_template('items.html', user=current_user, item=current_item)

@app.route('/items/new')
def createItem():
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.getUser(id=session['logged_user'])
    return render_template('new_item.html', user=current_user)

@app.route('/items/new/create', methods=['POST'])
def createNewItem():
    if 'logged_user' not in session:
        return redirect('/login')
    if UserItem.validateCreateItem(request.form):
        new_item_data = {
            **request.form,
            'user_id' : session['logged_user']
        }
        new_item = UserItem.createNewItem(new_item_data)
        return redirect(f"/users/dashboard/{session['logged_user']}")
    return redirect('/items/new')

@app.route('/items/edit/<int:id>')
def displayEditPage(id):
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.getUser(id=session['logged_user'])
    item = UserItem.getItem(id)
    if session['logged_user'] == item.user_id:
        return render_template('edit_item.html', user=current_user, item=item)
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/items/edit/<int:id>/process', methods=['POST'])
def editItem(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if session['logged_user'] == UserItem.getItem(id).user_id:
        new_info = {
            **request.form,
            'id' : id,
            'user_id' : session['logged_user']
        }
        if not UserItem.validateCreateItem(new_info):
            return redirect(f'/items/edit/{id}')
        rslt = UserItem.updateItem(new_info)
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/items/destroy/<int:id>')
def deleteItem(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if session['logged_user'] == UserItem.getItem(id).user_id:
        rslt = UserItem.deleteItem(id)
    return redirect(f"/users/dashboard/{session['logged_user']}")