import webapp2
import cgi
form="""
<form method="post">
    <h2>Enter some text to ROT13:</h2>
    <textarea style="height: 100px; width: 400px;" name="text">%(text)s</textarea>
    <br>
    <input type="submit"/>
</form>
"""

def escape_html(s):
    return cgi.escape(s, quote='True')

def rot13(char):
    plain = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    cipher = 'nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM'

    d = dict(zip(plain, cipher))

    if not d.has_key(char):
        return escape_html(char)
    return d[char]

class MainPage(webapp2.RequestHandler):
    def write_form(self, text=""):
        self.response.out.write(form % {"text":text})

    def get(self):
        self.write_form()

    def post(self):
        text = self.request.get('text')

        newtext = ""
        for c in text:
            newtext += rot13(c)

        self.write_form(newtext)

app = webapp2.WSGIApplication([('/rot13', MainPage)], debug=True)


