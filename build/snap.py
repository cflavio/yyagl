import tarfile, os, shutil
from os.path import exists, abspath
from yyagl.build.linux import _do_bld
from yyagl.build.deployng import bld_ng
from yyagl.build.build import bld_dpath, InsideDir


def bld_snap(target, source, env, version, branch, summary, desc):
    ico_fpath = env['ICO_FPATH']
    bld_ng(env['APPNAME'], linux=True)
    start_dir = abspath('.') + '/'
    if exists(bld_dpath + 'linux'): shutil.rmtree(bld_dpath + 'linux')
    os.makedirs(bld_dpath + 'linux')
    with InsideDir(bld_dpath + 'linux'):
        _do_bld(start_dir, env['APPNAME'], ico_fpath, False)
    with InsideDir(bld_dpath + 'linux/img/data'):
        os.system('tar -xvf pdata.tar.xz')
    __do_snap(env['APPNAME'], version, branch, summary, desc)
    shutil.rmtree('linux')
    shutil.rmtree('snap')
    os.remove('yorg.zip')


snapcraft_yaml = '''name: {appname}
version: {version}
summary: {summary}
description: {desc}
confinement: devmode
base: core18
grade: devel

parts:
  {appname}:
    plugin: dump
    source: {appname}.zip
    source-type: zip
    stage-packages:
      - libreadline5
      - libglu1-mesa
      - libgl1
      - libglx0
      - i965-va-driver
      - libgl1-mesa-dri
      - vainfo
      - mesa-vdpau-drivers
      - libvdpau1
      - mesa-utils
      - x11-utils
      - libmad0
      - libpulse0
      - libasound2

apps:
  {appname}:
    command: {appname}
    plugs:
      - desktop
      - desktop-legacy
      - unity7
      - wayland
      - x11
      - opengl
      - audio-playback
      - pulseaudio
      - alsa
      - browser-support
      - home
      - gsettings
      - network
    environment:
      LD_LIBRARY_PATH: "$LD_LIBRARY_PATH:$SNAP/usr/lib/$SNAPCRAFT_ARCH_TRIPLET:$SNAP/usr/lib/$SNAPCRAFT_ARCH_TRIPLET/pulseaudio:/var/lib/snapd/lib/gl"
      MESA_GLSL_CACHE_DIR: "$SNAP_USER_DATA"
      LIBGL_DRIVERS_PATH: "$SNAP/usr/lib/$SNAPCRAFT_ARCH_TRIPLET/dri"

layout:
  /usr/share/alsa:
    bind: $SNAP/usr/share/alsa'''


def __do_snap(appname, version, branch, summary, desc):
    os.chdir('built')
    if exists(appname): shutil.rmtree(appname)
    if exists('snap'): shutil.rmtree('snap')
    if exists(appname + '.zip'): os.remove(appname + '.zip')
    os.system('multipass delete --purge snapcraft-' + appname)
    os.system('snapcraft clean')
    # with tarfile.open('%s-%s-linux_amd64.tar.xz' % (appname, branch)) as f:
    #     f.extractall('.')
    # os.system('cd %s ; zip -r ../%s.zip * ; cd ..' % (appname, appname))
    os.chdir('linux/img/data')
    shutil.make_archive('../../../%s' % appname, 'zip', '.')
    os.chdir('../../..')
    os.system('snapcraft init')
    syaml = snapcraft_yaml.format(
        appname=appname, version=version, summary=summary, desc=desc)
    with open('snap/snapcraft.yaml', 'w') as f: f.write(syaml)
    os.system('snapcraft')


# sudo snap install appname_version_amd64.snap --devmode --dangerous
# $ appname
# sudo snap remove appname
