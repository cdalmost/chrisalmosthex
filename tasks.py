# Copyright (c) Christopher Almost, 2011.

import datetime
from hex import Game
from google.appengine.api import mail
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class SendReminders(webapp.RequestHandler):
  def get(self):
    period   = datetime.datetime.now() - datetime.timedelta(days=5)
    long_ago = datetime.datetime.now() - datetime.timedelta(weeks=5)
    games = db.GqlQuery("SELECT * FROM Game" +
                        "WHERE date_modified < :1 AND date_modified > :2",
                        period, long_ago)

    entries = ['Cheers!']
    for game in games:
      if not 'w' == game.onus: # Game has no winner yet.
        story = "%s vs. %s, created %s, last modified %s" \
            % (game.r_name, game.b_name, \
            str(game.date_created.date()), \
            str(game.date_modified.date()))
        entries.append(story)
    entries.append('Red vs. Blue')
    entries.reverse()

    mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>",
                   to="Chris Almost <cdalmost@gmail.com>",
                   subject="Hex reminders",
                   body='\n'.join(entries))

class SendSummary(webapp.RequestHandler):
  def get(self):
    games = db.GqlQuery("SELECT * FROM Game")
    long_ago = datetime.datetime.now() - datetime.timedelta(weeks=5)

    entries = ['Cheers!']
    for game in games:
      flag = '(old)' if game.date_modified < long_ago else '(new)'
      story = "%s vs. %s, created %s, last modified %s %s" \
          % (game.r_name, game.b_name, str(game.date_created.date()), \
          str(game.date_modified.date()), flag)
      if 'w' == game.onus: # Game has a winner.
        story += ", %s won" % game.winner
      entries.append(story)
    entries.append('Red vs. Blue')
    entries.reverse()

    mail.send_mail(sender="Chris Almost <cdalmost@gmail.com>",
                   to="Chris Almost <cdalmost@gmail.com>",
                   subject="Summary of hex games",
                   body='\n'.join(entries))

def main():
  run_wsgi_app(webapp.WSGIApplication([
      ('/tasks/reminder', SendReminders),
      ('/tasks/summary',  SendSummary),
    ], debug=True))

if __name__ == '__main__':
  main()
