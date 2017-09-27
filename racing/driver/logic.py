from yyagl.gameobject import Logic, GameObject
from yyagl.racing.car.car import Car, CarProps, CarPlayer, CarPlayerServer, \
    CarPlayerClient, NetworkCar, AiCar, AiCarPlayer


class DriverLoaderStrategy(GameObject):

    @staticmethod
    def load(cars, r_p, car_name, track, race, player_car_names, s_p, aipoller):
        if not cars: return race.fsm.demand('Countdown', s_p)
        eng = DriverLoaderStrategy.eng
        car = cars.pop(0)
        car_cls = Car
        if eng.server.is_active or eng.client.is_active:
            car_cls = NetworkCar  # if car in player_cars else Car
        no_p = car not in player_car_names
        srv_or_sng = eng.server.is_active or not eng.client.is_active
        car_cls = AiCar if no_p and srv_or_sng else car_cls
        race.logic.cars += [DriverLoaderStrategy.actual_load(
            cars, car, r_p, track, race, car_cls, player_car_names, s_p, aipoller)]

    @staticmethod
    def actual_load(cars, load_car_name, r_p, track, race, car_cls,
                    player_car_names, seas_p, aipoller):
        for _drv in r_p.drivers:
            if _drv.dprops.car_name == load_car_name:
                drv = _drv
        s_p = track.get_start_pos(r_p.grid.index(load_car_name))
        pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
        car_props = CarProps(
            r_p, load_car_name, pos, hpr,
            lambda: DriverLoaderStrategy.load(cars, r_p, load_car_name, track,
                                              race, player_car_names, seas_p, aipoller),
            race, drv.dprops.f_engine, drv.dprops.f_tires,
            drv.dprops.f_suspensions, race.track.phys.wp2prevs, aipoller)
        return car_cls(car_props)


class DriverPlayerLoaderStrategy(GameObject):

    @staticmethod
    def load(r_p, car_name, track, race, player_car_names, s_p, aipoller):
        cars = [car for car in r_p.season_props.car_names if car != car_name]
        if r_p.a_i:
            car_cls = AiCarPlayer
        else:
            car_cls = CarPlayer
            if DriverPlayerLoaderStrategy.eng.server.is_active:
                car_cls = CarPlayerServer
            if DriverPlayerLoaderStrategy.eng.client.is_active:
                car_cls = CarPlayerClient
        race.logic.player_car = DriverLoaderStrategy.actual_load(
            cars, car_name, r_p, track, race, car_cls, player_car_names, s_p, aipoller)


class DriverLogic(Logic):

    def __init__(self, mdt, driver_props):
        Logic.__init__(self, mdt)
        self.dprops = driver_props

    def to_dct(self):
        dct = {
            'img_idx': self.dprops.info.img_idx,
            'name': self.dprops.info.name,
            'speed': self.dprops.info.speed,
            'adherence': self.dprops.info.adherence,
            'stability': self.dprops.info.stability,
            'car_name': self.dprops.car_name,
            'f_engine': self.dprops.f_engine,
            'f_tires': self.dprops.f_tires,
            'f_suspensions': self.dprops.f_suspensions}
        return dct