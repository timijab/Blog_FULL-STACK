import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
# flask_ckeditor uses:
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

## Delete this code:
import requests

# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    # this is where i want my ckeditor to come up at
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    posts = BlogPost.query.all()
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/edit/<post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    all_posts = BlogPost.query.all()
    form = CreatePostForm()
    date = ''
    if request.method == 'GET':
        for post in all_posts:
            if int(post.id) == int(post_id):
                date += post.date
                # prepolulating the form with the data in the database so user doesnt have to start form the begining
                form = CreatePostForm(
                    title=post.title,
                    subtitle=post.subtitle,
                    img_url=post.img_url,
                    author=post.author,
                    body=post.body
                )
        return render_template("make-post.html", tag='Edit Post', form=form)
    elif request.method == 'POST':
        for post in all_posts:
            if int(post.id) == int(post_id):
                post.title = form.title.data
                post.subtitle = form.subtitle.data
                post.img_url = form.img_url.data
                post.author = form.author.data
                post.body = form.body.data

            db.session.commit()
        return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/new-post", methods=['POST', 'GET'])
def create_new():
    # ckeditor is an integration for flask, to add support to image upload, code syntax, highlighting and more.
    #  ckeditor needs to be added to form.
    form = CreatePostForm()
    if request.method == 'GET':
        return render_template("make-post.html", form=form)
    else:
        # go straight and assign values to the db.
        new_blog = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('get_all_posts'))


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/delete/<int:post_id>')
def delete(post_id):
    all_post = BlogPost.query.all()
    for post in all_post:
        if int(post.id) == int(post_id):
            db.session.delete(post)
            db.session.commit()
    return redirect(url_for('get_all_posts'))



if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
