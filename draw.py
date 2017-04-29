#!/usr/bin/env python3

import argparse
import cairo
import math
import multiprocessing
import progressbar
import os
import subprocess as sp
import sys
import tempfile

FFMPEG_BIN = '/usr/bin/ffmpeg'

WIDTH, HEIGHT = 1920, 1080
FRAME_COUNT = 200

def arrow_head(ctx):
    ctx.move_to(0, 0)
    ctx.line_to(-2, -.5)
    ctx.rel_curve_to(.125, .25, .125, .75, 0, 1)
    ctx.line_to(0, 0)

def arrow(ctx, s, e, arrow_size=20):
    d = (e[0] - s[0], e[1] - s[1])
    l = math.sqrt(d[0] ** 2 + d[1] ** 2)
    u = (d[0] / l, d[1] / l)
    r = (arrow_size * u[0], arrow_size * u[1])

    ctx.save()

    ctx.move_to(*s)
    line_length = l - arrow_size
    ctx.line_to(s[0] + u[0] * line_length, s[1] + u[1] * line_length)
    ctx.stroke_preserve()

    ctx.set_matrix(cairo.Matrix(r[0], r[1], -r[1], r[0], *e))
    arrow_head(ctx)
    ctx.fill()

    ctx.restore()

def draw_frame(t):
    surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context (surface)

    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill ()

    o = (HEIGHT/2, HEIGHT/2)
    d = 360
    axis_length = d * 1.2
    x_history = int(o[0] + axis_length * 1.1)
    blob_radius = 10

    f = 0.004

    phi = t * f * math.pi * 2
    p = (o[0] + d * math.cos(phi), o[0] - d * math.sin(phi))

    # Draw the axes
    ctx.set_source_rgb(0.75, 0.75, 0.75)
    ctx.set_line_width(5)
    arrow(ctx, (o[0] - axis_length, o[1]), (o[0] + axis_length, o[1]))
    arrow(ctx, (o[0], o[1] + axis_length), (o[0], o[1] - axis_length))

    # Draw the link-line
    ctx.move_to(*p)
    ctx.line_to(x_history, p[1])
    ctx.save()
    ctx.set_dash([10, 10])
    ctx.stroke()
    ctx.restore()

    # Draw the phasor
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(5)
    ctx.arc(*p, blob_radius, 0, math.pi * 2)
    ctx.fill()
    arrow(ctx, o, (o[0] + d * math.cos(phi), o[0] - d * math.sin(phi)))

    # Draw the wave-history
    for x in range(x_history, WIDTH + 10):
        phi = (t - x + x_history) * f * math.pi * 2
        ctx.line_to(x, o[0] - d * math.sin(phi))
    ctx.set_source_rgb(0, 0, 0)
    ctx.stroke()

    return surface


def make_frame(frame_num):
    frame = draw_frame(frame_num)
    f, path = tempfile.mkstemp('.png')
    os.close(f)
    frame.write_to_png(path)
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Render an animation with cairo and ffmpeg')
    parser.add_argument('out_path', metavar='OUT_PATH', type=str, nargs='?',
        help='The output file path', default='out.mp4')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Print verbose output to stdout')
    args = parser.parse_args()

    command = [FFMPEG_BIN,
            '-y', # (optional) overwrite output file if it exists
            '-f', 'image2pipe',
            '-r', '30',
            '-vcodec', 'png',
            '-r', '30', # frames per second
            '-i', '-', # The imput comes from a pipe
            '-vcodec', 'libx264',
            '-r', '30',
            args.out_path ]

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    frames = [pool.apply_async(make_frame, (f,)) for f in range(FRAME_COUNT)]

    p = sp.Popen(command, stdin=sp.PIPE,
            stdout=None if args.verbose else sp.PIPE, stderr=sp.STDOUT)
    bar = progressbar.ProgressBar(max_value = FRAME_COUNT)

    try:
        for frame_num in range(FRAME_COUNT):
            png_path = frames[frame_num].get()
            with open(png_path, 'rb') as f:
                p.stdin.write(f.read())
            os.remove(png_path)
            bar.update(frame_num)
        p.stdin.close()
        p.wait()
    except Exception as e:
        print(e)
        pass
