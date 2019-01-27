import pyproj
from affine import Affine

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
