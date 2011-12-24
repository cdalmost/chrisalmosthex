# Copyright (c) Christopher Almost, 2011.

import datetime
from hex import Game
from google.appengine.api import mail
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class SendReminders(webapp.RequestHandler):
  def get(self):
    pass

class SendSummary(webapp.RequestHandler):
  def get(self):
    week_ago = datetime.datetime.now() - datetime.timedelta(days=6)
    long_ago = datetime.datetime.now() - datetime.timedelta(weeks=8)

    #games = db.GqlQuery("SELECT * FROM Game WHERE date_modified < :1", week_ago)
    games = db.GqlQuery("SELECT * FROM Game")

    entries = ['Red vs. Blue']
    for game in games:
      flag = '*' if game.date_modified < long_ago else ''
      entries.append("created %s, last modified %s, %s vs. %s %s"
          % (str(game.date_created.date()),
             str(game.date_modified.date()),
             game.r_name, game.b_name, flag))

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
