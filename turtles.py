# Turtles: lots of turtles
# Leeds Hack 2012
# Monkey Tennis

import turtle
import Tkinter

from collections import deque


from twisted.internet import reactor, defer
from twisted.internet.task import cooperate, LoopingCall
from twisted.internet import tksupport

import ply.lex as lex
import ply.yacc as yacc

import lexer
import parser

import boto
import json

MAX_RECURSION = 50
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
            try:
                self.processloop.stop()
            except AssertionError:
                pass  #don't care if already stopped
            self.processloop.start(0.0000001)
            #self.process()
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
                    self.turtle.pencolor(str(self.evaluate(args[0])))
                elif op == 'repeat':
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

def setup_window(title = "Turtles"):
    #setup canvas and make it play nicely with Twisted
    root = Tkinter.Tk() 
    canvas = Tkinter.Canvas(root,width=800,height=600)
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

def dispatcher():
    sms = get_sms()
    o = json.loads(sms)
    try:
        sms_id = o.get('to')[0]
    except IndexError:
        pass
        
if __name__ == "__main__":
    canvas = setup_window("Logo140 - Leeds Hack 2012")

    #create some demo turtles
    tc1 = TurtleContext(canvas)
    tc2 = TurtleContext(canvas)
    tc3 = TurtleContext(canvas)
    tc4 = TurtleContext(canvas)
    tc5 = TurtleContext(canvas)
    
    tcs['1'] = tc1
    tcs['2'] = tc2
    tcs['3'] = tc3
    tcs['4'] = tc4
    tcs['5'] = tc5

    tc6 = TurtleContext(canvas)
    tc7 = TurtleContext(canvas)
    tc8 = TurtleContext(canvas)
    tc9 = TurtleContext(canvas)
    tc10 = TurtleContext(canvas)
    
    tc1.parse('setpc blue')
    tc2.parse('setpc red')
    tc3.parse(u'setpc green')
    tc4.parse('setpc orange')
    tc5.parse('setpc purple')
    tc6.parse('setpc blue')
    tc7.parse('setpc red')
    tc8.parse('setpc green')
    tc9.parse('setpc orange')
    tc10.parse('setpc purple')
    tc2.turtle.left(180)
    tc3.turtle.left(90)
    tc4.turtle.left(270)
    tc5.turtle.left(230)
    tc7.turtle.left(130)
    tc8.turtle.left(40)
    tc9.turtle.left(220)
    tc10.turtle.left(190)

    #tc1.parse('to square repeat 4 [fd 50 rt 90] end')
    ##tc1.parse('to square repeat 4 [fd 50 rt 90 square] end')   #recursive
    ##tc1.parse('square')
    ##tc1.parse('repeat 36 [ square rt 10] ')
    #tc1.parse('to flower repeat 36 [rt 10 square] end')
    #tc1.parse('flower')  #nested function call

    s= 'repeat 10 [REpEAT 90[fd 4 rt 4] rt 36]'  #nested repeat
    tc1.parse(s)
    tc2.parse(s)
    tc3.parse(s)
    
    #s = 'repeat 10 [ pu  fd 5 pd fd 5 ]'   #dotted
    s = 'FD 50 setpc magenta fd 50'   
    tc4.parse(s)
    
    #s = 'repeat 18 [repeat 5 [rt 40 fd 100 rt 120] rt 20]'
    #tc5.parse(s)
    
    #s = 'repeat 36 [repeat repcount [repeat repcount [fd repcount lt 15] home] lt 1]'  #growing (may want to stop before done)
    #s= 'repeat 36 [repeat 36 [fd 10 rt 10] fd repcount rt 90 fd repcount]'
    tc6.parse(s)
    
    #s='repeat 12 [repeat 75 [fd 100 bk 100 rt 2] fd 250]'  #fanflower
    #tc7.parse(s)
    
    #s = 'repeat 8 [repeat 4 [rt 90 fd 100] bk 100 lt 45]'  #hypercube
    #tc8.parse(s)
    
    #s = 'repeat 100 [ fd repcount  rt 90 ]'  #todo repcount*2
    #tc9.parse(s)
    
    #s = 'to SAWTOOTH  rt   45   fd 56   lt    135   fd 40  rt   90  end'
    #tc10.parse(s)
    #s= 'to SAWBLADE repeat 12 [ SAWTOOTH rt 30 ] end'
    #tc10.parse(s)
    #s = 'SAWBLADE'
    #tc10.parse(s)
    

    for tc in tcs:
        print unicode(tcs[tc])

    reactor.run()  #no need for tk mainloop
    