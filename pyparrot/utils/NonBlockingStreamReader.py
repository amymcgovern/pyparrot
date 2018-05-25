"""
A non-blocking stream reader (used to solve the process communciation with ffmpeg)

This code is almost directly from:

http://eyalarubas.com/python-subproc-nonblock.html

Amy McGovern (dramymcgovern@gmail.com) modified to allow the thread to end nicely
and also to not throw an error if the stream ends, since our code already will know that
from parsing (and the programs are not expected to run forever)
"""

from threading import Thread
from queue import Queue, Empty
import time

class NonBlockingStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()
        self.is_running = True

        self._t = Thread(target = self._populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def _populateQueue(self, stream, queue):
        '''
        Collect lines from 'stream' and put them in 'quque'.
        '''

        while self.is_running:
            line = stream.readline()
            if line:
                queue.put(line)
            else:
                self.finish_reader()
            time.sleep(0.001)

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None

    def finish_reader(self):
        #print("Finishing the non-blocking reader")
        self.is_running = False

class UnexpectedEndOfStream(Exception): pass