from os import system, remove, rename, walk
from os.path import exists
from shutil import move, rmtree, copytree, copy
from distutils.dir_util import copy_tree
from .build import ver, bld_dpath, branch, bld_cmd, InsideDir, TempFile
from .deployng import bld_ng


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


def bld_windows(target, source, env):
    if env['NG']:
        bld_ng(env['APPNAME'], win=True)
        return
    internet_switch = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    cmd = bld_cmd.format(
        dst_dir=bld_dpath, appname=env['APPNAME'],
        AppName=env['APPNAME'].capitalize(), version=ver,
        p3d_fpath=env['P3D_PATH'][:-4] + 'nopygame.p3d', platform='win_i386',
        nointernet=internet_switch)
    system(cmd)
    with InsideDir('%swin_i386' % bld_dpath):
        fname = '{AppName} {version}.exe'.format(
            AppName=env['APPNAME'].capitalize(), version=ver)
        system('7z x -owinInstaller %s' % fname.replace(' ', '\\ '))
        remove(fname)
        with InsideDir('winInstaller'):
            copytree('../../../yyagl/licenses', './licenses')
            copy_tree('../../../licenses', './licenses')
            copy('../../../license.txt', './license.txt')
            if exists('./panda3d/cmu_1.9/win_i386/panda3d/'):
                src = '../../../yyagl/assets/core.pyd'
                copy(src, './panda3d/cmu_1.9/win_i386/panda3d/core.pyd')
            rename('$PLUGINSDIR', 'NSIS Plugins Directory')
            copytree('../../../assets', './assets')
            copytree('../../../yyagl/assets', './yyagl/assets')
            for root, _, fnames in walk('./assets'):
                for _fname in fnames:
                    fname = root + '/' + _fname
                    rm_ext = ['psd', 'po', 'pot', 'egg']
                    if any(fname.endswith('.' + ext) for ext in rm_ext):
                        remove(fname)
                    rm_ext = ['png', 'jpg']
                    is_ext = any(fname.endswith('.' + ext) for ext in rm_ext)
                    if 'assets/models/' in fname and is_ext:
                        remove(fname)
                    is_track = 'assets/models/tracks/' in fname
                    is_bam = fname.endswith('.bam')
                    no_conv = ['/track_all', '/collision', 'Anim']
                    is_no_conv = any(fname.endswith(concl + '.bam')
                                     for concl in no_conv)
                    if is_track and is_bam and not is_no_conv:
                        remove(fname)
            files_lst = [
                '\nSetOutPath "$INSTDIR\\%s"\n' % root[2:].replace('/', '\\') +
                '\n'.join(['File ".\\%s\\%s"' % (root[2:].replace('/', '\\'),
                                                  fnm)
                           for fnm in files])
                for root, _, files in walk('.')]
            install_files = ''.join(files_lst)
            uninstall_files = '\n'.join(
                'Delete "$INSTDIR\\%s\\%s"' % (root[2:].replace('/', '\\'),
                                               fnm)
                for root, dirs, files in walk('.') for fnm in files)
            nsi_src_inst = nsi_src.format(
                fullName=env['APPNAME'].capitalize(),
                outFile='{name}-{version}{int_str}-windows.exe'.format(
                    name=env['APPNAME'], version=branch, int_str=int_str),
                shortName=env['APPNAME'],
                iconFile=env['APPNAME'] + '.ico',
                installFiles=install_files,
                uninstallFiles=uninstall_files)
            with TempFile('installer.nsi', nsi_src_inst):
                system('makensis installer.nsi')
    src = '{dst_dir}win_i386/winInstaller/{appname}-{version}{int_str}' + \
        '-windows.exe'
    tgt_file = '{dst_dir}{appname}-{version}{int_str}-windows.exe'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch, int_str=int_str)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch, int_str=int_str)
    move(src_fmt, tgt_fmt)
    rmtree('%swin_i386' % bld_dpath)
