#!/usr/bin/env python

from bottle import route, run, debug, template, request, validate, static_file, error, install
from bottle_mongo import MongoPlugin

install(MongoPlugin(uri='localhost', db='tasks', json_mongo=True))



@route('/')
@route('/todo')
def todo_list(mongodb):        
    result = mongodb.tasks.find()
    return template('make_table', status="Open", rows=result)
    
    
@route('/new', method='GET')
def new_item():
    return template('new_task.tpl')

@route('/new', method='POST')
def new_item(mongodb):
    
    task_text = request.POST.get('task','').strip()
    task = {'text':task_text, 'status':1}
    new_id = mongodb.tasks.insert(task)
    return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
    

@route('/new/json/<no:re:\d+>', method='POST')
def new_item_json(no, mongodb):
    mongodb.setnx("current_tid", 1)
    json = request.json['new']    
    task = {'text':task_text, 'status':1}
    new_id = mongodb.tasks.insert(task)    
    return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id



@route('/edit/<no:re:\d+>', method='POST')
def edit_item(no, mongodb):
    edit = request.POST.get('task','').strip()
    status = request.POST.get('status','').strip()
    if status == 'open':
        intstatus = "1"
    else:
        intstatus = "0"
        
    mongodb.tasks.update({'_id':no}, {'$set' {'task':edit, 'status':intstatus}});
    return '<p>The item number %s was successfully updated</p>' % no
        
@route('/edit/<no:re:\d+>', method='GET')
def edit_item(no, mongodb):
    cur_data = mongodb.hget("Task:%s" % str(no), "text")
    cur_stat = mongodb.hget("Task:%s" % str(no), "status")
    print cur_data
    print cur_stat
    return template('edit_task', txt=cur_data, stat=cur_stat, no=no)


@route('/edit/json/<no:re:\d+>', method='POST')
def edit_item_json(no, mongodb):
    json = request.json['update']
    
    mongodb.tasks.update({'_id':json[0], json})

@route('/item/<item_no:re:\d+>')
def show_item(item_no, mongodb):
    result = mongodb.tasks.find({'_id':item_no})    
    
    if not result:
        return 'This item number does not exist!'
    else:
        return 'Task: %s' % result


@route('/help')
def help():
    return static_file('help.html', root='.')


@route('/json/<json:re:\d+$>')
def show_json(json):
    result = mongodb.taks.find()
    if not result:
        return {'task':'This item number does not exist!'}
    else:
        return result


@route('/completed')
def show_completed(mongodb):
    tasks = mongodb.tasks.find({'status':1})
    lstresults = []
    for i in task_nums:
        lstresults.insert(0, (tasks[0], tasks[1], tasks[2]))
        
    return template('make_table', status="Closed", rows=lstresults)

@route('/rss/open')
def rss_open(mongodb):
    sqlResults = mongodb.lrange("Tasks:open", 0, -1)
    rssResults = '''
<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>Open Todo Items</title>
            <description>open todo items</description>
            <link>http://localhost:8080/rss/open</link>
'''
    for i in sqlResults:
        rssResults += "<item>"
        rssResults += "<title>" + mongodb.hget("Task:%s" % str(i), "text") + "</title>"
        rssResults += "<description>" + mongodb.hget("Task:%s" % str(i), "text") + "</description>"
        rssResults += "<link>http://localhost:8080/item/" + str(i) + "</link>"
        rssResults += "</item>"
        
    rssResults += "</channel></rss>"
    return rssResults




@error(403)
def mistake403(code):
    return 'The parameter you passed has the wrong format!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'


run(reloader=True, debug=True)
