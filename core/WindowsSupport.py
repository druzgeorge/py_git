#imports
import os
from pygit import DESKTOP
import os
import shelve 
from colorit import *
from pathlib import Path
import shutil
import subprocess

class WindowsSupport(object):
    WINDOWS_GIT_PATH = ''
    git = ''
    def __init__(self, activate=False, argument=None, argument_content=None):
        self.activate = activate
        if self.activate == False:
            print('Windows Support disabled')
        print('Windows Support Activated')
        if not WindowsSupport.retrieve_windows_git_path("git"):
            print('git not found on windows system.')
            sys.exit(1)
        WindowsSupport.recognize_commands(self, self.argument, self.argument_content)
    #boolean function
    def retrieve_windows_git_path(executable):
        if os.path.sep in executable:
            raise ValueError("Invalid filename: %s" % executable)
        path = os.environ.get("PATH", "").split(os.pathsep)
        # PATHEXT tells us which extensions an executable may have
        path_exts = os.environ.get("PATHEXT", ".exe;.bat;.cmd").split(";")
        has_ext = os.path.splitext(executable)[1] in path_exts
        if not has_ext:
            exts = path_exts
        else:
            # Don't try to append any extensions
            exts = [""]

        for d in path:
            try:
                for ext in exts:
                    exepath = os.path.join(d, executable + ext)
                    if os.access(exepath, os.X_OK):
                        WINDOWS_GIT_PATH += exepath
                        git += exepath
                        return True
            except OSError:
                return False

        return False
    def recognize_commands(self, argument, argument_content):
        self.argument = argument
        self.argument_content = argument_content
        print(self.argument, self.argument_content)
        #redirecting to respective function
        if self.argument == 'masterDir':
            WindowsSupport.index_master(self.argument_content)
        elif self.argument == 'automate_actions':
            WindowsSupport.automate_actions(action=self.argument_content)
        elif self.argument == 'clone':
            WindowsSupport.clone(url=self.argument_content)
        elif self.argument == 'init':
            WindowsSupport.init(cwd=self.argument_content)
        elif  self.argument == 'push':
            WindowsSupport.push(path=os.getcwd())
        elif self.argument == 'set_global_credentials':
            print(self.argument_content)
            WindowsSupport.set_globals(self.argument_content)
        elif self.argument == 'add':
            WindowsSupport.add(self.argument_content)

    @staticmethod
    def automate_actions(action, commit_msg="new changes"):
        #todo: set actions to all possible automate actions
        actions = ['push']
        #if the action in actions ? redirect to distinct func : return error
        if action in actions:
            if action == 'push':
                subprocess.Popen('{0} pull'.format(git))
                subprocess.Popen("{0} add .".format(git))
                subprocess.Popen("{0} status".format(git))
                subprocess.Popen(f"{git} commit -m '{commit_msg}.Pushed with automate_actions'")
                WindowsSupport.push(path=os.getcwd())
        else:
            return "Unknown action {}".format(action)

    @staticmethod
    def add(mode):
        if mode == '.':
            print('Add all mode.Resulting to git.')
            subprocess.Popen(f"{git} add .")
        print("Adding {} to index...".format(mode))
        subprocess.Popen(f"{git} add {mode}")
        print('done')
        return

    @staticmethod
    def set_globals(username_password):
        #todo: fix yes or no query
        #todo: fix b'globalcredentials' KeyError problem
        #spliting username_password into a list separated by ','
        credentials = str(username_password).split('/')
        #making sure coloit will be usable in commandline interfaces
        sg.theme('SandyBeach')
        layout = [
            [sg.Text("This is very dangerous!")],
            [sg.Text("Setting credentials to global is efficent but insecure.\nYour information will be stored in "
                          f"{SHELF_DIR} as a shelve file.\nYou can proceed but it is advised to "
                          f"setup SSH keys for your github to avoid using this.\nRead this:'https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account'"
                          )],
            [sg.Text("Do you wish to continue?")],
            [sg.Yes(), sg.No()]
                        
        ]
        window = sg.Window('WARNING', layout)
        event, values = window.read()
        window.close()
        # print(color_front("This is very dangerous!", red=255, green=0, blue=0))
        # print(color_front("Setting credentials to global is efficent but insecure.\nYour information will be stored in "
        #                   f"{SHELF_DIR} as a shelve file.\nYou can proceed but it is advised to "
        #                   f"setup SSH keys for your github to avoid using this.\nRead this:{color_front('https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account', red=0, green=255, blue=0)}"
        #                   , red=255, green=0, blue=0))
        opt = event
        opt = opt.lower()
        if opt ==  "yes":
            print("Working...")
            try:
                Commands.safe_mkdir(SHELF_DIR)
                print('credentials', credentials)
                # so password is gloablcredentilas[1] and username is [0]
                Commands.shelfer(key='global_credentials', content=credentials)
            except FileExistsError:
                shutil.rmtree(SHELF_DIR)
                Commands.safe_mkdir(SHELF_DIR)
                # so password is gloablcredentilas[1] and username is [0]
                Commands.shelfer(key='global_credentials', content=credentials)
            print("Done...")
            return
        elif opt == 'no':
            print(color_front("Aborted!", red=255, green=0, blue=0))
            print(color_front(f"Read: https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account ", red=0, green=150, blue=240) ,color_front("On how to perform adding SSH key to account", 255,255,255))
            sys.exit(1)
        else:
            print('error!')
            sys.exit(1)
    @staticmethod
    def init(cwd):
        os.chdir(cwd)
        subprocess.Popen(f"{git} init")
        print("initialised git!")
        return
    @staticmethod
    def index_master(path_to_master_local_repo):
        os.chdir(path_to_master_local_repo)
        WindowsSupport.init(cwd=os.getcwd())
        WindowsSupport.shelfer(key="master_repo", content=path_to_master_local_repo)
        print('MasterIndexed')
        return
    @staticmethod
    def clone(url, path=DESKTOP):
        print("Cloning to Desktop")
        cwd = os.getcwd()
        os.chdir(path)
        subprocess.Popen(f"{git} clone {url}")
        os.chdir(cwd)
        return
    @staticmethod
    def push(path):
        print("Pushing new code")
        subprocess.Popen(f"{git} push")
    @staticmethod
    def safe_mkdir(path):
        print("Initialised safe_mkdir()\n Making dir in safe mode.")
        if not os.path.exists(path):
            os.mkdir(path)
            print("Directory successfully created at {}".format(path))
            return
        shutil.rmtree(path)
        os.mkdir(path)
        print("Directory successfully created at {}".format(path))
        return
    @staticmethod
    def shelfer(key="masterKey", content=None):
        shelve_file_path = os.path.join(str(SHELF_DIR), 'pygit_shelve')
        shelfobj = shelve.open(shelve_file_path)
        shelfobj[key] = content
        shelfobj.close()
        return

    