from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from os import getcwd, makedirs
from os.path import basename
from shutil import rmtree
from unittest import TestCase
from re import compile
from yyagl.build.build import InsideDir, files, size, exec_cmd, set_path, \
    _branch, _version, img_tgt_names, tracks_tgt_fnames


class BuildTests(TestCase):

    def setUp(self):
        makedirs('test_get_files/a')
        makedirs('test_get_files/b')
        makedirs('test_get_files/c')
        with open('test_get_files/a/c.ext1', 'w') as f:
            f.write('0123456789')
        open('test_get_files/a/d.ext2', 'w')
        with open('test_get_files/b/e.ext2', 'w') as f:
            f.write('0123456789')
        open('test_get_files/b/f.ext3', 'w')
        open('test_get_files/c/g.ext2', 'w')

    def tearDown(self):
        rmtree('test_get_files')

    def test_exec_cmd(self):
        self.assertEqual(exec_cmd('echo abc'), 'abc')

    def test_branch(self):
        self.assertIn(_branch(), ['master', 'testing', 'stable'])

    def test_version(self):
        pattern = compile("^[0-9]+\.[0-9]+\.[0-9]+\-[a-z0-9]+$")
        self.assertTrue(pattern.match(_version()))

    def test_img_tgt_names(self):
        files = ['/home/flavio/img.png', 'flavio/folder/img.jpg',
                 './folder/img.gif', 'img.bmp']
        expected = ['/home/flavio/img.txo', 'flavio/folder/img.txo',
                 './folder/img.txo', 'img.txo']
        self.assertEqual(expected, img_tgt_names(files))

    def test_tracks_tgt_fnames(self):
        tracks_tmpl ='../assets/tracks/%s/models/track_all.bam'
        tracks = ['dubai', 'orlando', 'moon', 'sheffield', 'nagano', 'rome', 'toronto']
        cars_tmpl = [
            '../assets/cars/%s/models/cardamage1.bam',
            '../assets/cars/%s/models/cardamage2.bam',
            '../assets/cars/%s/models/capsule.bam',
            '../assets/cars/%s/models/car.bam']
        cars = ['iapeto', 'teia', 'phoibe', 'themis', 'iperion', 'kronos', 'rea', 'diones']
        expected = [tracks_tmpl % track for track in tracks]
        expected += [ctl % car for ctl in cars_tmpl for car in cars]
        self.assertTrue(all(exp in tracks_tgt_fnames() for exp in expected))

    def test_path(self):
        self.assertEqual(set_path('abc'), 'abc/')
        self.assertEqual(set_path('abc/'), 'abc/')

    def test_get_files(self):
        _files = files(['ext2'], 'c')
        self.assertSetEqual(set(_files),
                            set(['./test_get_files/a/d.ext2',
                                 './test_get_files/b/e.ext2']))

    def test_get_size(self):
        self.assertEqual(size('test_get_files'), 20)

    def test_inside_dir(self):
        self.assertNotEqual(basename(getcwd()), 'tests')
        with InsideDir('tests'):
            self.assertEqual(basename(getcwd()), 'tests')
        self.assertNotEqual(basename(getcwd()), 'tests')
