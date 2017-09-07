from .menu import LoadingMenu


class Loading(object):

    def enter_loading(self, rprops, track_name_transl, drivers):
        self.menu = LoadingMenu(rprops, self, track_name_transl,
                                drivers)

    def exit_loading(self):
        self.menu.destroy()
