import flask
import sqlite3

from flask.helpers import url_for
from flask import Flask, redirect, render_template, request, send_file
from flask_paginate import Pagination, get_page_args
from datetime import datetime

import random

app = Flask(__name__, template_folder="templates/", static_folder="")

@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_hash = hash(username)

        con = sqlite3.connect('data/website.db')
        cur = con.cursor()

        cur.execute("SELECT * FROM Users WHERE username='{}';".format(username))
        info = cur.fetchone()

        if info is None: # If the username entered is not found in the database
            return render_template("login.html", message="Please Verify Username")
        else: # If the username is found
            cur.execute("SELECT * FROM Users WHERE username='{}' and password='{}';".format(username, password))
            info = cur.fetchone()
            if info is None: # If the username password combination is not found 
                return render_template("login.html", message="Wrong Password")
            else: # If the username password combination is found 
                user_hash = info[2]
        con.commit()
        con.close()
        return redirect(url_for("feed", user_hash=user_hash))
    else:
        return render_template("login.html", message="")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_hash = hash(username)

        con = sqlite3.connect('data/website.db')
        cur = con.cursor()
        
        cur.execute("SELECT * FROM USERS WHERE username='{}';".format(username))
        info = cur.fetchone()

        if info is not None: # If the username is already taken
            con.commit()
            con.close()            
            return render_template("register.html", message="Username already taken")
        else:  # If the username is not taken
            cur.execute("INSERT INTO users VALUES ('{}','{}','{}');".format(username, password, user_hash))
            con.commit()
            con.close()
            return render_template("login.html", message="Successful, Please Log in")
    else:
        return render_template("register.html", message="")


@app.route('/<user_hash>/feed', methods=['GET', 'POST'])
def feed(user_hash):
    con = sqlite3.connect('data/website.db')
    cur = con.cursor()
    # Get all posts in the database from newest to oldest
    cur.execute("SELECT * FROM POSTS ORDER BY post_time DESC;")
    posts = cur.fetchall()
    if request.method == 'POST': 
        if request.form.get('up'): # if UP is clicked
            post_id = request.form['post_id']
            cur.execute("SELECT * FROM VOTES WHERE voter='{}' and voted_post_id='{}';".format(user_hash, post_id))
            if not cur.fetchone(): # If the user has not voted for this post
                # Add one to up count 
                cur.execute("SELECT up FROM Posts WHERE post_id='{}';".format(post_id))          
                up = cur.fetchone()
                up_count = up[0] + 1
                cur.execute("SELECT post_time FROM Posts WHERE post_id='{}';".format(post_id))
                # get post time
                post_time_tuple = cur.fetchone()
                post_time = post_time_tuple[0]
                # Update the up count right after click the button, otherwise only update after two clicks
                i = 0
                for post in posts:
                    list_post = list(post)
                    if list_post[6] == post_time:
                        list_post[3] = up_count
                        post = tuple(list_post)
                        posts[i] = post
                    i += 1
                cur.execute("UPDATE POSTS SET up = '{}' WHERE post_id = '{}';".format(up_count, post_id))
                cur.execute("INSERT INTO Votes VALUES ('{}','{}');".format(user_hash, post_id))
            else: # If the user has voted for this post
                pass
        elif request.form.get('down'): # if DOWN is clicked
            post_id = request.form['post_id']
            cur.execute("SELECT * FROM VOTES WHERE voter='{}' and voted_post_id='{}';".format(user_hash, post_id))
            if not cur.fetchone(): # If the user has not voted for this post
                cur.execute("SELECT down FROM Posts WHERE post_id='{}';".format(post_id))
                # Add one to down count 
                down = cur.fetchone()
                down_count = down[0] + 1
                cur.execute("SELECT post_time FROM Posts WHERE post_id='{}';".format(post_id))
                # get post time
                post_time_tuple = cur.fetchone()
                post_time = post_time_tuple[0]
                # Update the down count right after click the button, otherwise only update after two clicks
                i = 0
                for post in posts:
                    list_post = list(post)
                    if list_post[6] == post_time:
                        list_post[4] = down_count
                        post = tuple(list_post)
                        posts[i] = post
                    i += 1
                cur.execute("UPDATE POSTS SET down = '{}' WHERE post_id = '{}';".format(down_count, post_id))
                cur.execute("INSERT INTO Votes VALUES ('{}','{}');".format(user_hash, post_id))
            else:
                pass
    con.commit()
    con.close()

    # Pagnition
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', per_page=5)
    total = len(posts)
    pagination_posts = posts[offset: offset + 5]
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template("feed.html", title="Feed", posts=pagination_posts, user_hash=user_hash,  pagination=pagination)


@app.route('/<user_hash>/create', methods=['GET', 'POST'])
def create(user_hash):
    con = sqlite3.connect('data/website.db')
    cur = con.cursor()
    cur.execute("SELECT username FROM USERS WHERE user_hash='{}';".format(user_hash))
    username_tuple = cur.fetchone()
    username = str
    username = username_tuple[0]

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        up = 0
        down = 0
        now = datetime.now()
        post_time = now.strftime("%Y-%m-%d %H:%M:%S")
        post_id = hash(post_time)
        cur.execute("INSERT INTO Posts VALUES ('{}','{}','{}','{}','{}','{}','{}','{}');".format(post_id, title, content, up, down, user_hash, post_time, username))
        con.commit()
        con.close()
        return redirect(url_for("myposts", user_hash=user_hash))
    else:
        return flask.render_template("create.html", title="create", user_hash=user_hash, username=username)
    

@app.route('/<user_hash>/myposts', methods=['GET', 'POST'])
def myposts(user_hash):
    con = sqlite3.connect('data/website.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM POSTS WHERE user_hash='{}' ORDER BY post_time DESC;".format(user_hash))
    posts = cur.fetchall()
    if request.method == 'POST':
        if request.form.get('delete'):
            post_id = request.form['post_id']
            cur.execute("SELECT post_time FROM Posts WHERE post_id='{}';".format(post_id))
            post_time_tuple = cur.fetchone()
            post_time= post_time_tuple[0]
            # Make post disapear right away after clicking
            i = 0
            for post in posts:
                if post[6] == post_time:
                    posts.pop(i)
                i += 1
            cur.execute("DELETE FROM POSTS WHERE post_id ='{}';".format(post_id))
    con.commit()
    con.close()

    # Pagnition
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', per_page=5)
    total = len(posts)
    pagination_posts = posts[offset: offset + 5]
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template("myposts.html", title="myposts", posts=pagination_posts, user_hash=user_hash, pagination=pagination)

@app.route('/<user_hash>/myprofile', methods=['GET'])
def myprofile(user_hash):
    return render_template("myprofile.html")

@app.route('/<user_hash>/aboutme', methods=['GET'])
def aboutme(user_hash):
    return render_template("aboutme.html")

@app.route('/<user_hash>/contact', methods=['GET'])
def contact(user_hash):
    return render_template("contact.html")

@app.route('/posts/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    con = sqlite3.connect('data/website.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM POSTS WHERE post_id='{}';".format(post_id))
    post = cur.fetchone()
    user_hash = post[5]
    cur.execute("SELECT username FROM USERS WHERE user_hash='{}';".format(user_hash))
    username_tuple = cur.fetchone()
    username = ''
    username = username_tuple[0]
    con.commit()
    con.close()
    return render_template("post.html", post=post, username=username, user_hash=user_hash)



if __name__=='__main__':
    app.run(debug=True, host="0.0.0.0",port=3000)

