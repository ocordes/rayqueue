"""

app/auth/terminal.py

written by: Oliver Cordes 2019-03-30
changed by: Oliver Cordes 2019-04-10


"""


"""

This code part is adopted from:

https://pypi.org/project/pyxtermjs/

pyxtermjs version 0.4.0.1 by Chad Smith grassfedcode@gmail.com

"""


from flask import current_app

import pty
import os
import subprocess
import select
import termios
import struct
import fcntl
import shlex
import signal

import sys


from app import db, socketio


def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack('HHHH', row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output(app):
    max_read_bytes = 1024 * 20
    running = True
    while running:
        socketio.sleep(0.01)
        with app.app_context():
            if app.config['fd']:
                timeout_sec = 0
                (data_ready, _, _) = select.select([app.config['fd']], [], [], timeout_sec)
                if data_ready:
                    output = os.read(app.config['fd'], max_read_bytes).decode()
                    socketio.emit('pty-output', {'output': output}, namespace='/pty')
            else:
                # break the loop
                msg = 'Stop the backgroud pty forward loop!'
                current_app.logger.info(msg)
                running = False



@socketio.on('pty-input', namespace='/pty')
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if current_app.config['fd']:
        # print("writing to ptd: %s" % data["input"])
        try:
            os.write(current_app.config['fd'], data['input'].encode())
        except:
            # clean the child, so it will be in zombie mode!
            msg = 'Close the connection to childpid={}'.format(current_app.config['child_pid'])
            current_app.logger.info(msg)
            os.waitpid(current_app.config['child_pid'], os.WNOHANG)
            current_app.config['child_pid'] = None
            current_app.config['fd'] = None



@socketio.on('resize', namespace='/pty')
def resize(data):
    if current_app.config['fd']:
        set_winsize(current_app.config['fd'], data['rows'], data['cols'])



@socketio.on('connect', namespace='/pty')
def connect():
    """new client connected"""

    if current_app.config['child_pid']:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        print('Starting subcommand %s ...' % current_app.config['CMD'])
        print('Using pid %i ...' % os.getpid() )
        sys.stdout.flush()
        subprocess.run(current_app.config['CMD'])
        with open('blubber.dat', 'w') as f:
            f.write('child is dead')
        print('Exit the child!')
        sys.stdout.flush()
        #sys.exit(0)
        #sys.stdin.close()
        #sys.stdout.close()
        #sys.stderr.close()
        os.kill(os.getpid(), signal.SIGKILL)
        os._exit(0)  # quit the child process  leaves the process as zombie ...
        print('Immer noch da!')
        sys.stdout.flush()
    else:
        # this is the parent process fork.
        # store child fd and pid
        msg = 'Create a child process pid={}'.format(child_pid)
        current_app.logger.info(msg)

        # copy the data to the app context
        current_app.config['fd'] = fd
        current_app.config['child_pid'] = child_pid
        set_winsize(fd, 50, 50)
        #cmd = " ".join(shlex.quote(c) for c in current_app.config["cmd"])
        cmd = current_app.config['CMD']
        #print('child pid is', child_pid)
        #print(
        #    f'starting background task with command `{cmd}` to continously read '
        #    'and forward pty output to client'
        #)
        socketio.start_background_task(target=read_and_forward_pty_output,
                                        app=current_app._get_current_object())
        #print('task started')
