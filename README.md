animism
=======

`animism` is a simple framework for procedurally generating animations with
*cairo* and *ffmpeg*.

## Installation

1. Install depedencies:

   On Debian/Ubuntu:
   ```
   $ sudo apt install python3-setuptools python3-cairo python3-pip
   $ sudo pip3 install progressbar2
   ```

2. Build the python module:
   ```
   $ python3 setup.py build
   ```

3. Install the python module:
   ```
   $ sudo python3 setup.py install
   ```

### Usage

Code example:

#### `test.py`
```
#!/usr/bin/env python3

import animism
import cairo

def draw_frame(frame_num, width, height):
    surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context (surface)

    # Fill background
    ctx.rectangle(0, 0, width, height)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill ()

    # Draw content
    offset = frame_num * 2
    l = width / 8
    r = 7 * width / 8
    t = height / 8
    b = 7 * height / 8

    ctx.move_to(l + offset, t)
    ctx.line_to(r - offset, b)
    ctx.move_to(l, t + offset)
    ctx.line_to(r, b - offset)
    ctx.move_to(r - offset, t)
    ctx.line_to(l + offset, b)
    ctx.move_to(l, b - offset)
    ctx.line_to(r, t + offset)

    ctx.set_source_rgb(0.5, 0, 1)
    ctx.set_line_width(height / 64)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()

    return surface

if __name__ == '__main__':
    animism.run(draw_frame, 200)
```

#### Usage
```
$ python3 test.py
$ mplayer out.mp4
```

For more examples see `examples/` sub-directory.
