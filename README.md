logo140
=======

Leeds Hack 2012 entry

Logo140 allows users to collaboratively draw a picture by texting Logo turtle
commands to a central number (using mediaburst's SMS API), e.g. "FD 50 RT 90" 
would move forward 50 and then right-turn 90 degrees.

The Logo commands are sent via Google App Engine to an Amazon queue where they 
are picked and processed by the application. Each user gets their own turtle, 
based on their phone number, and the application can move multiple turtles at 
once.

The implemented Logo language supports turtle movement, loops, named functions, 
nested function calls and limited recursion, with local and global variable 
scoping. A more complex example is:

    TO sawtooth  RT 45  FD 56   LT 135  FD 40  RT 90  END
    TO sawblade REPEAT 12 [ sawtooth rt 30 ] END
    TO eyeball REPEAT 36 [ sawblade rt 10] END
    eyeball


requirements
------------
 * sudo aptitude install python-tk package
 * pip install twisted
 * pip install ply
 * pip install boto
