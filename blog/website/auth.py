from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
import random
import string
from flask_mail import  Message
from .models import OTP
from . import mail




auth = Blueprint("auth", __name__)
auth_v2=Blueprint('auth_v2',__name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 3:
            flash("Email is invalid.", category='error')
        else:
            hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(email=email, username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!',category='success')
            return redirect(url_for('views.index'))
        
        
        return render_template("signup.html",user=current_user,email=email,username=username)

    return render_template("signup.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.index"))




def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@auth.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            otp = generate_otp()
            new_otp = OTP(user_id=user.id, otp=otp)
            db.session.add(new_otp)
            db.session.commit()
            
            msg = Message('Password Reset OTP', sender='darkkamal78@gmail.com', recipients=[email])
            msg.body = f'Your OTP is {otp}'
            mail.send(msg)
            
            flash('An OTP has been sent to your email.', category='info')
            return redirect(url_for('auth.verify_otp', user_id=user.id))
        else:
            flash('Email does not exist.', category='error')
    
    return render_template("forgot_password.html")

@auth.route("/verify-otp/<int:user_id>", methods=['GET', 'POST'])
def verify_otp(user_id):
    if request.method == 'POST':
        otp = request.form.get('otp')
        password = request.form.get('password')
        user = User.query.get(user_id)
        otp_record = OTP.query.filter_by(user_id=user_id, otp=otp).first()
        
        if otp_record:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.password = hashed_password
            db.session.delete(otp_record)
            db.session.commit()
            flash('Password reset successful!', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP.', category='error')
    
    return render_template("verify_otp.html")
