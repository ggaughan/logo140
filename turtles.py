# Turtles: lots of turtles
# Leeds Hack 2012
# Monkey Tennis

import turtle

from collections import deque

class TurtleContext(object):
    """Process information
    """
    def __init__(self, **kwargs):
        super(TurtleContext, self).__init__(**kwargs)
        
        self.turtle = turtle.Turtle  #todo: replace with our own
        self.pending_scripts = deque([])  #stuff still to be parsed
        self.commands = []  #program steps
        self.np = 0  #index to next program step
    
    def __unicode__(self):
        return "pending=(%s)" % (self.pending_scripts)
    
    
tcs = []    
    
if __name__ == "__main__":
    tcs.append(TurtleContext())
    
    for tc in tcs:
        print unicode(tc)
