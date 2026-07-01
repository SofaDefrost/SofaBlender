import bpy
import os

def setup_video_render(output_dir, file_name="animation.mp4", fps=24, width=1920, height=1080):
    scene = bpy.context.scene

    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100

    scene.render.fps = fps

    scene.render.image_settings.file_format = 'FFMPEG'

    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.video_bitrate = 6000

    scene.render.filepath = os.path.join(output_dir, file_name)


def render_animation():
    bpy.ops.render.render(animation=True)