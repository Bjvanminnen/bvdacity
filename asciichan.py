import os
import webapp2
import jinja2
from xml.dom import minidom
import urllib2
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

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
def gmaps_img(points):
  markers = '&'.join('markers=%s %s' % (p.lat, p.lon) for p in points)
  return GMAPS_URL + markers

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
  url = IP_URL + ip
  content = None
  try:
    content = urllib2.urlopen(url).read()
  except URLError:
    return

  if content:
    # parse the xml and find the coordinates
    d = minidom.parseString(content)
    coords = d.getElementsByTagName("gml:coordinates")
    if coords and coords[0].childNodes[0].nodeValue:
      lon, lat = coords[0].childNodes[0].nodeValue.split(',')
      return db.GeoPt(lat, lon)

class Art(db.Model):
  title = db.StringProperty(required=True)
  art = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add = True)
  coords = db.GeoPtProperty()

def top_Arts():
  arts = db.GqlQuery("SELECT * "
                     "FROM Art "
                     "ORDER BY created DESC "
                     "LIMIT 10")
  arts = list(arts)

        
class MainPage(Handler):
    def render_front(self, title="", art="", error=""):

      #find which arts have coords
      points = filter(None, (a.coords for a in arts))

      #if we have any arts with coords, make an image url
      img_url = None
      if points:
        img_url = gmaps_img(points)
      # display the image url

      self.render("front.html", title=title, art=art, error=error, arts=arts,
        img_url = img_url)
    
    def get(self):
      return self.render_front()
        
    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")
        
        if title and art:
            a = Art(title = title, art = art)

            coords = get_coords(self.request.remote_addr)

            #lookup the user's coordinates from their IP
            #if we have coordinates, add them to the Art
            if coords:
              a.coords = coords

            a.put()
            
            self.redirect("/ascii")
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title=title, art=art, error=error)
        
app = webapp2.WSGIApplication([('/ascii', MainPage)], debug=True)
