# Copyright (c) Christopher Almost, 2011.

import os, re, datetime, hashlib, urllib
from hexutils import HexGame
from google.appengine.api import mail, channel
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Game(db.Model):
  """Models a hex game, with the players, contact info, game state, etc."""
  # Player information: name and email
  r_name  = db.StringProperty()
  b_name  = db.StringProperty()
  r_email = db.EmailProperty()
  b_email = db.EmailProperty()
  # Unique game identifiers
  r_hash = db.StringProperty()
  b_hash = db.StringProperty()
  # Are the players currently connected?
  r_conn = db.BooleanProperty()
  b_conn = db.BooleanProperty()
  # Game status
  size   = db.IntegerProperty()
  onus   = db.StringProperty()  # 'r' or 'b' ('w' iff game over)
  winner = db.StringProperty()  # name of winner or ''
  state  = db.StringProperty()
  # Useful statistics
  move = db.IntegerProperty()
  date_created  = db.DateTimeProperty(auto_now_add=True)
  date_modified = db.DateTimeProperty(auto_now=True)

class CreatePage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/create.html')
    self.response.out.write(template.render(path, dict()))

class AboutPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
    self.response.out.write(template.render(path, dict()))

class GameCreator(webapp.RequestHandler):
  def post(self):
    # Get the data and do some verification.
    p1 = self.request.get('p1').strip().title() # Creator
    p2 = self.request.get('p2').strip().title() # Opponent
    e1 = self.request.get('e1').strip()
    e2 = self.request.get('e2').strip()
    size = int(self.request.get('size'))

    # If the validation fails send them back to the start.
    if not (re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,4}$", e1) \
        and re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,4}$", e2) \
        and p1 and p2 and size < 30 and size > 4):
      self.redirect('/')
      return

    # Create the game model and put it in the database.
    g = Game()
    g.b_name = p1 # Creator is blue.
    g.r_name = p2 # Opponent is red.
    g.b_email = e1
    g.r_email = e2
    g.b_conn = True # Creator is redirected immediately.
    g.r_conn = False
    # Create unique game identifiers.
    now = datetime.datetime.now()
    g.b_hash = hashlib.sha1(p1 + 'b' + repr(now)).hexdigest()
    g.r_hash = hashlib.sha1(p2 + 'r' + repr(now)).hexdigest()
    g.size   = size
    g.onus   = 'r' # Red moves first.
    g.winner = ''
    g.state  = (size * size) * 'w'
    g.move   = 0
    g.put() # Add the game to the database.

    # Email both players.
    mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>", to=e1,
        subject="You initiated a game with %s." % p2,
        body=init_mesg % (p1, p2, urllib.urlencode({'hash': g.b_hash})))
    mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>", to=e2,
        subject="%s would like to play hex." % p1,
        body=invt_mesg % (p2, p1, urllib.urlencode({'hash': g.r_hash})))

    # Send the creator to his (blank) game page.
    self.redirect('/play?' + urllib.urlencode({'hash': g.b_hash}))

class ConnectionHandler(webapp.RequestHandler):
  def post(self):
    game_hash = self.request.get('from')
    p, g = player_and_game_from_hash(game_hash)
    if g:
      if 'r' == p:
        g.r_conn = True
      else: # 'b' == p
        g.b_conn = True
      g.put()

class DisconnectionHandler(webapp.RequestHandler):
  def post(self):
    game_hash = self.request.get('from')
    p, g = player_and_game_from_hash(game_hash)
    if g:
      if 'r' == p:
        g.r_conn = False
      else: # 'b' == p
        g.b_conn = False
      g.put()

class GameDisplayer(webapp.RequestHandler):
  def get(self):
    # A player wishes to view his game.
    game_hash = self.request.get('hash')
    p, g = player_and_game_from_hash(game_hash)
    if g:
      # Valid game hash: show them the game.
      if 'w' == g.onus:
        mesg = "The game is over (%s won)." % g.winner
      else:
        mesg = "It's %s's turn." % (g.r_name if ('r' == g.onus) else g.b_name)
      token = channel.create_channel(game_hash)
      template_values = {
        'r_name': g.r_name,
        'b_name': g.b_name,
        'mesg': mesg,
        'hash': game_hash,
        'token': token,
        'size': g.size,
        'state': g.state,
        'm': g.onus,
        'p': p,
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/play.html')
      self.response.out.write(template.render(path, template_values))
    else:
      # Invalid hash (or there was none): show them the start page.
      self.redirect('/')

class MoveMaker(webapp.RequestHandler):
  def post(self):
    # A move has been suggested.
    game_hash = self.request.get('hash')
    p, g = player_and_game_from_hash(game_hash)
    # Was it in fact p's turn to move?
    if not (g.onus == p):
      self.redirect('/play?' + urllib.urlencode({'hash': game_hash}))
      return
    # Prepare to process the move.
    if p == 'r':
      p_name = g.r_name
      o_name = g.b_name
      o_hash = g.b_hash
      o_conn = g.b_conn
      o_email = g.b_email
    else: # p == 'b'
      p_name = g.b_name
      o_name = g.r_name
      o_hash = g.r_hash
      o_conn = g.r_conn
      o_email = g.r_email

    # Get the move and act on it.
    move_str = self.request.get('coords')
    if move_str == 'resign':
      g.onus = 'w'
      g.winner = o_name
      self.redirect('/play?' + urllib.urlencode({'hash': game_hash}))
      mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>",
          to=o_email, subject="%s resigned." % p_name,
          body=rsgn_mesg % (o_name, p_name, urllib.urlencode({'hash': o_hash})))
    else: # Normal move.
      x, y = move_str.split(' ')
      index = g.size * int(x) + int(y)
      g.state = g.state[:index] + p + g.state[index+1:]
      g.move += 1
      g.onus = HexGame.swap[p]

      # Check whether the game is over.
      hg = HexGame(game_size=g.size, state_str=g.state)
      if p == hg.check_win():
        # The player won!
        g.onus = 'w'
        g.winner = p_name
        path = os.path.join(os.path.dirname(__file__), 'templates/winner.html')
        self.response.out.write(template.render(path, {"name": p_name}))
        mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>",
            to=o_email, subject="Game over, %s won." % p_name,
            body=over_mesg % (o_name, p_name, urllib.urlencode({'hash': o_hash})))
      else:
        # Send them on their merry way.
        self.redirect('/play?' + urllib.urlencode({'hash': game_hash}))
        # Send opponent an email if they are not currently connected.
        if not o_conn:
          mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>",
              to=o_email,
              subject="[Move #%d] It's your turn against %s." % (g.move, p_name),
              body=move_mesg % (o_name, p_name, urllib.urlencode({'hash': o_hash})))
    # Record the update.
    g.put()
    # Refresh opponent's page if they are connected.
    if o_conn: channel.send_message(o_hash, "reload")

def player_and_game_from_hash(game_hash):
  if game_hash:
    query = Game.all()
    query.filter("r_hash =", game_hash)
    game = query.get()
    if game:
      return ('r', game)
    query = Game.all()
    query.filter("b_hash =", game_hash)
    game = query.get()
    if game:
      return ('b', game)
  return (None, None)

init_mesg = """Dear %s,

You initiated a game of hex with %s.  View the game at:

http://hex.chrisalmost.org/play?%s
"""

invt_mesg = """Dear %s,

Your friend %s would like to play hex with you.  It's your turn.  View the game at:

http://hex.chrisalmost.org/play?%s
"""

move_mesg = """Dear %s,

It's your turn to make a move against %s.

http://hex.chrisalmost.org/play?%s
"""

over_mesg = """Dear %s,

Your opponent, %s, won the game.  Better luck next time!

http://hex.chrisalmost.org/play?%s
"""

rsgn_mesg = """Dear %s,

Your opponent, %s, resigned, so you won the game.  Congratulations.

http://hex.chrisalmost.org/play?%s
"""

def main():
  run_wsgi_app(webapp.WSGIApplication([
      ('/play',   GameDisplayer),
      ('/move',   MoveMaker),
      ('/create', GameCreator),
      ('/about',  AboutPage),
      ('/_ah/channel/disconnected/', DisconnectionHandler),
      ('/_ah/channel/connected/',    ConnectionHandler),
      ('/.*', CreatePage),
    ], debug=True))

if __name__ == '__main__':
  main()
