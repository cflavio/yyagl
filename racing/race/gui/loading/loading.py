from .menu import LoadingMenu


class Loading(object):

    def enter_loading(self, rprops, sprops, track_name_transl, drivers):
        self.menu = LoadingMenu(rprops, sprops, self, track_name_transl, drivers)

    def exit_loading(self):
        self.menu.destroy()
