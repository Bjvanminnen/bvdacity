import webapp2
import jinja2
import os
import logging

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
        entries = db.GqlQuery("SELECT * FROM BlogEntry")
        
        self.render("blog.html", entries=entries)
    
class BlogPage(Handler):
    def get(self, blog_id):
        entry = BlogEntry.get_by_id(int(blog_id)) 
        self.render("blog.html", entries=[entry])
        

class BlogEntry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
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
        

app = webapp2.WSGIApplication([('/blog', MainPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)', BlogPage)], debug=True)


