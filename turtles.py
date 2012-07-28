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

class LogoTurtle(turtle.RawTurtle):
    """Wrapper around turtle
       In future, this could be swapped out to render elsewhere...
    """
    def __init__(self, canvas, **kwargs):
        super(LogoTurtle, self).__init__(canvas, **kwargs)
        
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
        
        #action
        self.turtle = LogoTurtle(canvas)
        
    
    def __unicode__(self):
        return "parsed=(%s)\npending=(%s)" % (self.commands, self.pending_scripts)
    
    def parse(self, s):
        new_commands = self.parser.parse(s, lexer=self.lexer)
        self.commands.extend(new_commands)
    
    def do_repeat(self, N):
        def repeat_coop():
            for obj in xrange(N):
                self.turtle.forward(10)
                self.turtle.right(2)
                yield None
        return cooperate(repeat_coop())
    
    def process(self):
        """Process the next command"""
        if self.np < len(self.commands):
            command = self.commands[self.np]
            self.np += 1
            op, args = command[0], command[1:]
            if op == 'fd':
                self.turtle.forward(args[0])
            elif op == 'rt':
                self.turtle.right(args[0])
            elif op == 'lt':
                self.turtle.left(args[0])
            #todo etc.
            #todo else
        #else nothing to do
        reactor.callLater(1, self.process)  #todo improve!
    
    def _demo(self):
        """test demo: temp - todo remove"""
        self.do_repeat(40)
    
    
tcs = []    
    
if __name__ == "__main__":
    #setup canvas and make it play nicely with Twisted
    root = Tkinter.Tk() 
    canvas = Tkinter.Canvas(root,width=600,height=600)
    canvas.pack(side = Tkinter.LEFT)
    tksupport.install(root)
    root.protocol('WM_DELETE_WINDOW', reactor.stop)
    root.title("Logo140 - Leeds Hack 2012")

    #create some demo turtles
    tc1 = TurtleContext(canvas)
    tc2 = TurtleContext(canvas)
    tcs.append(tc1)
    tcs.append(tc2)
    
    tc1.turtle.pen(pencolor = 'blue')
    tc1.turtle.pen(pencolor = 'red')
    tc2.turtle.left(180)
    
    #tc1._demo()
    tc2._demo()   
    tc1.parse('rt 105 fd 10 lt 55 bk 5')
    tc1.process()

    for tc in tcs:
        print unicode(tc)
        

    reactor.run()  #no need for tk mainloop
