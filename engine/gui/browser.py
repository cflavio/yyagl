from sys import platform
from os import environ, system
from webbrowser import open_new_tab


class Browser(object):

    @staticmethod
    def init_cls():
        return BrowserLinux if platform.startswith('linux') else Browser

    @staticmethod
    def open(url):
        open_new_tab(url)


class BrowserLinux(Browser):

    @staticmethod
    def open(url):
        environ['LD_LIBRARY_PATH'] = ''
        system('xdg-open ' + url)
