import os
import webapp2
import jinja2
import logging
import time

from google.appengine.ext import db

NOBID = -1

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
        
class Game(db.Model):
    id = db.IntegerProperty(required = True)
    scotch = db.IntegerProperty(required = True)
    p1_money = db.IntegerProperty(required = True)
    p2_money = db.IntegerProperty(required = True)
    p1_draw = db.BooleanProperty(required = True)
    p1_bid = db.IntegerProperty(required = True)
    p2_bid = db.IntegerProperty(required = True)
    rnd = db.IntegerProperty(required = True)
    
    def gstr(self):
        gstr = ""
        for i in range(11):
            if i == self.scotch:
                gstr += jinja2.Markup("<span style='color: red'>S</span> ")
            else:
                gstr += str(i) + " "
        return gstr
    
    def handle_bids(self):
        self.p1_money -= self.p1_bid
        self.p2_money -= self.p2_bid
        
        if self.p1_bid == self.p2_bid:
            if self.p1_draw:
                self.scotch -= 1
            else:
                self.scotch += 1
            self.p1_draw = not self.p1_draw
        elif self.p1_bid > self.p2_bid:
            self.scotch -= 1
        else:
            self.scotch += 1        
        
        # reset
        self.p1_bid = NOBID
        self.p2_bid = NOBID
    
    def draw(self):
        pass

    def p1_win(self):
        return self.scotch == 0
    
    def p2_win(self):
        return self.scotch == 10
    
    def game_over(self):
        return self.draw() or self.p1_win() or self.p2_win()
    
    
    
        
class PlayerPage(Handler):
    def get_game(self):
        games = db.GqlQuery("SELECT * FROM Game")        
        game = games.get() # not using id to start
        
        if game == None:
            game = Game(id=1, scotch=5, p1_money=100, p2_money=100,
                        p1_draw=True, p1_bid=NOBID, p2_bid=NOBID, rnd=1)
            game.put()
        return game
    
    def render_page(self, error=""):
        game = self.get_game()        
        
        bids = [game.p1_bid, game.p2_bid]
        if not self.p1:
            bids.reverse()
            
        info=''
        waiting = False
        if bids[1] == NOBID and bids[0] != NOBID:
            info = 'Waiting on other player to make a bid.'
            waiting = True
        elif bids[1] != NOBID:
            info = 'Other player is waiting on you...'
        
        if game.game_over():
            if game.draw():
                info = 'Draw.'
            elif game.p1_win():
                info = 'Player 1 wins.'
            else:
                info = 'Player 2 wins.'
                
            self.render("gameover.html", game=game, info=info)
        else:
            self.render("bidgame.html", game=game, my_bid=bids[0], info=info,
                        error=error)
            
#        while waiting:
#            logging.warn('sleeping')
#            time.sleep(15)
#            game = self.get_game()
#            bids = [game.p1_bid, game.p2_bid]
#            if not self.p1:
#                bids.reverse()
#            if bids[1] == NOBID and bids[0] != NOBID:
#                self.render_page()
            
    
    def get(self):
        self.render_page()
        
    def post(self):
        
        ng = self.request.get("newgame", default_value = None)
        if ng != None:
            logging.warn("New game")
            games = db.GqlQuery("SELECT * FROM Game")
            game = games.get()
            db.delete(game)            
            self.render_page()
            return
        
        
        
        logging.debug("post")
        
        form_round = int(self.request.get("round"))
        bid = int(self.request.get('bid'))
        game = self.get_game()
        
        if form_round != game.rnd:
            logging.warn("skipping resubmission of previous round")
            self.render_page()
            return
        
        logging.warn("bid: " + str(bid))
        
        error = ''
        if self.p1:
            logging.warn("self.p1:" + str(bid > game.p1_money))
            
            if bid < min(1, game.p1_money):
                error = 'must bid at least ' + str(min(1, game.p1_money))
            elif bid > game.p1_money:
                error = 'cant bid more than ' + str(game.p1_money)
            else:
                game.p1_bid = bid
        else:
            logging.warn("self.p2")
            if bid < min(1, game.p2_money):
                error = 'must bid at least ' + str(min(1, game.p2_money))
            elif bid > game.p2_money:
                error = 'cant bid more than ' + str(game.p2_money)
            else:
                game.p2_bid = bid
        
        if game.p1_bid != NOBID and game.p2_bid != NOBID:
            game.handle_bids()
            game.rnd += 1
        
        game.put()
            
        self.render_page(error)
        
    
        
        
    
class Player1Page(PlayerPage):
    p1 = True

class Player2Page(PlayerPage):
    p1 = False
        
        
        
app = webapp2.WSGIApplication([('/bidgame/player1', Player1Page),
                               ('/bidgame/player2', Player2Page)], debug=True)
