from collections import namedtuple

__fields = 'menu_args cars_names drivers season_tracks tracks_tr ' + \
    'track_img player_name drivers_img cars_img car_path phys_path '


GameProps = namedtuple('GameProps', __fields)