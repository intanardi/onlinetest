from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from . import user
from .forms import UserForm, LoginForm
from .. import db, csrf
from ..models import *
import json

ROWS_PER_PAGE = 5
PERMISSION_LIST = [1,2]

@user.route('/')
@user.route('/index', methods=['POST', 'GET'])
@csrf.exempt
@login_required
def index():
    _keyword = ""
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('question.home'))
    if request.method == "POST":
        _keyword= request.form['keyword']
    _search = "%{}%".format(_keyword)
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 2))
    total_rows = User.query.filter(User.role_id.in_(PERMISSION_LIST),User.fullname.like(_search) ,User.status.is_(True)).count()
    boxsize = ROWS_PER_PAGE
    num_pages = -(total_rows // -boxsize)
    users = User.query.filter(User.role_id.in_(PERMISSION_LIST),User.fullname.like(_search) ,User.status.is_(True)).order_by(User.id).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('user.index', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('user.index', page=users.prev_num) \
        if users.has_prev else None
    return render_template('admin/user/index.html', users=users.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages))

@user.route('/add', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def add():
    if current_user.role_id not in PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('user.index'))
    form = UserForm()
    roles = Role.query.all()
    divisions = Division.query.all()
    levels = Level.query.all()
    if request.method == 'POST':
        print(request.form)
        user = User()
        user.role_id = int(request.form['roles'])
        user.division_id = int(request.form['division'])
        user.level_id = int(request.form['level'])
        user.username = request.form['username']
        user.email = request.form['email']  
        user.fullname = request.form['fullname']
        user.phone = request.form['phone'] 
        user.address = request.form['address']
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.index'))
        
    return render_template('admin/user/add.html', form=form, roles=roles, divisions=divisions, levels=levels)

@login_required
@user.route('/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
def edit(id):
    if current_user.role_id not in PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('user.index'))
    form = UserForm()
    user = User.query.filter_by(id=id).first()
    roles = Role.query.all()
    divisions = Division.query.all()
    levels = Level.query.all()
    if request.method == 'POST':
        print(request.form)
        if  'roles' in request.form:
            user.role_id = int(request.form['roles'])
        if  'division' in request.form:
            user.division_id = int(request.form['division'])
        if  'level' in request.form:
            user.level_id = int(request.form['level'])
        user.username = request.form['username']
        user.email = request.form['email']  
        user.fullname = request.form['fullname']
        user.phone = request.form['phone'] 
        user.address = request.form['address'] 
        # user.role_id = int(request.form['roles'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('admin/user/edit.html', form=form, user=user, roles=roles, divisions=divisions, levels=levels)

@login_required
@user.route('/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
def delete(id):
    if current_user.role_id not in PERMISSION_LIST:
        flash("You have no permision!")
        return redirect(url_for('candidate.index'))
    if current_user.role_id != 1:
        flash("You have no permision!")
        return redirect(url_for('user.index'))
    user = User.query.filter_by(id=id).first()
    user.status = False
    db.session.add(user)
    # db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user.index'))
