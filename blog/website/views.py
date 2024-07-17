from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required,current_user
from .models import Post, User, Comment, Like
from . import db
from faker import Faker
import os

views = Blueprint("views", __name__)
fake=Faker()

@views.route("/")
@views.route("/home")
@login_required
def index():
    posts = Post.query.all()
    if not posts:
        for _ in range(10):
            fake_post = Post(
                text=fake.paragraph(nb_sentences=5),
                author=fake.random_int(min=1, max=10)
            )
            db.session.add(fake_post)
        db.session.commit()
        posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.index'))

    return render_template('create_post.html', user=current_user)



@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.index'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.index'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.index'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.index'))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author_id=current_user.id, post_id=post_id).first()

    if not like:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
    else:
        db.session.delete(like)

    db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_update():
   if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        age = request.form['age']
        
    
        if 'profile-upload' in request.files:
            file = request.files['profile-upload']
            if file.filename != '':
                
                file.save(os.path.join('website', 'static', 'profile_picture.jpg'))
                current_user.profile_picture = file.read()
        

        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        current_user.gender = gender
        current_user.age = age
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('views.index'))
   
   return render_template('profile.html', user=current_user)