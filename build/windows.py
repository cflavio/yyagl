from os import system, remove, rename, walk
from os.path import exists
from shutil import move, rmtree, copytree, copy
from distutils.dir_util import copy_tree
from .build import ver, bld_dpath, branch, InsideDir, TempFile
from .deployng import bld_ng


nsi_src = r'''Name {full_name}
OutFile {out_file}
InstallDir "$PROGRAMFILES\{full_name}"
InstallDirRegKey HKCU "Yorg" ""
SetCompress auto
SetCompressor lzma
ShowInstDetails nevershow
ShowUninstDetails nevershow
InstType "Typical"
RequestExecutionLevel admin
Function launch
  ExecShell "open" "$INSTDIR\{short_name}.exe"
FunctionEnd
!include "MUI2.nsh"
!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_FUNCTION launch
!define MUI_FINISHPAGE_RUN_TEXT "Run Yorg"
Function finishpageaction
CreateShortcut "$DESKTOP\{short_name}.lnk" "$INSTDIR\{short_name}.exe"\
  "" "$INSTDIR\{icon_file}"
FunctionEnd
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION finishpageaction
Var StartMenuFolder
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Yorg"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
!insertmacro MUI_LANGUAGE "English"
Section "" SecCore
{install_files}
WriteRegStr HKCU "Yorg" "" $INSTDIR
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Yorg" \
                 "DisplayName" "Yorg"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Yorg" \
                 "UninstallString" '"$INSTDIR\Uninstall.exe"'
WriteUninstaller "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\{full_name}.lnk"\
      "$INSTDIR\{short_name}.exe" "" "$INSTDIR\{icon_file}"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" \
      "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd
Section Uninstall
  Delete "$INSTDIR\{short_name}.exe"
  {uninstall_files}
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR"
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$DESKTOP\{short_name}.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\{full_name}.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  DeleteRegKey /ifempty HKCU "Yorg"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Yorg"
SectionEnd'''


def bld_windows(target, source, env):
    #if env['DEPLOYNG']:
    #    bld_ng(env['APPNAME'], win=True)
    #    return
    #internet_switch = '-s' if env['NOINTERNET'] else ''
    #int_str = '-nointernet' if env['NOINTERNET'] else ''
    #cmd = bld_cmd.format(
    #    dst_dir=bld_dpath, appname=env['APPNAME'],
    #    AppName=env['APPNAME'].capitalize(), version=ver,
    #    p3d_fpath=env['P3D_PATH'][:-4] + 'nopygame.p3d', platform='win_i386',
    #    nointernet=internet_switch)
    #system(cmd)
    bld_ng(env['APPNAME'], win=True)
    with InsideDir('%swin_amd64' % (bld_dpath + '../build/')):
        #fname = '{app_name} {version}.exe'.format(
        #    app_name=env['APPNAME'].capitalize(), version=ver)
        #system('7z x -owinInstaller %s' % fname.replace(' ', '\\ '))
        #remove(fname)
        #with InsideDir('winInstaller'):
            copytree('../../yyagl/licenses', './licenses')
            copy_tree('../../licenses', './licenses')
            copy('../../license.txt', './license.txt')
            copytree('../../assets', './assets')
            copytree('../../yyagl/assets', './yyagl/assets')
            copy('./assets/images/icon/yorg.ico', './yorg.ico')
            for root, _, fnames in walk('./assets'):
                for _fname in fnames:
                    fname = root + '/' + _fname
                    rm_ext = ['psd', 'po', 'pot', 'egg']
                    if any(fname.endswith('.' + ext) for ext in rm_ext):
                        remove(fname)
                    rm_ext = ['png', 'jpg']
                    if any(fname.endswith('.' + ext) for ext in rm_ext):
                        remove(fname)
                    is_track = 'assets/tracks/' in fname
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
            out_file_tmpl = '{name}-{version}-windows.exe'
            out_file = out_file_tmpl.format(name=env['APPNAME'],
                                            version=branch)
            nsi_src_inst = nsi_src.format(
                full_name=env['APPNAME'].capitalize(),
                out_file=out_file,
                short_name=env['APPNAME'],
                icon_file=env['APPNAME'] + '.ico',
                install_files=install_files,
                uninstall_files=uninstall_files)
            with TempFile('installer.nsi', nsi_src_inst):
                system('makensis installer.nsi')
    src = '{dst_dir}../build/win_amd64/{appname}-{version}-windows.exe'
    tgt_file = '{dst_dir}{appname}-{version}-windows.exe'
    src_fmt = src.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                         version=branch)
    tgt_fmt = tgt_file.format(dst_dir=bld_dpath, appname=env['APPNAME'],
                              version=branch)
    move(src_fmt, tgt_fmt)
    #rmtree('dist')
    rmtree('build/__whl_cache__')
    rmtree('build/win_amd64')
