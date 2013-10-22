import webapp2
import jinja2
import os
import logging
import json

from datetime import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t  = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        key = 'MainPage'
        entries = memcache.get(key)
        if entries is None:
          logging.error("DB query")
          queryTime = datetime.now()
          entries = db.GqlQuery("SELECT * FROM BlogEntry")
          memcache.set(key, entries)
          memcache.set("qt", queryTime)
        else:
          queryTime = memcache.get("qt")

        now = datetime.now()
        seconds = (now - queryTime).seconds
        self.render("blog.html", entries=entries, seconds=seconds)
    
class BlogPage(Handler):
    def get(self, blog_id):
        entry = BlogEntry.get_by_id(int(blog_id)) 
        self.render("blog.html", entries=[entry], seconds=100)
        

class BlogEntry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def asJSON(self):
      return '{"subject": "%s", "content": "%s"}' % (self.subject, self.content)
    
class NewPost(Handler):
    def get(self):
        self.render("newpost.html")
        
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        error = ""
        
        logging.warn("Subject: " + subject)
        if content == "" or subject == "":
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content,
                    error=error)
        else:
            entry = BlogEntry(subject = subject, content = content)
            entry.put()
            
            blog_id = str(entry.key().id())
            self.redirect("/blog/%s"%blog_id)



class JSONMain(Handler):
  def get(self):
    entries = db.GqlQuery("SELECT * FROM BlogEntry")
    self.response.headers["Content-Type"] = "application/json"

    self.write("[" + ','.join(entry.asJSON() for entry in entries) + "]")

        
class JSONPage(Handler):
  def get(self, blog_id):
    entry = BlogEntry.get_by_id(int(blog_id))
    self.response.headers["Content-Type"] = "application/json"
    self.write(entry.asJSON())
    


app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)', BlogPage),
                               ('/blog/.json', JSONMain),
                               ('/blog/([0-9]+).json', JSONPage)], debug=True)


