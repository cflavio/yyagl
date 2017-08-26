from collections import namedtuple


__fields = 'keys joystick sounds color_main color font coll_path ' + \
    'coll_name car_path phys_file wheel_names road_name model_name ' + \
    'damage_paths wheel_gfx_names particle_path drivers shaders_dev ' + \
    'shaders music_path coll_track_path unmerged merged ghosts ' + \
    'corner_names wp_info show_waypoints weapon_info start track_name ' + \
    'track_path track_model_name empty_name anim_name omni_tag sign_cb ' + \
    'sign_name minimap_path minimap_image col_dct camera_vec shadow_src ' + \
    'laps rocket_path turbo_path rotate_all_path mine_path bonus_model ' + \
    'bonus_suff cars a_i ingame_menu menu_args drivers_img cars_imgs ' + \
    'share_urls share_imgs respawn_name pitstop_name wall_name goal_name ' + \
    'bonus_name roads_names grid player_car_name'


RaceProps = namedtuple('RaceProps', __fields)
