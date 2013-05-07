from bottle.ext import sqlite
from bottle import route, run, debug, template, request, validate, static_file, error, install

plugin = sqlite.Plugin(dbfile='todo.db')
install(plugin)


@route('/')
@route('/todo')
def todo_list(db):        
    result = db.execute("SELECT id, task FROM todo WHERE status LIKE '1'").fetchall()
    return template('make_table', status="Open", rows=result)
    
    
@route('/new', method='GET')
def new_item():
    return template('new_task.tpl')

@route('/new', method='POST')
def new_item(db):
    new = request.POST.get('task', '').strip()
    result = db.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
    new_id = result.lastrowid
    return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
    

@route('/new/json/<no:re:\d+>', method='POST')
def new_item_json(no, db):
    json = request.json['new']
    print json
    oldid = json[0]
    newtask = json[1]
    newstatus= json[2]
    sql = "INSERT INTO todo (task,status) VALUES (?,?)".format(str(newtask), str(newstatus))
    #return sql
    result = db.execute(sql)
    new_id = result.lastrowid
    return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id



@route('/edit/<no:re:\d+>', method='POST')
def edit_item(no, db):
    edit = request.POST.get('task','').strip()
    status = request.POST.get('status','').strip()

    if status == 'open':
        status = 1
    else:
        status = 0
    sql = "UPDATE todo SET task='{0}', status='{1}' WHERE id={2}".format(str(edit), str(status), str(no))
    #return sql
    db.execute(sql)
    return '<p>The item number %s was successfully updated</p>' % no
        
@route('/edit/<no:re:\d+>', method='GET')
def edit_item(no, db):
    cur_data = db.execute("SELECT task, status FROM todo WHERE id LIKE ?", [no]).fetchone()
    return template('edit_task', old=cur_data, no=no)


@route('/edit/json/<no:re:\d+>', method='POST')
def edit_item_json(no, db):
    json = request.json['update']
    print json
    oldid = json[0]
    newtask = json[1]
    newstatus= json[2]
    sql = "UPDATE todo SET task='{0}', status='{1}' WHERE id={2}".format(str(newtask), str(newstatus), str(oldid))
    #return sql
    db.execute(sql)
    return '<p>The item number %s was successfully updated</p>' % no

@route('/item/<item:re:\d+>')
def show_item(item, db):
    result = db.execute("SELECT task FROM todo WHERE id LIKE ?", [item]).fetchone()
    if not result:
        return 'This item number does not exist!'
    else:
        return 'Task: %s' % result.__getitem__(0)


@route('/help')
def help():
    return static_file('help.html', root='.')


@route('/json/<json:re:\d+$>')
def show_json(json, db):
    result = db.execute("SELECT task FROM todo WHERE id LIKE ?", [json]).fetchone()
    if not result:
        return {'task':'This item number does not exist!'}
    else:
        return {'Task': result.__getitem__(0)}


@route('/completed')
def show_completed(db):
    result = db.execute("SELECT id, task FROM todo WHERE status LIKE '0'").fetchall()
    return template('make_table', status="Closed", rows=result)

@route('/rss/open')
def rss_open(db):
    sql = "SELECT id, task, status FROM todo WHERE status like '1'"
    sqlResults = db.execute(sql).fetchall()
    rssResults = '''
<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>Open Todo Items</title>
            <description>open todo items</description>
            <link>http://localhost:8080/rss/open</link>
'''
    for row in sqlResults:
        rssResults += "<item>"
        rssResults += "<title>" + str(row[0]) + "</title>"
        rssResults += "<description>" + str(row[1]) + "</description>"
        rssResults += "<link>http://localhost:8080/item/" + str(row[0]) + "</link>"
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
