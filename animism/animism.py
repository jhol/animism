#!/usr/bin/env python3

import argparse
import multiprocessing
import progressbar
import os
import subprocess as sp
import sys
import tempfile

FFMPEG_BIN = '/usr/bin/ffmpeg'


def make_frame(draw_frame_func, frame_num, width, height):
    frame = draw_frame_func(frame_num, width, height)
    f, path = tempfile.mkstemp('.png')
    os.close(f)
    frame.write_to_png(path)
    return path


def run(draw_frame_func, frame_count, width=1920, height=1080):
    parser = argparse.ArgumentParser(
        description='Render an animation with cairo and ffmpeg')
    parser.add_argument('out_path', metavar='OUT_PATH', type=str, nargs='?',
        help='The output file path', default='out.mp4')
    parser.add_argument('-p', '--preview', action='store_true',
        help='Display a preview window')
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
            args.out_path] + ([
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'yuyv422',
            '-window_size', '%dx%d' % (width/2, height/2),
            '-f', 'sdl', 'Preview'
            ] if args.preview else [])

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    frames = [pool.apply_async(make_frame, (draw_frame_func, f, width, height))
            for f in range(frame_count)]

    p = sp.Popen(command, stdin=sp.PIPE,
            stdout=None if args.verbose else sp.PIPE, stderr=sp.STDOUT)
    bar = progressbar.ProgressBar(max_value = frame_count)

    try:
        for frame_num in range(frame_count):
            png_path = frames[frame_num].get()
            with open(png_path, 'rb') as f:
                p.stdin.write(f.read())
                p.stdin.flush()
            os.remove(png_path)
            bar.update(frame_num)
        p.stdin.close()
        p.wait()
    except Exception as e:
        print(e)
        pass
