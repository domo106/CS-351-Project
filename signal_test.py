import time
import threading
import os
import signal

class FiveSec(threading.Thread):
    def restart(self):
        self.my_timer = time.time() + 5
    def run(self, *args):
        self.restart()
        while 1:
            time.sleep(0.1)
            if time.time() >= self.my_timer:
                break
        print("Time's up!")
        os.kill(os.getpid(), signal.SIGINT)


def main():
    try:
        t = FiveSec()
        t.daemon = True
        t.start()
        while 1:
            x = input('::> ')
            t.restart()
            print('\nYou entered %r\n' % x)
    except KeyboardInterrupt:
        print("\nDone!")

if __name__ == '__main__':
    main()