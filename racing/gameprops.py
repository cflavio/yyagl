from collections import namedtuple

__fields = 'menu_args cars_names drivers_info season_tracks tracks_tr ' + \
    'track_img player_name drivers_img cars_img car_path phys_path model_name ' + \
    'damage_paths wheel_gfx_names xmpp_debug'


GameProps = namedtuple('GameProps', __fields)
