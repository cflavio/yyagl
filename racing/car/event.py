from itertools import chain
from panda3d.core import Vec3, Vec2
from direct.showbase.InputStateGlobal import inputState
from yyagl.gameobject import Event
from yyagl.racing.race.event import NetMsgs
from yyagl.racing.weapon.rocket.rocket import Rocket


class InputDctBuilder:  # maybe a visitor?

    @staticmethod
    def build(state, joystick):
        if state == 'Results':
            return InputDctBuilderAi()
        elif joystick:
            return InputDctBuilderJoystick()
        else:
            return InputDctBuilderKeyboard()


class InputDctBuilderAi(InputDctBuilder):

    def build_dct(self, ai, has_weapon):
        return ai.get_input()


class InputDctBuilderKeyboard(InputDctBuilder):

    def build_dct(self, ai, has_weapon):
        keys = ['forward', 'left', 'reverse', 'right']
        return {key: inputState.isSet(key) for key in keys}


class InputDctBuilderJoystick(InputDctBuilder):

    def build_dct(self, ai, has_weapon):
        x, y, a, b = eng.event.joystick.get_joystick()
        if b and has_weapon:
            self.on_fire()
        return {'forward': y < -.4, 'reverse': y > .4 or a,
                'left': x < -.4, 'right': x > .4}


class CarEventProps:

    def __init__(self, keys, joystick, rocket_path, respawn_name,
                 pitstop_name, road_name, wall_name, goal_name, bonus_name,
                 roads_names):
        self.keys = keys
        self.joystick = joystick
        self.rocket_path = rocket_path
        self.respawn_name = respawn_name
        self.pitstop_name = pitstop_name
        self.road_name = road_name
        self.wall_name = wall_name
        self.goal_name = goal_name
        self.bonus_name = bonus_name
        self.roads_names = roads_names


class CarEvent(Event):

    def __init__(self, mdt, carevent_props):
        Event.__init__(self, mdt)
        eng.attach_obs(self.on_collision)
        self.props = carevent_props
        keys = carevent_props.keys
        self.label_events = [
            ('forward', keys['forward']), ('left', keys['left']),
            ('reverse', keys['rear']), ('right', keys['right'])]
        watch = inputState.watchWithModifiers
        self.toks = map(lambda (lab, evt): watch(lab, evt), self.label_events)

    def start(self):
        eng.attach_obs(self.on_frame)

    def on_collision(self, obj, obj_name):
        if obj == self.mdt.gfx.nodepath.node():
            if obj_name.startswith(self.props.respawn_name):
                self.__process_respawn()
            if obj_name.startswith(self.props.pitstop_name):
                self.mdt.gui.apply_damage(True)
                self.mdt.phys.apply_damage(True)
                self.mdt.gfx.apply_damage(True)

    def __process_respawn(self):
        start_wp_n, end_wp_n = self.mdt.logic.last_wp
        self.mdt.gfx.nodepath.setPos(start_wp_n.get_pos() + (0, 0, 2))
        wp_vec = Vec3(end_wp_n.getPos(start_wp_n).xy, 0)
        wp_vec.normalize()
        or_h = (wp_vec.xy).signedAngleDeg(Vec2(0, 1))
        self.mdt.gfx.nodepath.setHpr(-or_h, 0, 0)
        self.mdt.gfx.nodepath.node().setLinearVelocity(0)
        self.mdt.gfx.nodepath.node().setAngularVelocity(0)

    def on_frame(self):
        input_dct = self._get_input()
        if self.mdt.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            input_dct = {key: False for key in input_dct}
            self.mdt.logic.reset_car()
        self.mdt.logic.update(input_dct)
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)
        self.__update_contact_pos()
        self.mdt.phys.update_car_props()
        self.mdt.logic.update_waypoints()

    def __update_contact_pos(self):
        car_pos = self.mdt.gfx.nodepath.get_pos()
        top = (car_pos.x, car_pos.y, car_pos.z + 50)
        bottom = (car_pos.x, car_pos.y, car_pos.z - 50)
        hits = eng.ray_test_all(top, bottom).getHits()
        road_n = self.props.road_name
        for hit in [hit for hit in hits if road_n in hit.getNode().getName()]:
            self.mdt.logic.last_wp = self.mdt.logic.closest_wp()

    def destroy(self):
        eng.detach_obs(self.on_collision)
        eng.detach_obs(self.on_frame)
        map(lambda tok: tok.release(), self.toks)
        Event.destroy(self)


class CarPlayerEvent(CarEvent):

    def __init__(self, mdt, carevent_props):
        CarEvent.__init__(self, mdt, carevent_props)
        if not eng.is_runtime:
            self.accept('f11', self.mdt.gui.toggle)
        self.has_weapon = False
        state = self.mdt.fsm.getCurrentOrNextState()
        self.input_dct_bld = InputDctBuilder.build(state,
                                                   carevent_props.joystick)

    def on_frame(self):
        CarEvent.on_frame(self)
        self.mdt.logic.camera.update(self.mdt.phys.speed_ratio,
                                     self.mdt.logic.is_rolling)
        self.mdt.audio.update(self._get_input())

    def on_collision(self, obj, obj_name):
        CarEvent.on_collision(self, obj, obj_name)
        if obj != self.mdt.gfx.nodepath.node():
            return
        if obj_name.startswith(self.props.wall_name):
            self.__process_wall()
        if any(obj_name.startswith(s) for s in self.props.roads_names):
            eng.audio.play(self.mdt.audio.landing_sfx)
        if obj_name.startswith(self.props.goal_name):
            self.__process_goal()
        if obj_name.startswith(self.props.bonus_name):
            self.on_bonus()

    def on_bonus(self):
        if not self.mdt.logic.weapon:
            self.mdt.logic.weapon = Rocket(self.mdt, self.props.rocket_path)
            self.accept(self.props.keys['button'], self.on_fire)
            self.has_weapon = True

    def on_fire(self):
        self.ignore(self.props.keys['button'])
        self.mdt.logic.fire()
        self.has_weapon = False

    def _on_crash(self):
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            self.mdt.gfx.crash_sfx()

    def __process_wall(self):
        eng.play(self.mdt.audio.crash_sfx)
        self._on_crash()

    def __process_nonstart_goals(self, lap_number, laps):
        curr_lap = min(laps, lap_number)
        self.mdt.gui.lap_txt.setText(str(curr_lap)+'/'+str(laps))
        eng.play(self.mdt.audio.lap_sfx)

    def _process_end_goal(self):
        self.notify('on_end_race')

    def __process_goal(self):
        if self.mdt.logic.last_time_start and not self.mdt.logic.correct_lap:
            return
        self.mdt.logic.reset_waypoints()
        lap_times = self.mdt.logic.lap_times
        is_best = not lap_times or min(lap_times) > self.mdt.logic.lap_time
        if self.mdt.logic.last_time_start and (not lap_times or is_best):
            self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
        if self.mdt.logic.last_time_start:
            lap_times += [self.mdt.logic.lap_time]
            self.__process_nonstart_goals(1 + len(lap_times), self.mdt.laps)
        self.mdt.logic.last_time_start = globalClock.getFrameTime()
        if len(lap_times) == self.mdt.laps:
            self._process_end_goal()

    def _get_input(self):
        return self.input_dct_bld.build_dct(self.mdt.ai, self.has_weapon)

    def destroy(self):
        map(self.ignore, ['f11', self.props.keys['button']])
        CarEvent.destroy(self)


class CarPlayerEventServer(CarPlayerEvent):

    def __init__(self, mdt):
        CarPlayerEvent.__init__(self, mdt)

    def _process_end_goal(self):
        eng.server.send([NetMsgs.end_race])
        CarPlayerEvent._process_end_goal(self)


class CarPlayerEventClient(CarPlayerEvent):

    def __init__(self, mdt):
        CarPlayerEvent.__init__(self, mdt)
        self.last_sent = globalClock.getFrameTime()

    def on_frame(self):
        CarPlayerEvent.on_frame(self)
        pos = self.mdt.gfx.nodepath.getPos()
        hpr = self.mdt.gfx.nodepath.getHpr()
        velocity = self.mdt.phys.vehicle.getChassis().getLinearVelocity()
        packet = list(chain([NetMsgs.player_info], pos, hpr, velocity))
        if globalClock.getFrameTime() - self.last_sent > .2:
            eng.client.send(packet)
            self.last_sent = globalClock.getFrameTime()

    def _process_end_goal(self):
        eng.client.send([NetMsgs.end_race_player])
        CarPlayerEvent._process_end_goal(self)


class CarNetworkEvent(CarEvent):

    def _get_input(self):
        return {key: False for key in ['forward', 'left', 'reverse', 'right']}


class CarAiEvent(CarEvent):

    def _get_input(self):
        return self.mdt.ai.get_input()


class CarAiPlayerEvent(CarAiEvent, CarPlayerEvent):

    pass
