import glob
import json
import libtmux
import os
import subprocess

from stitch_helper import services


ICONS = {
    "emacs": chr(0xe001),
    "shell": chr(0xe002),
    "service": chr(0xe003),
    "db": chr(0xe004),
    "watch": chr(0xe005),
    "test": chr(0xe006),
}


def vm_up():
    result = subprocess.call(
        "ssh -t core 'echo up'",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    return result == 0


def start_core_vm():
    if not vm_up():
        subprocess.call("make up", cwd=os.path.expanduser("~/git/boxcutter"), shell=True)

        if not vm_up():
            raise Exception("Unable to connect to core vm")

        subprocess.call("ssh -t core /bin/bash -ic 'run-all'", shell=True)


class Tmux:
    def __init__(self):
        self.tmux = libtmux.Server()
        try:
            self.tmux.list_sessions()
        except:
            print("Starting new tmux server")
            subprocess.call(
                "tmux new -s temp -d",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            self.tmux = libtmux.Server()

        start_core_vm()

    @property
    def current_session(self):
        for session in self.tmux.list_sessions():
            if session.get("session_attached") == "1":
                return session

        return None

    @property
    def current_window(self):
        for window in self.current_session.list_windows():
            if window.get("window_active") == "1":
                return window

        return None

    @property
    def current_pane(self):
        for pane in self.current_window.list_panes():
            if pane.get("pane_active") == "1":
                return pane

    @property
    def attached(self):
        return self.current_session is not None

    def has_session(self, name):
        return self.tmux.has_session(name)

    def new_window(self, session, pwd, name, cmds):
        window = session.new_window(ICONS.get(name, name))
        pane = window.panes[0]
        pane.send_keys("ssh core")
        pane.send_keys("cd {}".format(pwd))
        for cmd in cmds:
            pane.send_keys(cmd)

        return window

    def new_session(self, service):
        session = self.tmux.new_session(service.name)

        session.set_environment("STITCH_CODE_DIR", service.code_dir)
        if service.nrepl:
            session.set_environment("STITCH_NREPL_PORT", service.nrepl)

        if service.cider_version:
            session.set_environment("STITCH_CIDER_VERSION", service.cider_version)

        self.new_window(session, service.pwd, "shell", [])
        for window_name, window_cmds in service.windows:
            self.new_window(session, service.pwd, window_name, window_cmds)

        emacs = session.new_window(ICONS["emacs"])
        emacs.panes[0].send_keys("emacs")
        session.kill_window(1)
        emacs.move_window(1)
        return session

    def session(self, service):
        if not self.has_session(service.name):
            self.new_session(service)

        if self.has_session("temp"):
            self.tmux.kill_session("temp")

        if self.attached:
            self.tmux.switch_client(service.name)
