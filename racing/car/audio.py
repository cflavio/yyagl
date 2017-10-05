from collections import namedtuple
from panda3d.core import AudioSound as PAudioSound
from yyagl.gameobject import Audio
from yyagl.engine.audio import AudioSound


__sounds = 'engine brake crash crash_hs lap landing pitstop rocket_fired ' + \
    'rocket_hit turbo rotate_all_fired rotate_all_hit'


CarSounds = namedtuple('CarSounds', __sounds)


class AbsAudioUpdate:

    def __init__(self, engine_sfx, brake_sfx):
        self.engine_sfx = engine_sfx
        self.brake_sfx = brake_sfx

    def update(): pass

    def destroy(self): self.engine_sfx = self.brake_sfx = None


class CountDownAudioUpdate(AbsAudioUpdate):

    def __init__(self, engine_sfx, brake_sfx):
        AbsAudioUpdate.__init__(self, engine_sfx, brake_sfx)
        self.curr_eng_ratio = 0

    def update(self, is_skidmarking, speed_ratio, input):
        incr = 1.0 * globalClock.getDt()
        self.curr_eng_ratio += incr if input.forward else -incr
        self.curr_eng_ratio = min(1, max(0, self.curr_eng_ratio))
        self.engine_sfx.set_volume(max(.4, abs(self.curr_eng_ratio)))
        self.engine_sfx.set_play_rate(max(.4, abs(self.curr_eng_ratio)))


class RaceAudioUpdate(AbsAudioUpdate):

    def update(self, is_skidmarking, speed_ratio, input):
        is_brk_playing = self.brake_sfx.is_playing()
        if is_skidmarking and not is_brk_playing:
            self.brake_sfx.play()
        elif not is_skidmarking and is_brk_playing:
            self.brake_sfx.stop()
        gear_thresholds = [0, .3, .6, .8, .9]
        thr = max(gtr for gtr in gear_thresholds if speed_ratio >= gtr)
        idx = gear_thresholds.index(thr)
        up = 1 if idx == len(gear_thresholds) - 1 else gear_thresholds[idx + 1]
        gear_ratio = (speed_ratio - thr) / (up - thr)
        self.engine_sfx.set_volume(.4 + .6 * speed_ratio)
        play_rate = speed_ratio - .1 + .2 * gear_ratio
        self.engine_sfx.set_play_rate(max(.1, abs(play_rate)))


class CarAudio(Audio):

    def on_play(self): pass


class CarPlayerAudio(CarAudio):

    def __init__(self, mdt, props):
        CarAudio.__init__(self, mdt)
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
        map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx])
        self.engine_sfx.set_volume(0)
        self.engine_sfx.play()
        self.update_state = CountDownAudioUpdate(self.engine_sfx, self.brake_sfx)

    def on_play(self):
        self.update_state.destroy()
        self.update_state = RaceAudioUpdate(self.engine_sfx, self.brake_sfx)

    def update(self, is_skidmarking, speed_ratio, input):
        self.update_state.update(is_skidmarking, speed_ratio, input)

    def destroy(self):
        self.update_state.destroy()
        self.engine_sfx.stop()
        Audio.destroy(self)
