#!/usr/bin/env python

import boto
import json
import uuid
import random

sqs = boto.connect_sqs()
q = sqs.get_queue('logo140')

def random_commands(n):
    '''Return some simple turtle movement commands'''
    commands = ['FD', 'RT', 'LT'] 
    l = []
    for i in xrange(0, n):
        l.append('%s %s' % (random.choice(commands), random.randint(0, 100)))

    return l

for i in xrange(0, 15):

    msg_data = {"content": random_commands(10),
            "to": [str(uuid.uuid1())], "part": ["1"], "msg_id": ["VI_144681241"],
            "from": ["447534226331"]}
    
    message = q.new_message(body=json.dumps(msg_data))
    q.write(message)
