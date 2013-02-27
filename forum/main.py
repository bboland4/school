import cgi
import datetime
import urllib
import webapp2
import logging

from google.appengine.ext import db
from google.appengine.api import users
from webapp2_extras import sessions

header= \
'''
<div>
<a href="/">Home</a>
</div>
'''

threadPageHeader = \
'''<form method="POST" action="/newThread">
    <input type="text" name="threadname" />
    <input type="submit" name="newthread" value="Create a new Thread" />
</form>
''' 
PostPageHeader = \
'''<form method="POST" action="/newForumPost">
    Title</br><input type="text" name="threadTitle" /></br>
    Content</br><textarea rows="4" cols="50" name="threadContent"></textarea>
    </br><input type="submit" name="newthread" value="Reply" />
</form>
''' 

THREAD_LIST = db.Key.from_path('Thread', 'LIST')

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)
            
    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()
                


class Thread(db.Model):
    name = db.StringProperty()
    dateCreated = db.DateTimeProperty(auto_now_add=True)

class ForumPost(db.Model):
	title = db.StringProperty()		    #header title of the post
	content = db.StringProperty()		#the msg that was posted
	threadName = db.StringProperty()	#the place where the thread was posted
	owner = db.UserProperty()		    #who created the post
	datePosted = db.DateTimeProperty(auto_now_add=True)	#when the post was created


class MainPage(BaseHandler):
    def get(self):
        html = '<html><body>' + header + threadPageHeader

        threads = Thread.all().ancestor(THREAD_LIST)

        for thread in threads:
            html += '<a href="/Thread?name=%s">%s</a></br>' % (thread.name, thread.name)
        
        
        html += '</body></html'
        self.response.out.write(html)


class NewThread(BaseHandler):
    def post(self):
        tname = self.request.POST['threadname']
        newThread = Thread(key_name=tname, parent=THREAD_LIST)
        newThread.name = tname
        newThread.put()        
        self.redirect('/threads')
    
    
class NewForumPost(BaseHandler):
    def post(self):
        threadname = self.session.get('threadname')
        threadtitle = self.request.POST['threadTitle']
        
        #get parent thread
        t = Thread.all().filter("name",threadname).fetch(1)
        
        newForumPost = ForumPost(key_name=threadtitle, parent=t[0] )
        newForumPost.title = threadtitle
        newForumPost.content = self.request.POST['threadContent']
        newForumPost.threadName = threadname
        newForumPost.put()        
        self.redirect('/Thread?name=%s' % threadname)
        
class ThreadPage(BaseHandler):
    def get(self):
        tname = self.request.get('name')
        self.session['threadname'] = tname
        html = '<html><body>' + header
        t = Thread.all().filter("name",tname).fetch(1)
        curThread = t[0]
        #key = db.key.from_path('ForumPost', tname, parent=curThread)
        posts = ForumPost.all().ancestor(curThread)
        
        
        for p in posts:
            html += '<h4>%s</h4></br>' % p.title
            html += '<p>%s<p></br></br>' % p.content
            
        html += PostPageHeader + '</body></html>'
        self.response.out.write(html)

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'cs473project1secretkey'}

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/threads', MainPage),
                               ('/newForumPost', NewForumPost),
                               ('/Thread', ThreadPage),
                               ('/newThread', NewThread)],
                              debug=True, config=config)
