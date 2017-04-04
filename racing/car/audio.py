from panda3d.core import AudioSound
from yyagl.gameobject import Audio


class CarAudioProps:

    def __init__(self, engine, brake, crash, crash_hs, lap, landing):
        self.engine = engine
        self.brake = brake
        self.crash = crash
        self.crash_hs = crash_hs
        self.lap = lap
        self.landing = landing


class CarAudio(Audio):

    def __init__(self, mdt, props):
        Audio.__init__(self, mdt)
        self.engine_sfx = loader.loadSfx(props.engine)
        self.brake_sfx = loader.loadSfx(props.brake)
        self.crash_sfx = loader.loadSfx(props.crash)
        self.crash_high_speed_sfx = loader.loadSfx(props.crash_hs)
        self.lap_sfx = loader.loadSfx(props.lap)
        self.landing_sfx = loader.loadSfx(props.landing)
        map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx])
        self.engine_sfx.set_volume(0)
        self.engine_sfx.play()

    def update(self, input_dct):  # use on_frame (independent from caller)
        playing = self.brake_sfx.status() == AudioSound.PLAYING
        if self.mdt.logic.is_skidmarking and not playing:
            self.brake_sfx.play()
        elif not self.mdt.logic.is_skidmarking and playing:
            self.brake_sfx.stop()
        self.engine_sfx.set_volume(max(.25, abs(self.mdt.phys.speed_ratio)))
        self.engine_sfx.set_play_rate(max(.25, abs(self.mdt.phys.speed_ratio)))

    def destroy(self):
        self.engine_sfx.stop()
        Audio.destroy(self)
