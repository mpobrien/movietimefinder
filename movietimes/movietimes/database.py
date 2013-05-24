from datetime import timedelta
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from movietimes import app
import string
import random


def generate_token(length):
    return ''.join(random.choice(string.ascii_letters + string.digits)
                    for n in xrange(length))

class UserAlreadyRegistered(Exception):
    pass

class Users:
    @staticmethod
    def ensure_indexes():
        db.users.ensure_index("email")

    @staticmethod
    def reset_password(token, new_password):
        return db.users.update({"token":token}, {"$set":{"password":new_password}})

    @staticmethod
    def get_by_email(email):
        return db.users.find_one({"email":email})

    @staticmethod
    def get_by_email_pw(email, password):
        return db.users.find_one({"email":email, "password":password})

    @staticmethod
    def get_by_oid(oid):
        user = db.users.find_one({"_id":oid})
        return user

    @staticmethod
    def get_by_token(oid):
        user = db.users.find_one({"token":oid})
        return user

    @staticmethod
    def register_user(email, password):
        #TODO hash the password, generate a salt
        try:
            new_user = {"email":email, "password":password, "token":generate_token(64)}
            new_user_oid = db.users.save(new_user)
            new_user['_id'] = new_user_oid
            return new_user
        except DuplicateKeyError:
            raise UserAlreadyRegistered

class ResetTokens:
    max_age = timedelta(hours=3)

    @staticmethod
    def setup_forgot_token(email):
        token = generate_token(64)
        token_oid = db.tokens.insert({"_id":token, "email":email, "ctime":datetime.now(), "active":True})
        return token_oid

    @staticmethod
    def use_token(token):
        return db.tokens.find_and_modify(query=dict(_id=token, active=True, ctime={"$gt":datetime.now() - ResetTokens.max_age}),
                                         update={"$set":{"active":False}})

    @staticmethod
    def ensure_indexes():
        pass
        


def ensure_indexes():
    return
    for dbclass in [Users, ResetTokens]:
        dbclass.ensure_indexes()

