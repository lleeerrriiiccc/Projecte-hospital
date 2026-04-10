import flask
import os
from flask import Flask
from flask import request, redirect, url_for, send_from_directory, render_template, make_response
import tools.manager as m
from flask import Flask, jsonify, request
import jwt
import datetime
import datetime



############
# APP CONFIG
############
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))
app = Flask(__name__, template_folder=template_dir)



############
# JWT TOKEN
############
app.secret_key = os.environ.get('FLASK_SECRET')
app.config.update(
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE='Lax')



############
# STATIC FILES
############
@app.route('/css/<path:filename>')
def css(filename):
    css_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'css'))
    return send_from_directory(css_dir, filename)



############
# MAIN ROUTE
############
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return redirect(url_for('login'))
    



############
# LOGIN ROUTE
############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if m.login(username, password):
        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        resp = make_response(redirect(url_for('dashboard')))
        resp.set_cookie(
            "token",
            token,
            httponly=True,
            samesite="Strict"
        )
        return resp

    return redirect(url_for('login'))
        



############
# HOME ROUTE
############
@app.route('/home')
def home():
    return render_template('home.html') 



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')