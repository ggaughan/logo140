from twisted.internet import reactor
from twisted.internet.task import cooperate, LoopingCall

from turtles import setup_window, draw_headings, TurtleContext, Dispatcher

if __name__ == "__main__":
    canvas = setup_window("Logo140, Collaborative Art Installation - Leeds Hack 2012")
    draw_headings(canvas)

    #create some demo turtles
    tc1 = TurtleContext(canvas)
    tc1.parse('setpc blue repeat 12 [repeat 75 [fd 60 bk 60 rt 2] fd 130]')  #fanflower

    
    dispatcher = Dispatcher(canvas=canvas)
    l = LoopingCall(dispatcher.dispatcher)
    l.start(5.0)        

    reactor.run()  #no need for tk mainloop
    