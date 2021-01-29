from pathlib import Path
import sys
if '' in sys.path: sys.path.remove('')
sys.path.append(str(Path(__file__).parent.parent.parent))
from unittest import TestCase
from panda3d.core import loadPrcFileData
from yyagl.engine.engine import Engine
from yyagl.engine.joystick import JoystickMgr, JoystickState
from yyagl.engine.gui.menu import NavInfoPerPlayer


class EngineJoystickTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')
        self.eng = Engine()

    def tearDown(self): self.eng.destroy()

    def test_init(self):
        self.assertIsInstance(self.eng.joystick_mgr, JoystickMgr)

    def test_get_joystick(self):
        j_state = self.eng.joystick_mgr.get_joystick(0)
        self.assertIsInstance(j_state, JoystickState)
        self.assertEqual(j_state.x, 0)
        self.assertEqual(j_state.y, 0)
        self.assertEqual(j_state.b0, 0)
        self.assertEqual(j_state.b1, 0)
        self.assertEqual(j_state.b2, 0)
        self.assertEqual(j_state.b3, 0)
        self.assertEqual(j_state.dpad_l, 0)
        self.assertEqual(j_state.dpad_r, 0)
        self.assertEqual(j_state.dpad_u, 0)
        self.assertEqual(j_state.dpad_d, 0)
        self.assertEqual(j_state.trigger_l, 0)
        self.assertEqual(j_state.trigger_r, 0)
        self.assertEqual(j_state.shoulder_l, 0)
        self.assertEqual(j_state.shoulder_r, 0)
        self.assertEqual(j_state.stick_l, 0)
        self.assertEqual(j_state.stick_r, 0)

    def test_get_joystick_val(self):
        jmgr = self.eng.joystick_mgr
        self.assertEqual(jmgr.get_joystick_val(0, 'face_x'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'face_y'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'face_a'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'face_b'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'dpad_l'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'dpad_r'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'dpad_u'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'dpad_d'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'trigger_l'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'trigger_r'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'shoulder_l'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'shoulder_r'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'stick_l'), 0)
        self.assertEqual(jmgr.get_joystick_val(0, 'stick_r'), 0)

    def test_bind_keyboard(self):
        nav_info = [NavInfoPerPlayer(
            'raw-arrow_left', 'raw-arrow_right', 'raw-arrow_up',
            'raw-arrow_down', 'raw-rcontrol')]
        self.eng.joystick_mgr.bind_keyboard(nav_info)
        self.assertEqual(self.eng.joystick_mgr.nav[0].fire, 'raw-rcontrol')
        self.eng.joystick_mgr.unbind_keyboard(0)
        self.assertIsNone(self.eng.joystick_mgr.nav[0], None)
