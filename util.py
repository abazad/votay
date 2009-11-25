from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache
import os
import sys

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def missingTrailingSlash(handler):
  if handler.request.uri.endswith('/'):
    return False
  else:
    handler.redirect(''.join([handler.request.uri, '/']), permanent=True)
    return True
   
def send404(handler):
  handler.error(404)
  handler.response.out.write(template.render(APP_ROOT_DIR + '/home/views/404.html', {}))
  
def getRecentBlogPosts(page):
  data = None
  if page == 1:
    data = memcache.get('p1')

  if data is None:
    query = db.GqlQuery('SELECT * FROM BlogPost ORDER BY created_at desc')
    per_page = 5
    posts = query.fetch(per_page, per_page*(page-1))
  
    data = {'posts': posts}
    if page == 1: 
      memcache.add('p1', data, 3600)

  return data

def addImageDataToPost(post):
  if post.width:
    return
  query = db.GqlQuery('SELECT * FROM ImageMetaData WHERE filename = :1', post.image)
  list = query.fetch(1)
  if len(list) == 1:
    post.width = list[0].width
    post.height = list[0].height
    post.put()

def loadBlogPost(permalink):
  post = memcache.get(permalink)
  
  if post is None:
    query = db.GqlQuery('SELECT * FROM BlogPost WHERE permalink = :1', permalink)
    list = query.fetch(1)

    if len(list) == 0:
      return None
    
    post = list[0]
    memcache.add(permalink, post, 3600)
  return post
