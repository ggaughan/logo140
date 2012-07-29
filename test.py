from twisted.internet import reactor
from twisted.internet.task import cooperate, LoopingCall

from turtles import setup_window, TurtleContext, Dispatcher

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
    s='TO square REPEAT 4 [FD 30 RT 90] END REPEAT 10 [square RT 36]'
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
    

    #for tc in tcs:
    #    print unicode(tcs[tc])       
    
    #no SQS for testing
    #dispatcher = Dispatcher()
    #l = LoopingCall(dispatcher.dispatcher)
    #l.start(5.0)        

    reactor.run()  #no need for tk mainloop
    