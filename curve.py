import pyproj
import numpy as np
from geo import wgs2pix
import downloader
from PIL import Image
import os
import scaling


def pixlist(pixels, x, y, distance):
    geod = pyproj.Geod(ellps='WGS84')
    xpix, ypix = wgs2pix(x, y)

    x_corner, y_corner, _ = geod.fwd(x, y, 90, distance)
    xpix_corner, _ = wgs2pix(x_corner, y_corner)

    radius = abs(xpix_corner - xpix)

    # Pixels is a Pillow image so its pixels[y, x]
    b, a = xpix, ypix
    nx, ny = pixels.shape
    x, y = np.ogrid[-a:nx - a, -b:ny - b]
    mask = x * x + y * y <= radius * radius
    return pixels[mask]


def stats(pixels, x, y):
    xpix, ypix = wgs2pix(x, y)
    center = pixlist(pixels, x, y, 1000)
    around = pixlist(pixels, x, y, 2000)
    return {
        'center': center.mean(),
        'min': np.percentile(around, 5),
        'max': np.percentile(around, 95),
    }


def get_curve(x, y):
    ret = []
    it = zip(downloader.get_possible_instants(), downloader.get_path_list())
    for instant, path in it:
        if not os.path.exists(path):
            return ret
        pixels = np.array(Image.open(path)) / scaling.MULTIPLIER
        point = stats(pixels, x, y)
        point['instant'] = instant
        ret.append(point)
    return ret
