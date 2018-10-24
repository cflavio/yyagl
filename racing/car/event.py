from random import uniform, choice
from itertools import chain
from panda3d.core import Vec3, Vec2
from direct.showbase.InputStateGlobal import inputState
from yyagl.gameobject import EventColleague
from yyagl.racing.race.event import NetMsgs, wpnclasses2id
from yyagl.racing.weapon.rocket.rocket import Rocket, RocketNetwork
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket, RearRocketNetwork
from yyagl.racing.weapon.turbo.turbo import Turbo, TurboNetwork
from yyagl.racing.weapon.rotate_all.rotate_all import RotateAll
from yyagl.racing.weapon.mine.mine import Mine, MineNetwork
from yyagl.computer_proxy import ComputerProxy, once_a_frame
from yyagl.engine.vec import Vec


class Keys(object):

    def __init__(self, forward, rear, left, right, fire, respawn, pause):
        self.forward = forward
        self.rear = rear
        self.left = left
        self.right = right
        self.fire = fire
        self.respawn = respawn
        self.pause = pause


class DirKeys(object):

    def __init__(self, forward, rear, left, right):
        self.forward = forward
        self.rear = rear
        self.left = left
        self.right = right


class InputBuilder(object):

    @staticmethod
    def create(state, joystick):
        if state == 'Results':
            return InputBuilderAi()
        elif joystick:
            return InputBuilderJoystick()
        else:
            return InputBuilderKeyboard()


class InputBuilderAi(InputBuilder):

    def build(self, ai, joystick_mgr):
        return ai.get_input()


class InputBuilderKeyboard(InputBuilder):

    def build(self, ai, joystick_mgr):
        keys = ['forward', 'rear', 'left', 'right']
        return DirKeys(*[inputState.isSet(key) for key in keys])


class InputBuilderJoystick(InputBuilder):

    def build(self, ai, joystick_mgr):
        j_x, j_y, j_a, j_b = joystick_mgr.get_joystick()
        if j_b and self.mediator.logic.weapon:
            self.on_fire()
        inp = {'forward': j_y < -.4, 'rear': j_y > .4 or j_a,
               'left': j_x < -.4, 'right': j_x > .4}
        keys = ['forward', 'rear', 'left', 'right']
        return DirKeys(*[inp[key] for key in keys])


class CarEvent(EventColleague, ComputerProxy):

    def __init__(self, mediator, race_props, yorg_client):
        EventColleague.__init__(self, mediator)
        ComputerProxy.__init__(self)
        self.eng.attach_obs(self.on_collision)
        self.props = race_props
        keys = race_props.keys
        self.label_events = [
            ('forward', keys.forward), ('left', keys.left),
            ('rear', keys.rear), ('right', keys.right)]
        watch = inputState.watchWithModifiers
        self.toks = map(lambda (lab, evt): watch(lab, evt), self.label_events)
        self.curr_wpn_id = 0

    def start(self):
        self.eng.attach_obs(self.on_frame)

    def on_collision(self, obj, tgt_obj):
        if obj != self.mediator.gfx.nodepath.get_node():
            return
        obj_name = tgt_obj.get_name()
        if obj_name.startswith(self.props.respawn_name):
            self.process_respawn()
        if obj_name.startswith(self.props.pitstop_name):
            self.mediator.phys.apply_damage(True)
            self.mediator.gfx.apply_damage(True)
            self.mediator.event.on_damage(0)
        if obj_name.startswith(self.props.goal_name):
            self._process_goal()
        obst_names = [self.props.wall_name, 'Vehicle']
        if any(obj_name.startswith(name) for name in obst_names):
            self._process_wall()
        if obj_name.startswith(self.props.bonus_name):
            self.on_bonus()
        weapons = ['Mine']
        if any(obj_name.startswith(wpn_name) for wpn_name in weapons):
            int_lat = 10000
            int_rot = 20000
            self.mediator.phys.pnode.apply_central_force((choice([-int_lat, int_lat]), choice([-int_lat, int_lat]), 96000))
            self.mediator.phys.pnode.apply_torque((0, 0, choice([-int_rot, int_rot])))

    def on_bonus(self, cls=None, wpn_id=None):
        if self.mediator.logic.weapon:
            self.mediator.logic.weapon.destroy()
        if cls == 'remove':
            self.mediator.logic.weapon = None
            self.ignore(self.props.keys.fire)
            return
        if cls: wpn_cls = cls
        else:
            wpn_classes = [Rocket, RearRocket, Turbo, RotateAll, Mine]
            probs = [.2, .2, .2, .1, .2]
            sel = uniform(0, sum(probs))
            for i, _ in enumerate(wpn_classes):
                if sum(probs[:i]) <= sel <= sum(probs[:i + 1]):
                    wpn_cls = wpn_classes[i]
        part_path = self.props.particle_path
        wpn2path = {
            Rocket: self.props.rocket_path,
            RocketNetwork: self.props.rocket_path,
            RearRocket: self.props.rocket_path,
            RearRocketNetwork: self.props.rocket_path,
            Turbo: self.props.turbo_path,
            TurboNetwork: self.props.turbo_path,
            RotateAll: self.props.rotate_all_path,
            Mine: self.props.mine_path,
            MineNetwork: self.props.mine_path}
        path = wpn2path[wpn_cls]
        self.mediator.logic.weapon = wpn_cls(
            self.mediator, path, self.props.season_props.car_names, part_path, wpn_id or self.curr_wpn_id)
        self.curr_wpn_id += 1
        self.mediator.logic.weapon.attach_obs(self.on_rotate_all)
        return wpn_cls

    def on_rotate_all(self, sender):
        self.notify('on_rotate_all', sender)

    def _on_crash(self):
        if self.mediator.fsm.getCurrentOrNextState() != 'Results':
            self.mediator.gfx.crash_sfx()

    def _process_wall(self):
        self._on_crash()

    def _process_goal(self):
        is_res = self.mediator.fsm.getCurrentOrNextState() == 'Results'
        has_started = self.mediator.logic.lap_time_start
        is_corr = self.mediator.logic.correct_lap
        if is_res or has_started and not is_corr:
            return
        self.mediator.logic.reset_waypoints()
        lap_times = self.mediator.logic.lap_times
        if self.mediator.logic.lap_time_start:
            lap_times += [self.mediator.logic.lap_time]
            self._process_nonstart_goals(1 + len(lap_times), self.mediator.laps)
        self.mediator.logic.lap_time_start = self.eng.curr_time

    def _process_nonstart_goals(self, lap_number, laps):
        pass

    def process_respawn(self):
        last_wp = self.mediator.logic.last_wp
        start_wp_n, end_wp_n = last_wp.prev, last_wp.next
        self.mediator.gfx.nodepath.set_pos(start_wp_n.pos + (0, 0, 2))
        wp_vec = Vec(end_wp_n.node.get_pos(start_wp_n.node).x, end_wp_n.node.get_pos(start_wp_n.node).y, 0).normalize()
        or_h = (wp_vec.xy).signed_angle_deg(Vec2(0, 1))
        self.mediator.gfx.nodepath.set_hpr((-or_h, 0, 0))
        self.mediator.gfx.nodepath.get_node().set_linear_velocity(0)
        self.mediator.gfx.nodepath.get_node().set_angular_velocity(0)

    def on_frame(self):
        _input = self._get_input()
        if self.mediator.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            _input = DirKeys(*[False for _ in range(4)])
            self.mediator.logic.reset_car()
        self.__update_contact_pos()
        self.mediator.phys.update_car_props()
        self.mediator.logic.update_waypoints()
        self.mediator.logic.update(_input)
        if self.mediator.logic.is_upside_down:
            self.mediator.gfx.nodepath.set_r(0)

    def __update_contact_pos(self):
        top = self.mediator.pos + (0, 0, 50)
        bottom = self.mediator.pos + (0, 0, -50)
        hits = self.eng.phys_mgr.ray_test_all(top, bottom).get_hits()
        r_n = self.props.road_name
        for hit in [hit for hit in hits if r_n in hit.get_node().get_name()]:
            self.mediator.logic.last_wp = self.mediator.logic.closest_wp()

    def on_damage(self, level):
        pass

    def destroy(self):
        map(self.eng.detach_obs, [self.on_collision, self.on_frame])
        map(lambda tok: tok.release(), self.toks)
        EventColleague.destroy(self)
        ComputerProxy.destroy(self)


class CarPlayerEvent(CarEvent):

    def __init__(self, mediator, race_props, yorg_client):
        CarEvent.__init__(self, mediator, race_props, yorg_client)
        if not self.eng.is_runtime:
            self.accept('f11', self.mediator.gui.pars.toggle)
            self.accept('f8', self._process_end_goal)
        state = self.mediator.fsm.getCurrentOrNextState()
        self.input_bld = InputBuilder.create(state, race_props.joystick)
        self.accept(self.props.keys.respawn, self.process_respawn)

    def on_frame(self):
        CarEvent.on_frame(self)
        self.mediator.logic.camera.update(
            self.mediator.phys.speed_ratio, self.mediator.logic.is_rolling,
            self.mediator.fsm.getCurrentOrNextState() == 'Countdown',
            self.mediator.logic.is_rotating)
        self.mediator.audio.update(self.mediator.logic.is_skidmarking,
                              self.mediator.phys.lin_vel_ratio,
                              self._get_input(),
                              self.mediator.logic.is_drifting,
                              self.mediator.phys.is_flying,
                              self.mediator.logic.is_rolling)

    def on_collision(self, obj, tgt_obj):
        CarEvent.on_collision(self, obj, tgt_obj)
        if obj != self.mediator.gfx.nodepath.get_node():
            return
        obj_name = tgt_obj.get_name()
        if any(obj_name.startswith(s) for s in self.props.roads_names):
            self.mediator.audio.landing_sfx.play()
        if obj_name.startswith(self.props.pitstop_name):
            self.mediator.gui.panel.apply_damage(True)
            self.mediator.gfx.set_decorator('pitstop')
            self.mediator.audio.pitstop_sfx.play()
        if 'Rocket' in obj_name:
            if obj != tgt_obj.get_python_tag('car').phys.pnode:
                self.mediator.audio.rocket_hit_sfx.play()

    def on_bonus(self, wpn_cls=None):
        if self.mediator.logic.weapon:
            self.mediator.gui.panel.unset_weapon()
        wpn_cls = CarEvent.on_bonus(self, wpn_cls)
        if not wpn_cls: return  # if removing
        self.accept(self.props.keys.fire, self.on_fire)
        self.mediator.gui.panel.set_weapon(
            self.props.season_props.wpn2img[wpn_cls.__name__])
        return wpn_cls

    def on_fire(self):
        self.ignore(self.props.keys.fire)
        self.mediator.logic.fire()
        self.mediator.gui.panel.unset_weapon()
        self.ignore(self.props.keys.fire)

    def _process_wall(self):
        CarEvent._process_wall(self)
        self.mediator.audio.crash_sfx.play()

    def _process_nonstart_goals(self, lap_number, laps):
        CarEvent._process_nonstart_goals(self, lap_number, laps)
        curr_lap = min(laps, lap_number)
        self.mediator.gui.panel.lap_txt.setText(str(curr_lap)+'/'+str(laps))
        self.mediator.audio.lap_sfx.play()

    def _process_end_goal(self):
        self.notify('on_end_race')

    def _process_goal(self):
        CarEvent._process_goal(self)
        lap_times = self.mediator.logic.lap_times
        is_best = not lap_times or min(lap_times) > self.mediator.logic.lap_time
        if self.mediator.logic.lap_time_start and (not lap_times or is_best):
            self.mediator.gui.panel.best_txt.setText(
                self.mediator.gui.panel.time_txt.getText())
        if len(lap_times) == self.mediator.laps:
            self._process_end_goal()
        # self.on_bonus()  # to test weapons

    @once_a_frame
    def _get_input(self):
        return self.input_bld.build(self.mediator.ai, self.eng.joystick_mgr)

    def destroy(self):
        evts = ['f11', 'f8', self.props.keys.fire, self.props.keys.respawn]
        map(self.ignore, evts)
        CarEvent.destroy(self)


class CarPlayerEventServer(CarPlayerEvent):

    def _process_end_goal(self):
        CarPlayerEvent._process_end_goal(self)


class CarPlayerEventClient(CarPlayerEvent):

    def __init__(self, mediator, race_props, yorg_client):
        CarPlayerEvent.__init__(self, mediator, race_props, yorg_client)
        self.last_sent = self.eng.curr_time
        self.yorg_client = yorg_client

    def on_frame(self):
        CarPlayerEvent.on_frame(self)
        pos = self.mediator.pos
        fwd = render.get_relative_vector(self.mediator.gfx.nodepath.node, Vec3(0, 1, 0))
        velocity = self.mediator.phys.vehicle.get_chassis().get_linear_velocity()
        ang_vel = self.mediator.phys.vehicle.get_chassis().get_angular_velocity()
        curr_inp = self._get_input()
        inp = [curr_inp.forward, curr_inp.rear, curr_inp.left, curr_inp.right]
        eng_frc = self.mediator.phys.vehicle.get_wheel(0).get_engine_force()
        brk_frc_fwd = self.mediator.phys.vehicle.get_wheel(0).get_brake()
        brk_frc_rear = self.mediator.phys.vehicle.get_wheel(2).get_brake()
        steering = self.mediator.phys.vehicle.get_steering_value(0)
        level = 0
        curr_chassis = self.mediator.gfx.nodepath.get_children()[0]
        if self.mediator.gfx.chassis_np_low.get_name() in curr_chassis.get_name():
            level = 1
        if self.mediator.gfx.chassis_np_hi.get_name() in curr_chassis.get_name():
            level = 2
        wpn = ''
        wpn_id = 0
        wpn_pos = (0, 0, 0)
        wpn_fwd = (0, 0, 0)
        if self.mediator.logic.weapon:
            curr_wpn = self.mediator.logic.weapon
            wpn_id = curr_wpn.id
            wpn = wpnclasses2id[curr_wpn.__class__]
            wpn_pos = curr_wpn.gfx.gfx_np.node.get_pos(render)
            wpn_fwd = render.get_relative_vector(curr_wpn.gfx.gfx_np.node, Vec3(0, 1, 0))
        packet = list(chain(
            ['player_info', self.yorg_client.myid], pos, fwd, velocity,
            ang_vel, inp, [eng_frc, brk_frc_fwd, brk_frc_rear, steering],
            [level], [wpn, wpn_id], wpn_pos, wpn_fwd))
        packet += [len(self.mediator.logic.fired_weapons)]
        for i in range(len(self.mediator.logic.fired_weapons)):
            curr_wpn = self.mediator.logic.fired_weapons[i]
            wpn = wpnclasses2id[curr_wpn.__class__]
            wpn_pos = curr_wpn.gfx.gfx_np.node.get_pos(render)
            wpn_fwd = render.get_relative_vector(curr_wpn.gfx.gfx_np.node, Vec3(0, 1, 0))
            packet += chain([wpn, curr_wpn.id], wpn_pos, wpn_fwd)
        if self.eng.curr_time - self.last_sent > self.eng.client.rate:
            self.eng.client.send_udp(packet, self.yorg_client.myid)
            self.last_sent = self.eng.curr_time

    def _process_end_goal(self):
        self.eng.client.send(['end_race_player'])
        CarPlayerEvent._process_end_goal(self)


class CarNetworkEvent(CarEvent):

    @once_a_frame
    def _get_input(self):
        return self.mediator.logic.curr_network_input

    def on_bonus(self, wpn_cls=None):
        pass

    def set_fired_weapon(self, wpn_cls, wpn_pos, wpn_fwd):
        self.mediator.logic.fire()

    def unset_fired_weapon(self, wpn):
        self.mediator.logic.unset_fired_weapon(wpn)

    def set_weapon(self, wpn_cls, wpn_id):
        #if wpn_code:
        #    wpncode2cls = {
        #        'rocket': Rocket, 'rearrocket': RearRocket, 'turbo': Turbo,
        #        'rotateall': RotateAll, 'mine': Mine}
        #    wpn_cls = wpncode2cls[wpn_code]
        #else:
        #    wpn_cls = None
        CarEvent.on_bonus(self, wpn_cls, wpn_id)

    def unset_weapon(self):
        self.mediator.logic.weapon.destroy()
        self.mediator.logic.weapon = None


class CarAiEvent(CarEvent):

    @once_a_frame
    def _get_input(self):
        return self.mediator.ai.get_input()


class CarAiPlayerEvent(CarAiEvent, CarPlayerEvent):

    pass
