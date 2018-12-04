#version 130
#extension GL_ARB_shader_image_load_store : require
layout(rgba32f) uniform imageBuffer init_vel;
layout(rgba32f) uniform imageBuffer start_particle_time;
layout(rgba32f) uniform imageBuffer start_pos;
uniform float gravity;
uniform float osg_FrameTime;
uniform float delta_t;
uniform float start_time;  // particle system's start time
uniform mat4 p3d_ModelViewProjectionMatrix;
out float time;  // time relative to specific particle's beginning
out float ptime;

void main() {
    vec4 _start_particle_time = imageLoad(start_particle_time, gl_VertexID);
    vec4 vel = imageLoad(init_vel, gl_VertexID);
    time = osg_FrameTime - start_time;
    ptime = 0;
    vec4 pos = imageLoad(start_pos, gl_VertexID);
    gl_FrontColor = vec4(1);
    if (time > _start_particle_time.x) {
        float t = time - _start_particle_time.x;
        ptime = t;
        pos += vel * delta_t;
        vel += vec4(.0, .0, gravity, .0) * delta_t;
    } else gl_FrontColor = vec4(0);
    gl_PointSize = 10;
    gl_Position = p3d_ModelViewProjectionMatrix * pos;
    imageStore(start_pos, gl_VertexID, pos);
    imageStore(init_vel, gl_VertexID, vel);
}
