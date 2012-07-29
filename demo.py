from twisted.internet import reactor
from twisted.internet.task import cooperate, LoopingCall
import random

from turtles import setup_window, draw_headings, TurtleContext, Dispatcher

if __name__ == "__main__":
    canvas = setup_window("Logo140, Collaborative Art Installation - Leeds Hack 2012")

    #create some demo turtles
    fanflower = 'repeat 12 [repeat 75 [fd 60 bk 60 rt 2] fd 130]'
    tc1 = TurtleContext(canvas)
    tc1.turtle.pencolor(random.random(), random.random(), random.random())
    tc1.turtle.fillcolor(random.random(), random.random(), random.random())
    tc1.parse(fanflower)

    tc2 = TurtleContext(canvas)
    tc2.turtle.pencolor(random.random(), random.random(), random.random())
    tc2.turtle.fillcolor(random.random(), random.random(), random.random())
    tc2.parse('pu fd 10 rt 90 fd 10 rt 90 pd')
    tc2.parse(fanflower)
    
    
    dispatcher = Dispatcher(canvas=canvas)
    l = LoopingCall(dispatcher.dispatcher)
    l.start(5.0)        

    reactor.run()  #no need for tk mainloop
    