from flask_login.utils import _secret_key
from sqlalchemy.orm import backref
from app import create_app, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask_login import login_required
from datetime import datetime

_secret_key_mine = "dnsia129eGH1092dnsua81ainfia18ecdsn382r76dsnkudsay"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# @app.route('/secret')
# @login_required
# def secret():
#     return 'Only authenticated users are allowed!'

class Role(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
    
    @staticmethod
    def insert_static_data():
        values = [
            { 
            "id" : "1",
            "name" : "superadmin" },
            { 
            "id" : "2",
            "name" : "admin" },
            { 
            "id" : "3",
            "name" : "candidate" }
            ]
        for v in values:
            role = Role()
            role.id = v['id']
            user.name = v['name']
            db.session.add(role)
            db.session.commit()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(128))
    email = db.Column(db.String(64))
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(128))
    phone = db.Column(db.String(15))
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=3)
    added_time = db.Column(db.Date())
    last_login = db.Column(db.DateTime())
    is_deleted = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)
    
    # Candidate_Psikotest_Schedules = db.relationship('Candidate_Psikotest_Schedule', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def insert_static_data():
        values = [
            { "email" : "ardibatio@gmail.com", "username" :"ardipramanova", "password": "123456", "role_id": 2 }
            ]
        for v in values:
            user = User()
            user.username = v['username']
            user.password_hash = generate_password_hash(v['password'])
            user.email = v['email']
            user.role_id = v['role_id']
            db.session.add(user)
            db.session.commit()
    
    def insert_data(self, data):
        user = User()
        user.email = data['email']
        user.username = data['username']
        password_hashed = generate_password_hash(str(data['password'])+_secret_key_mine)
        # check = check_password_hash(nyanya, str(data['password'])+_secret_key_mine)
        user.email = data['email']
        user.password = password_hashed
        user.role_id = data['role']
        db.session.add(user)
        db.session.commit()
        return "00"
    
    def data_list():
        _dict = []
        user = User.query.filter_by(role_id=3).all()
        for u in user:
            schedule = "Not Set"
            schedule_status = 0
            get_schedule = Candidate_Test_Schedule.query.filter_by(candidate_id=u.id).first()
            if get_schedule is not None :
                schedule = get_schedule.date_test
                schedule_status = 1
            _dict.append({"name" : u.fullname, "email" : u.email,"phone" : u.phone, "address" : u.address, "status": schedule_status, "schedule": schedule, "division" : u.division.name, "level" : u.level.name})
        
        return _dict

class Level(db.Model):
    __tablename__ = "level"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    is_deleted = db.Column(db.Boolean, default=False)
    examinations = db.relationship('Examination', backref='level', lazy='dynamic')
    users = db.relationship('User', backref='level', lazy='dynamic')

    def __repr__(self):
        return '<Question_Level %r>' % self.name
    
    @staticmethod
    def insert_static_data():
        values = ['Staff', 'Senior', 'SPV']
        for v in values:
            level = Level()
            level.name = v
            db.session.add(level)
            db.session.commit()

class Division(db.Model):
    __tablename__ = "division"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    is_deleted = db.Column(db.Boolean, default=False)
    examinations = db.relationship('Examination', backref='division', lazy='dynamic')
    users = db.relationship('User', backref='division', lazy='dynamic')

    def __repr__(self):
        return '<Division %r>' % self.name
    
    @staticmethod
    def insert_static_data():
        values = ['Accounting', 'Audit' , 'Legal', 'HR', 'IT',]
        for v in values:
            division = Division()
            division.name = v
            db.session.add(division)
            db.session.commit()

class Examination(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    duration = db.Column(db.Time)
    timedelta_duration = db.Column(db.Float)
    is_deleted = db.Column(db.Boolean, default=False)
    questions = db.relationship('Question', backref='examination', lazy='dynamic')
    choices = db.relationship('Multiple_Choice', backref='examination', lazy='dynamic')
    pdfs = db.relationship('Examination_Detail', backref='examination', lazy='dynamic')
    
    def __repr__(self):
        return '<Examination %r>' % self.name

class Examination_Detail(db.Model):
    __tablename__ = "examination_detail"
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(128))
    name = db.Column(db.String(128))
    duration = db.Column(db.Time())
    timedelta_duration = db.Column(db.Float)
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'))
    is_deleted = db.Column(db.Boolean, default=False)
    Candidate_Main_Schedules = db.relationship('Candidate_Main_Schedule', backref='examination_detail', lazy='dynamic')
    
    def __repr__(self):
        return '<Examination_Detail %r>' % self.name

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.Text())
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'))
    is_deleted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '<Question %r>' % self.name

class Multiple_Choice(db.Model):
    __tablename__ = "multiple_choice"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    examination_id = db.Column(db.Integer, db.ForeignKey('examination.id'))
    is_correct = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '<Multiple_Choice %r>' % self.name

# ======================= STATIC MODELS =============================

class Psikotest_Type(db.Model):
    __tablename__ = "psikotest_type"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    preliminary = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)
    psikotests = db.relationship('Psikotest', backref='psikotest_type', lazy='dynamic')

    def __repr__(self):
        return '<Psikotest_Type %r>' % self.name
    
    @staticmethod
    def insert_static_data():
        values = ['CFIT', 'WPT']
        for v in values:
            pt = Psikotest_Type()
            pt.name = v
            db.session.add(pt)
            db.session.commit()

class Psikotest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    test_filename = db.Column(db.String(128))
    instruction_filename = db.Column(db.String(128))
    alert = db.Column(db.String(128))
    psikotest_type_id = db.Column(db.Integer, db.ForeignKey('psikotest_type.id'))
    duration = db.Column(db.Time())
    timedelta_duration = db.Column(db.Float)
    is_deleted = db.Column(db.Boolean, default=False)
    Candidate_Psikotest_Schedules = db.relationship('Candidate_Psikotest_Schedule', backref='psikotest', lazy='dynamic')
    
    def __repr__(self):
        return '<Psikotest %r>' % self.instruction_filename
    
    @staticmethod
    def insert_static_data():
        values = [
            { "filename" : "soal_cfit.pdf", "instruction" : "SIlahkan Baca Instruksi Lembar soal !", "psikotest_type_id": 1 },
            { "filename" : "soal_wpt.pdf", "instruction" : "SIlahkan Baca Instruksi Lembar soal !", "psikotest_type_id": 2 }
            ]
        for v in values:
            p= Psikotest()
            p.filename = v['filename']
            p.instruction = v['instruction']
            p.psikotest_type_id = v['psikotest_type_id']
            db.session.add(p)
            db.session.commit()

class Candidate_Test_Schedule(db.Model):
    __tablename__ = "candidate_test_schedule"
    id = db.Column(db.Integer, primary_key = True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_test = db.Column(db.DateTime())
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Candidate_Test_Schedule %r>' % self.date_test

class Candidate_Psikotest_Schedule(db.Model):
    __tablename__ = "candidate_psikotest_schedule"
    id = db.Column(db.Integer, primary_key = True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    psikotest_id = db.Column(db.Integer, db.ForeignKey('psikotest.id'))
    started_time = db.Column(db.DateTime())
    status = db.Column(db.Boolean, default=False)
    flag = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Candidate_Psikotest_Schedule %r>' % self.candidate_id

class Candidate_Main_Schedule(db.Model):
    __tablename__ = "candidate_main_schedule"
    id = db.Column(db.Integer, primary_key = True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    division_test_id = db.Column(db.Integer, db.ForeignKey('examination_detail.id'))
    started_time = db.Column(db.DateTime())
    status = db.Column(db.Boolean, default=False)
    flag = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Candidate_Main_Schedule %r>' % self.candidate_id

class Test_Type(db.Model):
    __tablename__ = "test_type"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    is_deleted = db.Column(db.Boolean, default=False)

    @staticmethod
    def insert_static_data():
        values = ['psikotest', 'main test']
        for v in values:
            gs = Test_Type()
            gs.name = v
            db.session.add(gs)
            db.session.commit()

class Candidate_Test_Result(db.Model):
    __tablename__ = "candidate_test_result"
    id = db.Column(db.Integer, primary_key = True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename_psikotest = db.Column(db.String(128))
    filename_maintest = db.Column(db.String(128))
    name = db.Column(db.String(64))
    is_deleted = db.Column(db.Boolean, default=False)

class Global_Setting(db.Model):
    __tablename__ = "global_setting"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    setting_code = db.Column(db.Integer)
    variable = db.Column(db.String(32))
    is_deleted = db.Column(db.Boolean, default=False)

    # code 1 total test duration

    @staticmethod
    def insert_static_data():
        values = [
            { "name" : "total test duration", "setting_code" : 1, "variable" : "120"}
            ]
        for v in values:
            gs = Global_Setting()
            gs.name = v['name']
            gs.setting_code = v['setting_code']
            gs.variable = v['variable']
            db.session.add(gs)
            db.session.commit()


    def __repr__(self):
        return '<Candidate_Psikotest_Schedule %r>' % self.name           

# ======================= END STATIC MODELS ==========================

# Insert Static data using python shell
def reinit():
    db.drop_all()
    db.create_all()

def initialize_data():
    Role().insert_static_data()
    User().insert_static_data()
    Level().insert_static_data()
    Division().insert_static_data()
    Global_Setting.insert_static_data()
    Psikotest_Type().insert_static_data()
    Test_Type().insert_static_data()
