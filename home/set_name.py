import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import models
import util

class MainHandler(webapp.RequestHandler):
  def get(self,path):
    util.send404(self)
    return
    
class SetNameHandler(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    
    query = db.GqlQuery('SELECT * FROM Nickname WHERE user_id = :1', user.user_id())
    list = query.fetch(1)
    if len(list) == 0:
      nickname = models.Nickname(user_id=user.user_id(),
                             nickname=self.request.get('name'),
                             url=self.request.get('url'))
    else:
      nickname = list[0]
      nickname.nickname = self.request.get('name')
      nickname.url = self.request.get('url')
    nickname.put()
    if self.request.get('return_url'):
      self.redirect(self.request.get('return_url'), permanent=False)
    else:
      self.redirect('/', permanent=False)      
  def get(self):
    user = users.get_current_user() 
    query = db.GqlQuery('SELECT * FROM Nickname WHERE user_id = :1', user.user_id())
    list = query.fetch(1)
    nickname = None
    if len(list) == 1:
      nickname = list[0]

    data = { 'title': 'Set Name', 
             'nickname': nickname,
             'email': user.email(),
             'logout_url': users.create_logout_url('/'),
             'return_url': self.request.get('return_url') }
    self.response.out.write(template.render('views/set_name.html', data))
    
def main():
  application = webapp.WSGIApplication([('/set-name.*', SetNameHandler),
                                        ('/(.*)', MainHandler)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
