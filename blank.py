from twisted.internet import reactor
from twisted.internet.task import cooperate, LoopingCall

from turtles import setup_window, draw_headings, TurtleContext, Dispatcher

if __name__ == "__main__":
    canvas = setup_window("Logo140, Collaborative Art Installation - Leeds Hack 2012")
    draw_headings(canvas)

    
    dispatcher = Dispatcher()
    l = LoopingCall(dispatcher.dispatcher)
    l.start(5.0)        

    reactor.run()  #no need for tk mainloop
    