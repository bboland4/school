#!usr/bin/env python

from bottle import route, run, json, install
from bottle_redis import RedisPlugin

install(RedisPlugin())

# lpush answers 'yes'       - this will add 'yes' to the answers list in your redis db

@route('/read')
def read_json():
    nchoices = rdb.llen('answers')
    answers = rdb.lrange('answers', 0, nchoices-1)
    return { 'answer':random.choice(answers) }
#call this with "http get http://localhost:8080/read"


@route('/answers', method='POST')
def write_json():
    print request.json['answers']
    rdb.delete('answers')
    for answer in request.json['answers']:
        rdb.lpush('answers', answers)
    
    
#call this with "http --json post http://localhost:8080/answers 'answers:=['def no', 'ok maybe...', 'def']'
run(debug=True, reloader=True)
