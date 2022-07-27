from flask import Flask, redirect, session
app = Flask(__name__)
app.secret_key = 'l0lh@x'

DATABASE = 'recipesdb'

@app.route('/')
def index():
    if 'logged_user' not in session:
        return redirect('/login')
    return redirect(f"/users/{session['logged_user']}/dashboard")