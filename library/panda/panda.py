from ..library import Library


class LibraryPanda3D(Library):

    @property
    def runtime(self):
        return base.appRunner

    @property
    def build_version(self):
        package = base.appRunner.p3dInfo.FirstChildElement('package')
        #  first_child_element not in panda3d.core.TiXmlDocument
        return package.Attribute('version')
        #  attribute not in panda3d.core.TiXmlDocument

    @property
    def curr_path(self):
        return base.appRunner.p3dFilename.get_dirname()
