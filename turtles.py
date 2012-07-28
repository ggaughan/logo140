# Turtles: lots of turtles
# Leeds Hack 2012
# Monkey Tennis

import turtle
import Tkinter

from collections import deque

from twisted.internet import reactor, defer
from twisted.internet.task import cooperate
from twisted.internet import tksupport

import ply.lex as lex
import ply.yacc as yacc

import lexer
import parser

import boto
import json

TURTLE_SPEED = 10  #1=slowest, 10=fast (0=no anim = fastest)

class LogoTurtle(turtle.RawTurtle):
    """Wrapper around turtle
       In future, this could be swapped out to render elsewhere...
    """
    def __init__(self, canvas, **kwargs):
        super(LogoTurtle, self).__init__(canvas, **kwargs)
        self.speed(TURTLE_SPEED)
        self.shape("turtle")
        
class TurtleContext(object):
    """Process (turtle/user) information
    """
    def __init__(self, canvas=None, **kwargs):
        super(TurtleContext, self).__init__(**kwargs)
        
        #incoming
        self.pending_scripts = deque([])  #stuff still to be parsed
        self.lexer = lex.lex(module=lexer)
        self.parser = parser.parser
        
        #parsed
        self.commands = []  #program steps
        self.np = 0  #index to next program step
        self.repeat_counters = deque()
        
        #action
        self.turtle = LogoTurtle(canvas)
        
    
    def __unicode__(self):
        return "parsed=(%s)\nnp=%s\npending=(%s)" % (self.commands, self.np, self.pending_scripts)
    
    def parse(self, s):
        new_commands = self.parser.parse(s, lexer=self.lexer)
        self.commands.extend(new_commands)
        self.process()
    
    #def do_repeat(self, N):
        #def repeat_coop():
            #for obj in xrange(N):
                #self.turtle.forward(10)
                #self.turtle.right(2)
                #yield None
        #return cooperate(repeat_coop())
    
    
    def process(self):
        """Process the next command"""
        if self.np < len(self.commands):
            command = self.commands[self.np]
            self.np += 1
            stepping = True  #temp
            op, args = command[0], command[1:]
            if op == 'fd':
                self.turtle.forward(args[0])
            elif op == 'bk':
                self.turtle.backward(args[0])
            elif op == 'rt':
                self.turtle.right(args[0])
            elif op == 'lt':
                self.turtle.left(args[0])
            elif op == 'repeat':
                self.repeat_counters.append((args[0], self.np))  #push start
            elif op == 'endrepeat':
                print "endrepeat todo"
                (counter, np) = self.repeat_counters.pop()  #pop latest
                counter -= 1
                if counter > 0:
                    self.repeat_counters.append((counter, np))  #push back
                    self.np = np  #again
                #todo else done
            #todo etc.
            else:
                #todo
                print "Unknown command"
            if stepping:
                reactor.callLater(0.00001, self.process)  #todo improve!
        #else nothing to do (until the next parse at least)

        
    #def _do_demo_repeat(self, N):
        #def repeat_coop():
            #for obj in xrange(N):
                #self.turtle.forward(10)
                #self.turtle.right(2)
                #yield None
        #return cooperate(repeat_coop())
    #def _demo(self):
        #"""test demo: temp - todo remove"""
        #self._do_demo_repeat(40)
    
    
tcs = []    

def setup_window(title = "Turtles"):
    #setup canvas and make it play nicely with Twisted
    root = Tkinter.Tk() 
    canvas = Tkinter.Canvas(root,width=600,height=600)
    canvas.pack(side = Tkinter.LEFT)
    tksupport.install(root)
    root.protocol('WM_DELETE_WINDOW', reactor.stop)
    root.title(title)
    return canvas

def get_sms():
    m_data = []
    sqs = boto.connect_sqs()
    q = sqs.get_queue('logo140')
    m = q.read()
    if m:
        m_data = m.get_body()
        m.delete()
    return m_data

if __name__ == "__main__":
    canvas = setup_window("Logo140 - Leeds Hack 2012")
    
    #create some demo turtles
    tc1 = TurtleContext(canvas)
    tc2 = TurtleContext(canvas)
    tc3 = TurtleContext(canvas)
    tc4 = TurtleContext(canvas)
    tc5 = TurtleContext(canvas)
    tcs.append(tc1)
    tcs.append(tc2)
    tcs.extend([tc3, tc4, tc5])
    
    tc1.turtle.pen(pencolor = 'blue')
    tc2.turtle.pen(pencolor = 'red')
    tc3.turtle.pen(pencolor = 'green')
    tc4.turtle.pen(pencolor = 'orange')
    tc5.turtle.pen(pencolor = 'purple')
    tc2.turtle.left(180)
    tc3.turtle.left(90)
    tc4.turtle.left(270)
    tc5.turtle.left(230)

    #tc1.parse('repeat 100 [fd 0]')  #busy
    #tc2.parse('repeat 50 [fd 0]') #busy
    #tc3.parse('repeat 200 [fd 0]') #busy
    
    #tc1._demo()
    #tc2._demo()   
    #tc1.parse('rt 105 fd 10 lt 55 fd 100 rt 90 bk 50 repeat 30 [ fd 10 rt 3 ]')  #will call process after
    
    #tc1.parse('repeat 90[fd 6 rt 4]')  #will call process after
    #tc2.parse('repeat 90[fd 6 rt 4]')  #will call process after
    #tc3.parse('repeat 90[fd 6 rt 4]')  #will call process after
    ##tc4.parse('repeat 90[fd 6 rt 4]')  #will call process after
    
    s= 'repeat 20 [repeat 90[fd 6 rt 4] rt 5]'  #nested repeat
    tc1.parse(s)
    tc2.parse(s)
    tc3.parse(s)
    tc4.parse(s)
    
    ##tc5.parse('repeat 40[fd 6 rt 4]')  #will call process after

    for tc in tcs:
        print unicode(tc)
        

    reactor.run()  #no need for tk mainloop
    