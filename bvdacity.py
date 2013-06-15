import webapp2
import cgi
import unit4.play as play

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December']

def valid_month(month):
    for m in months:
        if m.lower() == month.lower():
            return m

def valid_day(day):
    if day.isdigit():
        d = int(day)
        if d >= 1 and d <= 31:
            return d

def valid_year(year):
    if year.isdigit():
        y = int(year)
        if y >= 1900 and y <= 2020:
            return y

def escape_html(s):    
    return cgi.escape(s, quote='True')



form="""
<form method="post">
    What is your birthday?
    <br>
    <label>Month<input type="text" name="month" value="%(month)s"> </label>
    <label>Day<input type="text" name="day" value="%(day)s"></label>
    <label>Year<input type="text" name="year" value="%(year)s"></label>
    <div style="color: red">%(error)s</div>
    <br>
    <input type="submit">
</form>
"""

class MainPage(webapp2.RequestHandler):
    def write_form(self, error="", day="", month="", year=""):
        self.response.out.write(form % {"error": error,
                                        "day": escape_html(day),
                                        "month": escape_html(month),
                                        "year": escape_html(year)})

    def get(self):
        self.write_form()
    
    def post(self):
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = valid_month(user_month)
        day = valid_day(user_day)
        year = valid_year(user_year)

        if not (month and day and year):
            self.write_form("error", user_day, user_month, user_year)
        else:
            self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! That worked")

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/thanks', ThanksHandler)
                               #('/unit4/play', play.MainPage)
                               ],
        debug=True)

def main():
    app.run()

# if __name == '__main()__':
#    main()
      
