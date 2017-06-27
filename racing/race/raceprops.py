class RaceProps(object):

    def __init__(
            self, keys, joystick, sounds, color_main, color, font, coll_path,
            coll_name, car_path, phys_file, wheel_names, tuning_engine,
            tuning_tires, tuning_suspensions, road_name, model_name,
            damage_paths, wheel_gfx_names, particle_path, drivers, shaders,
            music_path, coll_track_path, unmerged, merged, ghosts,
            corner_names, waypoint_names, show_waypoints, weapon_names, start,
            track_name, track_path, track_model_name, empty_name, anim_name,
            omni_tag, sign_cb, sign_name, minimap_path, minimap_image, col_dct,
            camera_vec, shadow_src, laps, rocket_path, turbo_path, bonus_model,
            bonus_suff, cars, a_i, ingame_menu, menu_args, drivers_img,
            cars_imgs, share_urls, share_imgs, respawn_name, pitstop_name,
            wall_name, goal_name, bonus_name, roads_names, grid,
            player_car_name):
        # make initializer decorator
        self.keys = keys
        self.joystick = joystick
        self.sounds = sounds
        self.color_main = color_main
        self.color = color
        self.font = font
        self.coll_path = coll_path
        self.coll_name = coll_name
        self.car_path = car_path
        self.phys_file = phys_file
        self.wheel_names = wheel_names
        self.tuning_engine = tuning_engine
        self.tuning_tires = tuning_tires
        self.tuning_suspensions = tuning_suspensions
        self.road_name = road_name
        self.model_name = model_name
        self.damage_paths = damage_paths
        self.wheel_gfx_names = wheel_gfx_names
        self.particle_path = particle_path
        self.drivers = drivers
        self.shaders = shaders
        self.music_path = music_path
        self.coll_track_path = coll_track_path
        self.unmerged = unmerged
        self.merged = merged
        self.ghosts = ghosts
        self.corner_names = corner_names
        self.waypoint_names = waypoint_names
        self.show_waypoints = show_waypoints
        self.weapon_names = weapon_names
        self.start = start
        self.track_name = track_name
        self.track_path = track_path
        self.track_model_name = track_model_name
        self.empty_name = empty_name
        self.anim_name = anim_name
        self.omni_tag = omni_tag
        self.sign_cb = sign_cb
        self.sign_name = sign_name
        self.minimap_path = minimap_path
        self.minimap_image = minimap_image
        self.col_dct = col_dct
        self.camera_vec = camera_vec
        self.shadow_src = shadow_src
        self.laps = laps
        self.rocket_path = rocket_path
        self.turbo_path = turbo_path
        self.bonus_model = bonus_model
        self.bonus_suff = bonus_suff
        self.cars = cars
        self.a_i = a_i
        self.ingame_menu = ingame_menu
        self.menu_args = menu_args
        self.drivers_img = drivers_img
        self.cars_imgs = cars_imgs
        self.share_urls = share_urls
        self.share_imgs = share_imgs
        self.respawn_name = respawn_name
        self.pitstop_name = pitstop_name
        self.wall_name = wall_name
        self.goal_name = goal_name
        self.bonus_name = bonus_name
        self.roads_names = roads_names
        self.grid = grid
        self.player_car_name = player_car_name
