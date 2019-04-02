"""

app/auth/terminal.py

written by: Oliver Cordes 2019-03-30
changed by: Oliver Cordes 2019-04-02


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

import sys


from app import db, socketio


def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output(app):
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        with app.app_context():
            if app.config["fd"]:
                timeout_sec = 0
                (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
                if data_ready:
                    output = os.read(app.config["fd"], max_read_bytes).decode()
                    socketio.emit("pty-output", {"output": output}, namespace="/pty")



@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if current_app.config["fd"]:
        # print("writing to ptd: %s" % data["input"])
        os.write(current_app.config["fd"], data["input"].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    if current_app.config["fd"]:
        set_winsize(current_app.config["fd"], data["rows"], data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""

    if current_app.config["child_pid"]:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        print('Starting subcommand %s ...' % current_app.config["cmd"])
        subprocess.run(current_app.config["cmd"])
        print('Exit the child!')
        print(current_app.config["child_pid"])
        #sys.exit(0)
        #os._exit(0)
    else:
        # this is the parent process fork.
        # store child fd and pid
        current_app.config["fd"] = fd
        current_app.config["child_pid"] = child_pid
        set_winsize(fd, 50, 50)
        cmd = " ".join(shlex.quote(c) for c in current_app.config["cmd"])
        print("child pid is", child_pid)
        print(
            f"starting background task with command `{cmd}` to continously read "
            "and forward pty output to client"
        )
        socketio.start_background_task(target=read_and_forward_pty_output,
                                        app=current_app._get_current_object())
        print("task started")
