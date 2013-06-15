from google.appengine.ext import db


class User(db.Model):
    username = db.StringProperty(required = True)
    password_hash = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
