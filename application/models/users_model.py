from application import app, DATABASE
from application.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
import re    
bcrypt = Bcrypt(app)

class User:
    
    TABLE_NAME = 'users'
    ATTR_TAGS = ['first_name','last_name','email','password']
    NAME_LENGTH = 2
    PASSWORD_LENGTH = 8
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])')
    
    def __init__(self, data) -> None:
        self.id = data['id']
        for tag in self.ATTR_TAGS:
            setattr(self, tag, data[tag])

    @classmethod
    def getAllUsers(cls):
        query = f'SELECT * FROM {cls.TABLE_NAME};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        user = [cls(user) for user in rslt]
        return user

    @classmethod
    def getUser(cls, user_data=None, id=False):
        query = f'SELECT * FROM {cls.TABLE_NAME} WHERE '
        query += 'email = %(email)s' if not id else f'id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query, user_data)
        return cls(rslt[0]) if rslt else False

    @classmethod
    def validateLogin(cls, creds):
        cred_dict = {
            'email' : ('Please provide your email.', 'error_login_email'),
            'password' : ('Please enter your password.', 'error_login_pw')
            }
        if not cls.flashCheck(creds, cred_dict):
            return False
        current_user = cls.getUser(creds)
        if not current_user or bcrypt.check_password_hash(current_user.password, creds['password']):
            return False
        return current_user.id

    @classmethod
    def validateRegist(cls, regist_info):
        regist_info_dict = {
            'first_name' : 
                ('Please provide your first name.', 
                 'error_regist_fn',
                 len(regist_info['first_name']) >= cls.NAME_LENGTH),
            'last_name' : 
                ('Please provide your last name.', 
                 'error_regist_ln',
                 len(regist_info['last_name']) >= cls.NAME_LENGTH),
            'email' : 
                ('Please provide a valid email.', 
                 'error_regist_email',
                 cls.EMAIL_REGEX.match(regist_info['email']) != None),
            'password' : 
                (f'Your password must include: at least {cls.PASSWORD_LENGTH} characters, an upper case letter, a lower case letter, a number, and a special character.', 
                 'error_regist_pw',
                 len(regist_info['password']) >= cls.PASSWORD_LENGTH,
                 cls.PASSWORD_REGEX.match(regist_info['password']) != None),
            'confirm_pw' : 
                ('Passwords must match.', 
                 'error_regist_pw_match',
                 regist_info['password'] == regist_info['confirm_pw'])
        }
        return cls.flashCheck(regist_info, regist_info_dict)

    @classmethod
    def registerNewUser(cls, regist_info):
        query = f'SELECT * FROM {cls.TABLE_NAME} '
        query += 'WHERE email = %(email)s;'
        rslt = connectToMySQL(DATABASE).query_db(query, regist_info)
        if rslt:
            flash('An account with this email has already been registered. Please try another.',
                  'error_regist_email')
            return False
        return cls.createNewUser(regist_info)

    @classmethod
    def createNewUser(cls, user_info):
        user_data = {
            **user_info,
            'password': bcrypt.generate_password_hash(user_info['password'])
        }
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, user_data)
        return rslt

    @staticmethod
    def flashCheck(data, data_dict):
        validity = True
        for (k, v) in data_dict.items():
            if not data[k] or not all(v):
                flash(v[0], v[1])
                validity = False
        return validity