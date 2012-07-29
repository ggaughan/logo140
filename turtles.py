# Turtles: lots of turtles
# Leeds Hack 2012
# Monkey Tennis

import turtle
import Tkinter

from collections import deque
import random

from twisted.internet import reactor, defer
from twisted.internet.task import cooperate, LoopingCall
from twisted.internet import tksupport

import ply.lex as lex
import ply.yacc as yacc

import lexer
import parser

import boto
import json

LONG_NUMBER = "07624 809318"
MAX_RECURSION = 50

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

TURTLE_SPEED = 5  #1=slowest, 10=fast (0=no anim = fastest)
TURTLE_DEMO_SPEED = 8  #1=slowest, 10=fast (0=no anim = fastest)

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
        self.parsing = None  #last parsed
        self.lexer = lex.lex(module=lexer)
        self.lexer.context = self  #reverse reference, so lexer can access current namespaces
        self.parser = parser.parser

        #namespaces
        self.namespace = deque()
        self.namespace.append({})  #globals  #todo define some!
        self.namespace.append({})  #locals  #function locals will be added and removed at runtime

        #stack frames
        self.stack = deque()
        
        #parsed
        self.commands = []  #program steps
        self.np = 0  #index to next program step
        self.repeat_counters = deque()
        
        #action
        self.turtle = LogoTurtle(canvas)
        
        self.processloop = LoopingCall(self.process)
    
    def __unicode__(self):
        return "parsed=(%s)\nnp=%s\nlast parsed=(%s)" % (self.commands, self.np, self.parsing)
    
    def namespace_lookup(self, name):
        """Find which namespace the name is in, starting with locals first then working outwards
           return None if not found
        """
        for ns in self.namespace:
            if name in ns:
                return ns
    
    def parse(self, s):
        self.parsing = s
        new_commands = self.parser.parse(self.parsing, lexer=self.lexer)
        if new_commands is not None:
            self.commands.extend(new_commands)
            try:
                self.processloop.stop()
            except AssertionError:
                pass  #don't care if already stopped
            self.processloop.start(0.0000001)
            #self.process()
        #else possibly syntax error
    
    def calling(self):
        """Returns True if we are currently in a function call"""
        return len(self.stack) > 0
    
    def reset_stacks(self):
        self.stack.clear()
        while len(self.namespace) > 2:
            self.namespace.pop()
        self.repeat_counters.clear()
    
    def evaluate(self, expression):
        """Runtime evaluation"""
        if expression == 'repcount':
            return self.repeat_counters[-1][0]  #latest count
        else:
            return expression
    
    def process(self):
        """Process the next command"""
        if self.np < len(self.commands):
            command = self.commands[self.np]
            self.np += 1
            op, args = command[0], command[1:]
            op = op.lower()  #something wrong here: fix parser!
            try:
                if op == 'fd':
                    self.turtle.forward(self.evaluate(args[0]))
                elif op == 'bk':
                    self.turtle.backward(self.evaluate(args[0]))
                elif op == 'rt':
                    self.turtle.right(self.evaluate(args[0]))
                elif op == 'lt':
                    self.turtle.left(self.evaluate(args[0]))
                elif op == 'home':
                    self.turtle.home()
                elif op == 'pu':
                    self.turtle.penup()
                elif op == 'pd':
                    self.turtle.pendown()
                elif op == 'setpc':
                    try:
                        self.turtle.pencolor(str(self.evaluate(args[0])))
                    except:
                        print "Failed setting pencolor to %s" % str(self.evaluate(args[0]))
                        #continue
                elif op == 'repeat':
                    #todo limit size?
                    self.repeat_counters.append((self.evaluate(args[0]), self.np))  #push start
                elif op == 'endrepeat':
                    (counter, np) = self.repeat_counters.pop()  #pop latest
                    counter -= 1
                    if counter > 0:
                        self.repeat_counters.append((counter, np))  #push back
                        self.np = np  #again
                    #else done, continue
                elif op == 'to':
                    self.namespace[0][args[0].lower()] = self.np  #declare name + start point in locals (assumes name is lowercased already)
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
                            print "Maximum stack reached - existing commands will terminate (%s)" % unicode(self)
                            #also (for now) we skip all current commands
                            self.reset_stacks()
                            self.np = len(self.commands)
                        else:
                            self.stack.append((args[0], self.np))  #push local stack frame
                            self.namespace.append({})  #create local namespace
                            #todo pass args to function via local namespace
                            self.np = ns[args[0]]  #jump to function
                    #todo else runtime error: lexer found function but no longer there (scope issue?)
                        
                #todo etc.
                else:
                    #todo
                    print "I don't know how to %s" % op
            except Exception, e:
                print "Exception " + unicode(e)
                #carry on
        #else nothing to do (until the next parse at least)
        else:
            self.processloop.stop()
    
tcs = {}    

def draw_headings(canvas):
    tutorTurtle = TurtleContext(canvas)
    tutorTurtle.turtle.penup()
    
    tutorTurtle.turtle.goto(-395,260)
    tutorTurtle.turtle.write("Text your LOGO commands to your turtle at", 
                             True, align="left", font=("Arial", 14, "bold"))
    tutorTurtle.turtle.pencolor('red')
    tutorTurtle.turtle.write(" %s" % LONG_NUMBER, 
                             True, align="left", font=("Arial", 14, "bold italic"))    
    tutorTurtle.turtle.pencolor('black')
    
    tutorTurtle.turtle.goto(-395,240)
    tutorTurtle.turtle.write("Commands:", 
                             True, align="left", font=("Arial", 12, "italic bold"))
    
    tutorTurtle.turtle.goto(-380,220)
    tutorTurtle.turtle.write("FD n  LT n  RT n  BK n  HOME",
                             True, align="left", font=("Courier New", 11, "normal"))
    tutorTurtle.turtle.goto(-380,204)
    tutorTurtle.turtle.write("REPEAT n [", 
                             True, align="left", font=("Courier New", 11, "normal"))
    tutorTurtle.turtle.write(" commands ", 
                             True, align="left", font=("Courier New", 11, "italic"))    
    tutorTurtle.turtle.write("]", 
                             True, align="left", font=("Courier New", 11, "normal"))
    tutorTurtle.turtle.goto(-380,188)
    tutorTurtle.turtle.write("TO", 
                             True, align="left", font=("Courier New", 11, "normal"))
    tutorTurtle.turtle.write(" x ", 
                             True, align="left", font=("Courier New", 11, "bold"))    
    tutorTurtle.turtle.write(" commands ", 
                             True, align="left", font=("Courier New", 11, "italic"))    
    tutorTurtle.turtle.write("END", 
                             True, align="left", font=("Courier New", 11, "normal"))
    tutorTurtle.turtle.goto(-380,172)
    tutorTurtle.turtle.write("PU  PD  SETPC colour", 
                             True, align="left", font=("Courier New", 11, "normal"))
    
    EXAMPLE_SCRIPT = "TO square REPEAT 4 [FD 20 RT 90] END   REPEAT 9 [square RT 40]"
    
    tutorTurtle.turtle.goto(-395,152)
    tutorTurtle.turtle.write("Example:", 
                             True, align="left", font=("Arial", 12, "italic bold"))
    tutorTurtle.turtle.goto(-380,132)
    tutorTurtle.turtle.write(EXAMPLE_SCRIPT, 
                             True, align="left", font=("Courier New", 10, "normal"))
    tutorTurtle.turtle.hideturtle()
    
    tutorTurtle.turtle.showturtle()
    tutorTurtle.turtle.goto(+20,210)
    tutorTurtle.turtle.pendown()
    tutorTurtle.turtle.pensize(2)
    tutorTurtle.turtle.speed(TURTLE_DEMO_SPEED)
    tutorTurtle.turtle.pencolor('green')
    tutorTurtle.parse(EXAMPLE_SCRIPT)
    tutorTurtle.turtle.hideturtle()

    del tutorTurtle
    

def setup_window(title = "Turtles"):
    #setup canvas and make it play nicely with Twisted
    root = Tkinter.Tk() 
    canvas = Tkinter.Canvas(root,width=WINDOW_WIDTH,height=WINDOW_HEIGHT)
    canvas.pack(side = Tkinter.LEFT)

    tksupport.install(root)
   
    root.title(title)
    draw_headings(canvas)
    
    root.protocol('WM_DELETE_WINDOW', reactor.stop)
    
    return canvas



class Dispatcher(object):

    def __init__(self, **kwargs):
        self.canvas = kwargs.get('canvas')
        self.sqs = boto.connect_sqs()
        
    def get_sms(self):
        m_data = []
        q = self.sqs.get_queue('logo140')
        m = q.read()
        if m:
            m_data = m.get_body()
            m.delete()
        return m_data 
    
    def dispatcher(self):
        sms = self.get_sms()
        
        if sms:
            sms_id = ''        
            o = json.loads(sms)
            try:
                sms_id = o.get('from')[0]
            except IndexError:
                pass
        
            turtle = tcs.get(sms_id)
            content = ' '.join(o.get('content'))
            
            if turtle:
                turtle.parse(content)
            else:
                tc = TurtleContext(self.canvas)
                tc.turtle.pencolor(random.random(), random.random(), random.random())
                tc.turtle.fillcolor(random.random(), random.random(), random.random())
                tc.parse(content)
                tcs.update({sms_id: tc})
        
       
        
        
                
if __name__ == "__main__":
    canvas = setup_window("Logo140 - Leeds Hack 2012")
    
    dispatcher = Dispatcher(canvas=canvas)
    l = LoopingCall(dispatcher.dispatcher)
    l.start(5.0)        

    reactor.run()  #no need for tk mainloop
    