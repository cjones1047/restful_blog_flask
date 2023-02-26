from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import os
from datetime import datetime

file_path = os.path.abspath(os.getcwd())+"/posts.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
db = SQLAlchemy(app)

# include CKEditor resources
app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
ckeditor = CKEditor(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])


@app.route('/')
def get_all_posts():
    all_posts = db.session.query(BlogPost).all()

    return render_template("index.html", all_posts=all_posts)


@app.route("/post/<int:index>")
def show_post(index):
    post_to_show = db.session.get(BlogPost, index)

    return render_template("post.html", post=post_to_show)


@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    CreatePostForm.submit = SubmitField("Submit Post")
    form = CreatePostForm()
    if form.validate_on_submit():
        # create Python dictionary from form data
        post_dict = dict(request.form)
        # insert 'date' property into post_dict, since the date of the post should not be edited by the user
        todays_date_formatted = datetime.today().strftime("%B %d, %Y")
        post_dict['date'] = todays_date_formatted
        # remove keys for columns that do not exist in database:
        filtered_post_dict = {key: post_dict[key] for key in post_dict if key in dir(BlogPost)}
        created_post = BlogPost(**filtered_post_dict)
        db.session.add(created_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form)


@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post_to_show = db.session.get(BlogPost, post_id)
    CreatePostForm.submit = SubmitField("Update Post")
    edit_form = CreatePostForm(
        **{
            key: getattr(post_to_show, key) for key in post_to_show.__dict__ if key in dir(BlogPost)
        }
    )
    if edit_form.validate_on_submit():
        print(post_to_show)

    return render_template("make-post.html", form=edit_form, editing=True)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(port=8000, debug=True)
