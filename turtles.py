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

MAX_RECURSION = 5
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
        self.lexer.context = self  #reverse reference, so lexer can access current namespaces
        self.parser = parser.parser

        #namespaces
        self.namespace = deque()
        self.namespace.append({})  #globals  #todo complete
        self.namespace.append({})  #locals  #function locals will be added and removed at runtime

        #stack frames
        self.stack = deque()
        
        #parsed
        self.commands = []  #program steps
        self.np = 0  #index to next program step
        self.repeat_counters = deque()
        
        #action
        self.turtle = LogoTurtle(canvas)
        
    
    def __unicode__(self):
        return "parsed=(%s)\nnp=%s\npending=(%s)" % (self.commands, self.np, self.pending_scripts)
    
    def namespace_lookup(self, name):
        """Find which namespace the name is in, starting with locals first then working outwards
           return None if not found
        """
        for ns in self.namespace:
            if name in ns:
                return ns
    
    def parse(self, s):
        new_commands = self.parser.parse(s, lexer=self.lexer)
        if new_commands is not None:
            self.commands.extend(new_commands)
            self.process()
        #else possibly syntax error
    
    #def do_repeat(self, N):
        #def repeat_coop():
            #for obj in xrange(N):
                #self.turtle.forward(10)
                #self.turtle.right(2)
                #yield None
        #return cooperate(repeat_coop())
    
    def calling(self):
        """Returns True if we are currently in a function call"""
        return len(self.stack) > 0
    
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
                (counter, np) = self.repeat_counters.pop()  #pop latest
                counter -= 1
                if counter > 0:
                    self.repeat_counters.append((counter, np))  #push back
                    self.np = np  #again
                #else done, continue
            elif op == 'to':
                self.namespace[0][args[0]] = self.np  #declare name + start point in locals (assumes name is lowercased already)
                #todo store args too! so parser can check/greedy calls
                #find corresponding endto and jump over it
                endto_p = self.np
                depth = 1
                for c in self.commands[self.np:]:
                    endto_p += 1
                    if c[0] == 'to':
                        depth += 1  #handle nested to
                    if c[0] == 'endto':
                        depth -= 1
                        if depth == 0:
                            self.np = endto_p
                            break
            elif op == 'endto':
                if self.calling():
                    (name, np) = self.stack.pop()  #pop local stack frame
                    self.namespace.pop()  #pop local namespace
                    self.np = np  #restore np
                #else nop, i.e. pass over end of definition
            elif op == 'call':
                #note: any nested tos will be dealt with within (same level only - further inners will be jumped over)
                ns = self.lexer.context.namespace_lookup(args[0])   #(assumes name is lowercased already)
                if ns is not None:
                    if len(self.stack) > MAX_RECURSION:
                        print "Maximum stack reached - call will be ignored (%s)" % unicode(self)
                    else:
                        self.stack.append((args[0], self.np))  #push local stack frame
                        self.namespace.append({})  #create local namespace
                        #todo pass args to function via local namespace
                        self.np = ns[args[0]]  #jump to function
                #todo else runtime error: lexer found function but no longer there (scope issue?)
                    
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


if __name__ == "__main__":
    canvas = setup_window("Logo140 - Leeds Hack 2012")
    
    #create some demo turtles
    tc1 = TurtleContext(canvas)
    tc2 = TurtleContext(canvas)
    tc3 = TurtleContext(canvas)
    tc4 = TurtleContext(canvas)
    tc5 = TurtleContext(canvas)
    tc6 = TurtleContext(canvas)
    tc7 = TurtleContext(canvas)
    tc8 = TurtleContext(canvas)
    tc9 = TurtleContext(canvas)
    tc10 = TurtleContext(canvas)
    tcs.append(tc1)
    tcs.append(tc2)
    tcs.extend([tc3, tc4, tc5])
    tcs.extend([tc6, tc7, tc8, tc9, tc10])
    
    tc1.turtle.pen(pencolor = 'blue')
    tc2.turtle.pen(pencolor = 'red')
    tc3.turtle.pen(pencolor = 'green')
    tc4.turtle.pen(pencolor = 'orange')
    tc5.turtle.pen(pencolor = 'purple')
    tc6.turtle.pen(pencolor = 'blue')
    tc7.turtle.pen(pencolor = 'red')
    tc8.turtle.pen(pencolor = 'green')
    tc9.turtle.pen(pencolor = 'orange')
    tc10.turtle.pen(pencolor = 'purple')
    tc2.turtle.left(180)
    tc3.turtle.left(90)
    tc4.turtle.left(270)
    tc5.turtle.left(230)
    tc7.turtle.left(130)
    tc8.turtle.left(40)
    tc9.turtle.left(220)
    tc10.turtle.left(190)
    
    tc1.parse('to square repeat 4 [fd 50 rt 90 square] end')

    tc1.parse('repeat 36 [ square rt 10] ')
    
    #tc1._demo()
    #tc2._demo()   
    
    s= 'repeat 20 [repeat 90[fd 6 rt 4] rt 5]'  #nested repeat
    tc1.parse(s)
    tc2.parse(s)
    tc3.parse(s)
    tc4.parse(s)
    tc5.parse(s)
    tc6.parse(s)
    tc7.parse(s)
    tc8.parse(s)
    tc9.parse(s)
    tc10.parse(s)
    

    for tc in tcs:
        print unicode(tc)
        

    reactor.run()  #no need for tk mainloop
    