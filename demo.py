from twisted.internet import reactor
from twisted.internet.task import cooperate, LoopingCall

from turtles import setup_window, draw_headings, TurtleContext, Dispatcher

if __name__ == "__main__":
    canvas = setup_window("Logo140, Collaborative Art Installation - Leeds Hack 2012")
    draw_headings(canvas)

    #create some demo turtles
    tc1 = TurtleContext(canvas)
    #tc1.parse('setpc blue repeat 12 [repeat 75 [fd 100 bk 100 rt 2] fd 250]')  #fanflower
    tc1.parse('to SAWTOOTH  rt   45   fd 56   lt    135   fd 40  rt   90  end')
    tc1.parse('to SAWBLADE repeat 12 [ SAWTOOTH rt 30 ] end')
    tc1.parse('SAWBLADE')

    
    dispatcher = Dispatcher()
    l = LoopingCall(dispatcher.dispatcher)
    l.start(5.0)        

    reactor.run()  #no need for tk mainloop
    