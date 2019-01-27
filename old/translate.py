import pyproj
from affine import Affine
import numpy as np

web = pyproj.Proj(init='epsg:3857')  # Projection of my image : web mercator
wgs = pyproj.Proj(init='epsg:4326')  # Projection of the input coords

top_left_wgs = (0, 54.8)  # Coords in WGS84 : Always (x, y)
top_left_web = pyproj.transform(wgs, web, top_left_wgs[0], top_left_wgs[1])

bottom_right_wgs = (10, 49.5)  # Coords in WGS84
bottom_right_web = pyproj.transform(wgs, web, bottom_right_wgs[0], bottom_right_wgs[1])

# Img size in pixels
img_width = 1058
img_height = 915

# Pixel size in the web mercator projection
pixel_width = abs((top_left_web[0] - bottom_right_web[0]) / img_width)
pixel_height = abs((top_left_web[1] - bottom_right_web[1]) / img_height)

# Gdal Transform matrix
geotransform = (
    top_left_web[0],  # top left corner x
    pixel_width,      # pixel width,
    0.0,              # rotation about y-axis
    top_left_web[1],  # top left corner y
    0.0,              # rotation about x-axis
    -pixel_height,    # pixel height.
)

pix2coord = Affine.from_gdal(*geotransform)
coord2pix = ~pix2coord


def wgs2pix(x, y):
    """
    Gets WGS84 coordinates and transforms them
    to x,y pixel indices in the target image
    """
    # Reoject WGS84 coords to web mercator
    web_xy = pyproj.transform(wgs, web, x, y)
    # Tranform web mercator into pixel indexes
    pix_x, pix_y = coord2pix * web_xy
    # Round the pixel indexes
    return int(pix_x), int(pix_y)


DISTANCE = 2 * 1000  # 2km


def corners(x, y):
    geod = pyproj.Geod(ellps='WGS84')
    for azimuth in range(0, 360, 90):
        new_x, new_y, reverse_azimuth = geod.fwd(x, y, azimuth, DISTANCE)
        yield new_x, new_y


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
