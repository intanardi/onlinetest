from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request, current_app
from flask_login import login_required, login_user, logout_user, current_user
from . import question
from .. import db, csrf
from ..models import Multiple_Choice, User, Role, Question, Division, Level
import json

ROWS_PER_PAGE = 3

@login_required
@question.route('/home', methods=['GET', 'POST'])
def home():
    return "home"

@login_required
@question.route('/', methods=['GET', 'POST'])
@question.route('/index', methods=['GET', 'POST'])
@csrf.exempt
def index():
    _keyword = ""
    # _example = Question().data_list(1)
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('question.home'))
    if request.method == "POST":
        _keyword= request.form['keyword']
    _search = "%{}%".format(_keyword)
    page = request.args.get('page', 1, type=int)
    total_rows = Question.query.filter(Question.status.is_(True)).count()
    boxsize = 3
    num_pages = -(total_rows // -boxsize)
    question = Question.query.filter(Question.status.is_(True)).paginate(page=page, per_page=ROWS_PER_PAGE)
    next_url = url_for('question.index', page=question.next_num) \
        if question.has_next else None
    prev_url = url_for('question.index', page=question.prev_num) \
        if question.has_prev else None
    return render_template('question/index.html', quetions=question.items, prev_url=prev_url, next_url=next_url, num_pages=int(num_pages))
    
@login_required
@question.route('/add', methods=['GET', 'POST'])
@csrf.exempt
def add():
    # Check If user role is superadmin or admin
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    
    # get all data from database
    divisions = Division.query.all()
    levels = Level.query.all()
    if request.method == 'POST':
        # set variable to false
        is_multiple = False
        # check if form post got an answer list choice
        check_multiple_choices = request.form.getlist('answer[]')
        if check_multiple_choices:
            # if have a list set variable to true
            is_multiple = True
        question = Question()
        question.name = request.form['name']
        question.question_division_id = request.form['division']  
        question.question_level_id = request.form['level']
        question.question = request.form['question']
        question.is_multiple_choice = is_multiple
        db.session.add(question)
        db.session.commit()
        if is_multiple:
            for i in check_multiple_choices:
                mc = Multiple_Choice()
                mc.name = i
                mc.question_id = question.id
                db.session.add(mc)
                db.session.commit()
        # return "halo"
        return redirect(url_for('question.index'))
        
    return render_template('question/add.html', levels=levels, divisions=divisions)

@login_required
@question.route('/edit/<id>', methods=['GET', 'POST'])
@csrf.exempt
def edit(id):
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    question = Question.query.filter_by(id=id).first()
    if request.method == 'POST':
        question.username = request.form['username']
        question.email = request.form['email']  
        question.fullname = request.form['fullname']
        question.phone = request.form['phone'] 
        question.address = request.form['address']
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('question.index'))
    return render_template('question/edit.html', question=question, form=form)

@login_required
@question.route('/delete/<id>', methods=['GET', 'POST'])
@csrf.exempt
def delete(id):
    if current_user.role_id not in [1,2]:
        flash("You have no permision!")
        return redirect(url_for('candidate.home'))
    question = User.query.filter_by(id=id).first()
    question.status = False
    db.session.add(question)
    db.session.commit()
    return redirect(url_for('question.index'))