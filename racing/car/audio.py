from yyagl.gameobject import AudioColleague
from yyagl.engine.audio import AudioSound


class CarSounds(object):

    def __init__(self, engine, brake, crash, crash_hs, lap, landing, pitstop,
                 rocket_fired, rocket_hit, turbo, rotate_all_fired,
                 rotate_all_hit):
        self.engine = engine
        self.brake = brake
        self.crash = crash
        self.crash_hs = crash_hs
        self.lap = lap
        self.landing = landing
        self.pitstop = pitstop
        self.rocket_fired = rocket_fired
        self.rocket_hit = rocket_hit
        self.turbo = turbo
        self.rotate_all_fired = rotate_all_fired
        self.rotate_all_hit = rotate_all_hit


class AbsAudioUpdate(object):

    def __init__(self, engine_sfx, brake_sfx):
        self.engine_sfx = engine_sfx
        self.brake_sfx = brake_sfx

    def update(self, skidmarking, speed_ratio, input_, drifting, flying,
               rolling):
        pass

    def destroy(self): self.engine_sfx = self.brake_sfx = None


class CountDownAudioUpdate(AbsAudioUpdate):

    def __init__(self, engine_sfx, brake_sfx):
        AbsAudioUpdate.__init__(self, engine_sfx, brake_sfx)
        self.curr_eng_ratio = 0

    def update(self, skidmarking, speed_ratio, input_, drifting, flying,
               rolling):
        incr = 1.0 * globalClock.getDt()
        self.curr_eng_ratio += incr if input_.forward else -incr
        self.curr_eng_ratio = min(1, max(0, self.curr_eng_ratio))
        self.engine_sfx.set_volume(max(.4, abs(self.curr_eng_ratio)))
        self.engine_sfx.set_play_rate(max(.4, abs(self.curr_eng_ratio)))


class RaceAudioUpdate(AbsAudioUpdate):

    def update(self, skidmarking, speed_ratio, input_, drifting, flying,
               rolling):
        brk_playing = self.brake_sfx.playing
        if speed_ratio > .4:
            skidmarking = skidmarking or drifting
        if drifting and not skidmarking and speed_ratio > .4:
            self.brake_sfx.set_volume((speed_ratio - .4) / .8)
        else:
            self.brake_sfx.set_volume(1)
        if skidmarking and not brk_playing and not flying and not rolling:
            self.brake_sfx.play()
        elif brk_playing and (not skidmarking or (flying or rolling)):
            self.brake_sfx.stop()
        gear_thresholds = [0, .3, .6, .8, .9]
        thr = max(gtr for gtr in gear_thresholds if speed_ratio >= gtr)
        idx = gear_thresholds.index(thr)
        up_ = 1 if idx == len(gear_thresholds) - 1 else gear_thresholds[idx + 1]
        gear_ratio = (speed_ratio - thr) / (up_ - thr)
        self.engine_sfx.set_volume(.4 + .6 * speed_ratio)
        play_rate = speed_ratio - .1 + .2 * gear_ratio
        self.engine_sfx.set_play_rate(max(.1, abs(play_rate)))


class CarAudio(AudioColleague):

    def on_play(self): pass


class CarPlayerAudio(CarAudio):

    def __init__(self, mediator, props):
        CarAudio.__init__(self, mediator)
        self.engine_sfx = AudioSound(props.sounds.engine)
        self.brake_sfx = AudioSound(props.sounds.brake)
        self.crash_sfx = AudioSound(props.sounds.crash)
        self.crash_high_speed_sfx = AudioSound(props.sounds.crash_hs)
        self.lap_sfx = AudioSound(props.sounds.lap)
        self.landing_sfx = AudioSound(props.sounds.landing)
        self.pitstop_sfx = AudioSound(props.sounds.pitstop)
        self.rocket_fired_sfx = AudioSound(props.sounds.rocket_fired)
        self.rocket_hit_sfx = AudioSound(props.sounds.rocket_hit)
        self.turbo_sfx = AudioSound(props.sounds.turbo)
        self.rotate_all_fired_sfx = AudioSound(props.sounds.rotate_all_fired)
        self.rotate_all_hit_sfx = AudioSound(props.sounds.rotate_all_hit)
        list(map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx]))
        self.engine_sfx.set_volume(0)
        self.engine_sfx.play()
        self.update_state = CountDownAudioUpdate(self.engine_sfx,
                                                 self.brake_sfx)

    def on_play(self):
        self.update_state.destroy()
        self.update_state = RaceAudioUpdate(self.engine_sfx, self.brake_sfx)

    def update(self, is_skidmarking, speed_ratio, input_, is_drifting,
               is_flying, is_rolling):
        self.update_state.update(
            is_skidmarking, speed_ratio, input_, is_drifting, is_flying,
            is_rolling)

    def destroy(self):
        self.update_state.destroy()
        effects = [
            self.engine_sfx, self.brake_sfx, self.crash_sfx,
            self.crash_high_speed_sfx, self.lap_sfx, self.landing_sfx,
            self.pitstop_sfx, self.rocket_fired_sfx, self.rocket_hit_sfx,
            self.turbo_sfx, self.rotate_all_fired_sfx,
            self.rotate_all_hit_sfx]
        list(map(lambda sfx: sfx.stop(), effects))
        AudioColleague.destroy(self)
