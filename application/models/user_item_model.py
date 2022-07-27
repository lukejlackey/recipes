from application import DATABASE
from application.models.users_model import User
from application.config.mysqlconnection import connectToMySQL
from flask import flash 

class UserItem:
    
    TABLE_NAME = 'recipes'
    ATTR_TAGS = ['name', 'description', 'date', 'instructions', 'under', 'user_id']
    NAME_LENGTH = 2
    
    def __init__(self, data) -> None:
        self.id = data['id']
        for tag in self.ATTR_TAGS:
            setattr(self, tag, data[tag])
        if 'first_name' in data:
            self.first_name = data['first_name']
        if data['under']:
            self.under = 'Yes'
        else:
            self.under = 'No'

    @classmethod
    def getAllItems(cls):
        query = f'SELECT {cls.TABLE_NAME}.*, {User.TABLE_NAME}.first_name FROM {cls.TABLE_NAME} '
        query += f'LEFT JOIN {User.TABLE_NAME} ON {cls.TABLE_NAME}.user_id = {User.TABLE_NAME}.id;'
        rslt = connectToMySQL(DATABASE).query_db(query)
        print(rslt)
        if not rslt:
            return False
        items = [cls(item).__dict__ for item in rslt]
        return items

    @classmethod
    def getAllUserItems(cls, user_id):
        query = f'SELECT * FROM {cls.TABLE_NAME} WHERE '
        query += f'user_id = {user_id};'
        rslt = [cls(item) for item in connectToMySQL(DATABASE).query_db(query)]
        if not rslt:
            return False
        items = [cls(item).__dict__ for item in rslt]
        return items

    @classmethod
    def getItem(cls, id):
        query = f'SELECT {cls.TABLE_NAME}.*, {User.TABLE_NAME}.first_name FROM {cls.TABLE_NAME} '
        query += f'LEFT JOIN {User.TABLE_NAME} ON {cls.TABLE_NAME}.user_id = {User.TABLE_NAME}.id '
        query += f'WHERE {cls.TABLE_NAME}.id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return cls(rslt[0]) if rslt else False

    @classmethod
    def validateCreateItem(cls, item_info):
        info_dict = {
            'name' : 
                ('Please name your item.', 
                 'error_create_item_name',
                 len(item_info['name']) >= cls.NAME_LENGTH),
            'description' : 
                ('Please provide a description of your item.', 
                 'error_create_item_description'),
            'date' : 
                ('Please provide a date.', 
                 'error_create_item_description',),
            'instructions' : 
                ('Please provide instructions.', 
                 'error_create_item_instructions',),
            'under' : 
                ('Please provide whether or not you made your recipe in under 30 mins.', 
                 'error_create_item_under',)
        }
        return cls.flashCheck(item_info, info_dict)

    @classmethod
    def createNewItem(cls, item_info):
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, item_info)
        return rslt

    @classmethod
    def updateItem(cls, new_info):
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'{tag} = %({tag})s' )
        cols = ', '.join(cols)
        query += f'SET {cols} '
        query += 'WHERE id = %(id)s;'
        print(query)
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)
        return rslt

    @classmethod
    def deleteItem(cls, id):
        query = f'DELETE FROM {cls.TABLE_NAME} WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return rslt

    @staticmethod
    def flashCheck(data, data_dict):
        validity = True
        for (k, v) in data_dict.items():
            if not data[k] or not all(v):
                flash(v[0], v[1])
                validity = False
        return validity