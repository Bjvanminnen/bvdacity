import webapp2
import re
import logging
import hashlib
import random
import string
import SignupForm
from User import *

secret = "SECRET"

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid(string, regex):
    return regex.match(string)  

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(name, pw, salt)

def set_cookie(username, request):
    val = 'user=%s; Path=/' % str(username)            
    request.response.headers.add_header('Set-Cookie', val)

def add_user(username, password_hash, request):
    set_cookie(username, request)
    # add to db
    user = User(username = username, password_hash = password_hash)
    user.put()    
    

class MainPage(webapp2.RequestHandler):
    def write_form(self, form, username='', email='', user_error='',
                   password_error='', match_error='', email_error=''):
        variables = {}
        variables['username'] = username
        variables['email'] = email
        variables['user_error'] = user_error
        variables['password_error'] = password_error
        variables['match_error'] = match_error
        variables['email_error'] = email_error        
        
        self.response.out.write(form % variables)

    def get(self):
        cookie = self.request.cookies.get('user')        
        if cookie:
            self.redirect('/blog/welcome')
        self.write_form(SignupForm.form_signup)

    def post(self):            
        username = self.request.get('username')
        password = self.request.get('password')
        password2 = self.request.get('verify')
        email = self.request.get('email')
        
        user_error = ''
        password_error = ''
        match_error = ''
        email_error = ''
        success = True
        if not valid(username, USER_RE):
            user_error = 'That\'s not a valid username'
            success = False
        if not valid(password, PASSWORD_RE):
            password_error = 'That wasn\'t a valid password'
            success = False
        if not password == password2:
            match_error = 'Your passwords didn\'t match'
            success = False
        if not email == '' and not valid(email, EMAIL_RE):
            email_error = 'That\'s not a valid email.'
            success = False        
        
        if success:
            add_user(username, make_pw_hash(username, password), self)            
            self.redirect('/blog/welcome')
        else:
            self.write_form(SignupForm.form_signup, username, email, user_error,
                            password_error, match_error, email_error)
            
class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        cookie = self.request.cookies.get('user')        
        if not cookie:
            self.redirect('/blog/signup')        
        
        self.response.out.write("Welcome, " + cookie)
        
class LoginHandler(webapp2.RequestHandler):
    def write_form(self, form, username='', error=''):
        variables = {}
        variables['username'] = username        
        variables['error'] = error        
        
        self.response.out.write(form % variables)
        
    def get(self):        
        self.write_form(SignupForm.form_login)
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        
        users = db.GqlQuery("SELECT * FROM User")
        found = False
        for user in users:
            if user.username == username:
                found = True
                
                if not valid_pw(username, password, user.password_hash):
                    self.write_form(SignupForm.form_login, username=username,
                                    error = 'Invalid login')
                    return
                
        if not found:
            self.write_form(SignupForm.form_login, username=username,
                            error = 'Invalid login')
            return
         
        set_cookie(username, self)
        self.redirect('/blog/welcome')

class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        set_cookie('', self)
        self.redirect('/blog/signup')
        

app = webapp2.WSGIApplication([('/blog/signup', MainPage),
                               ('/blog/welcome', WelcomeHandler),
                               ('/blog/login', LoginHandler),
                               ('/blog/logout', LogoutHandler)], debug=True)


