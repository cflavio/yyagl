from os import system, remove, chdir, getcwd, rename, walk
from os.path import exists
from shutil import move, rmtree, copytree, copy
from distutils.dir_util import copy_tree
from .build import ver, bld_dir, branch, bld_cmd
from .deployng import build_ng


nsi_src = '''Name {fullName}
OutFile {outFile}
InstallDir "$PROGRAMFILES\\{fullName}"
SetCompress auto
SetCompressor lzma
ShowInstDetails nevershow
ShowUninstDetails nevershow
InstType "Typical"
RequestExecutionLevel admin
Function launch
  ExecShell "open" "$INSTDIR\\{shortName}.exe"
FunctionEnd
!include "MUI2.nsh"
!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_FUNCTION launch
!define MUI_FINISHPAGE_RUN_TEXT "Run Yorg"
Function finishpageaction
CreateShortcut "$DESKTOP\\{shortName}.lnk" "$INSTDIR\\{shortName}.exe"
FunctionEnd
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION finishpageaction
Var StartMenuFolder
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
!insertmacro MUI_LANGUAGE "English"
Section "" SecCore
{installFiles}
WriteUninstaller "$INSTDIR\\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\\$StartMenuFolder\\{fullName}.lnk"\
      "$INSTDIR\\{shortName}.exe" "" "$INSTDIR\\{iconFile}"
    CreateShortCut "$SMPROGRAMS\\$StartMenuFolder\\Uninstall.lnk" \
      "$INSTDIR\\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd
Section Uninstall
  Delete "$INSTDIR\\{shortName}.exe"
  {uninstallFiles}
  Delete "$INSTDIR\\Uninstall.exe"
  RMDir /r "$INSTDIR"
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$DESKTOP\\{shortName}.lnk"
  Delete "$SMPROGRAMS\\$StartMenuFolder\\Uninstall.lnk"
  Delete "$SMPROGRAMS\\$StartMenuFolder\\{fullName}.lnk"
  RMDir "$SMPROGRAMS\\$StartMenuFolder"
SectionEnd'''


class TempFile:

  def __init__(self, fName, text):
      self.fName, self.text = fName, text

  def __enter__(self):
      with open(self.fName, 'w') as outFile:
          outFile.write(self.text)

  def __exit__(self, exc_type, exc_val, exc_tb):
      remove(self.fName)


class InsideDir:

  def __init__(self, _dir):
      self.dir = _dir

  def __enter__(self):
      self.oldDir = getcwd()
      chdir(self.dir)

  def __exit__(self, exc_type, exc_val, exc_tb):
      chdir(self.oldDir)


def build_windows(target, source, env):
    if env['NG']:
        build_ng(env['APPNAME'], win=True)
        return
    internet_switch = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    bld_command = bld_cmd.format(
        path=bld_dir, name=env['APPNAME'], Name=env['APPNAME'].capitalize(),
        version=ver, p3d_path=env['P3D_PATH'][:-4] + 'nopygame.p3d',
        platform='win_i386', nointernet=internet_switch)
    system(bld_command)
    with InsideDir('%swin_i386' % bld_dir):
        fileName = '{Name} {version}.exe'.format(
            Name=env['APPNAME'].capitalize(), version=ver)
        system('7z x -owinInstaller %s' % fileName.replace(' ', '\\ '))
        remove(fileName)
        with InsideDir('winInstaller'):
            copytree('../../../yyagl/licenses', './licenses')
            copy_tree('../../../licenses', './licenses')  # it already exists
            copy('../../../license.txt', './license.txt')
            if exists('./panda3d/cmu_1.9/win_i386/panda3d/'):
                src = '../../../yyagl/assets/core.pyd'
                copy(src, './panda3d/cmu_1.9/win_i386/panda3d/core.pyd')
            rename('$PLUGINSDIR', 'NSIS Plugins Directory')
            copytree('../../../assets', './assets')
            copytree('../../../yyagl/assets', './yyagl/assets')
            for root, dirnames, filenames in walk('./assets'):
                for filename in filenames:
                    fname = root + '/' + filename
                    rm_ext = ['psd', 'po', 'pot', 'egg']
                    if any(fname.endswith('.' + ext) for ext in rm_ext):
                        remove(fname)
                    if 'assets/models/tracks/' in fname and \
                            fname.endswith('.bam') and not \
                            any(fname.endswith(concl + '.bam')
                                for concl in ['/track', '/collision', 'Anim']):
                        remove(fname)
            installFiles = ''.join(
                ['\nSetOutPath "$INSTDIR\\%s"\n' % root[2:].replace('/','\\') +
                 '\n'.join(['File ".\\%s\\%s"' % (root[2:].replace('/','\\'),
                                                  name)
                            for name in files])
                 for root, dirs, files in walk('.')])
            uninstallFiles = '\n'.join(
                'Delete "$INSTDIR\\%s\\%s"' % (root[2:].replace('/','\\'),
                                               name)
                                       for root, dirs, files in walk('.')
                                       for name in files)
            nsi_src_inst = nsi_src.format(
                fullName=env['APPNAME'].capitalize(),
                outFile='{name}-{version}{int_str}-windows.exe'.format(
                    name=env['APPNAME'], version=branch, int_str=int_str),
                shortName=env['APPNAME'],
                iconFile=env['APPNAME'] + '.ico',
                installFiles = installFiles,
                uninstallFiles = uninstallFiles)
            with TempFile('installer.nsi', nsi_src_inst):
                system( 'makensis installer.nsi' )
    src = '{path}win_i386/winInstaller/{name}-{version}{int_str}-windows.exe'
    tgt_file = '{path}{name}-{version}{int_str}-windows.exe'
    src_fmt = src.format(
        path=bld_dir, name=env['APPNAME'], version=branch, int_str=int_str)
    tgt_fmt = tgt_file.format(
        path=bld_dir, name=env['APPNAME'], version=branch, int_str=int_str)
    move(src_fmt, tgt_fmt)
    rmtree('%swin_i386' % bld_dir)
