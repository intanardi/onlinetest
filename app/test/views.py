from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from . import candidate
from .forms import CandidateForm, LoginForm
from .. import db
from ..models import User, Role, Candidate
from flask_paginate import Pagination, get_page_parameter
import json

ROWS_PER_PAGE = 3

@candidate.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role_id not in [1,2]:
            return redirect(url_for('candidate.home'))
        return redirect(url_for('user.index'))
    form = LoginForm()
    if request.method == 'POST':
        print("nyahaha")
        user = Candidate.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or pasword")
            return redirect(url_for('candidate.login'))
        login_user(user)
        return redirect(url_for('candidate.home'))
    return render_template('candidate/login.html', form=form)

@candidate.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@login_required
@candidate.route('/home', methods=['GET', 'POST'])
def home():
    return "home"

@login_required
@candidate.route('/', methods=['GET', 'POST'])
@candidate.route('/index', methods=['GET', 'POST'])
def index():
    _keyword = ""
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    if request.method == "POST":
        _keyword= request.form['keyword']
    _search = "%{}%".format(_keyword)
    page = request.args.get('page', 1, type=int)
    total_rows = User.query.filter(User.role_id.in_(["3"]), User.status.is_(True), User.fullname.like(_search)).count()
    boxsize = 3
    num_pages = -(total_rows // -boxsize)
    candidates = User.query.filter(User.role_id.in_(["3"]), User.status.is_(True), User.fullname.like(_search)).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('candidate.index', page=candidates.next_num) \
        if candidates.has_next else None
    prev_url = url_for('candidate.index', page=candidates.prev_num) \
        if candidates.has_prev else None
    return render_template('candidate/index.html', candidates=candidates.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages))
    
@login_required
@candidate.route('/add', methods=['GET', 'POST'])
def add():
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    form = CandidateForm()
    if request.method == 'POST':
        print("submitted")
        candidate = User()
        if request.form['password'] != request.form['repassword']:
            flash("Confirmation password sshould be a same")
            return redirect(url_for('candidate.add'))
        candidate.username = request.form['username']
        candidate.email = request.form['email']  
        candidate.fullname = request.form['fullname']
        candidate.phone = request.form['phone'] 
        candidate.address = request.form['address'] 
        candidate.set_password(request.form['password'] )
        db.session.add(candidate)
        db.session.commit()
        return redirect(url_for('candidate.index'))
        
    return render_template('candidate/add.html', form=form)

@login_required
@candidate.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    form = CandidateForm()
    candidate = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        candidate.username = request.form['username']
        candidate.email = request.form['email']  
        candidate.fullname = request.form['fullname']
        candidate.phone = request.form['phone'] 
        candidate.address = request.form['address']
        db.session.add(candidate)
        db.session.commit()
        return redirect(url_for('candidate.index'))
    return render_template('candidate/edit.html', candidate=candidate, form=form)

@login_required
@candidate.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    candidate = User.query.filter_by(id=id).first()
    candidate.status = False
    db.session.add(candidate)
    db.session.commit()
    return redirect(url_for('user.index'))