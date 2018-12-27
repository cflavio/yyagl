#version 130
#extension GL_ARB_shader_image_load_store : require
layout(rgba32f) uniform imageBuffer start_pos;
layout(rgba32f) uniform imageBuffer positions;
layout(rgba32f) uniform imageBuffer start_vel;
layout(rgba32f) uniform imageBuffer velocities;
layout(rgba32f) uniform imageBuffer emission_times;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform vec3 emitter_pos;
uniform vec3 accel;
uniform float osg_FrameTime;
uniform float delta_t;
uniform float start_time;  // particle system's start time
uniform float part_duration;  // single particle's duration
uniform int emitting;
out float from_emission;

void main() {
    float emission_time = imageLoad(emission_times, gl_VertexID).x;
    vec4 pos = imageLoad(positions, gl_VertexID);
    vec4 vel = imageLoad(velocities, gl_VertexID);
    float from_start = osg_FrameTime - start_time;
    from_emission = 0;
    gl_FrontColor = vec4(1);
    if (from_start > emission_time) {
        from_emission = from_start - emission_time;
        if (from_emission <= delta_t + .01) {
            pos = vec4(emitter_pos, 1);
            vel = imageLoad(start_vel, gl_VertexID);
        }
        pos += vec4((vel * delta_t).xyz, 0);
        vel += vec4(accel, .0) * delta_t;
    } else gl_FrontColor = vec4(0);
    if (emitting == 1 && from_start >= emission_time + part_duration)
        imageStore(emission_times, gl_VertexID, vec4(from_start, 0, 0, 1));
    gl_PointSize = 10;
    gl_Position = p3d_ModelViewProjectionMatrix * pos;
    imageStore(positions, gl_VertexID, pos);
    imageStore(velocities, gl_VertexID, vel);
}
