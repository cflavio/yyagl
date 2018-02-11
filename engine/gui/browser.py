from sys import platform
from os import environ, system
from webbrowser import open_new_tab


class BrowserOpener(object):

    @staticmethod
    def open(url):
        open_new_tab(url)


class BrowserOpenerLinux(BrowserOpener):

    @staticmethod
    def open(url):
        environ['LD_LIBRARY_PATH'] = ''
        system('xdg-open ' + url)



class Browser(object):

    @staticmethod
    def open(url):
        cls = BrowserOpenerLinux if platform.startswith('linux') else \
            BrowserOpener
        cls.open(url)
