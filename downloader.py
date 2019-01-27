import requests
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
from io import BytesIO
import scaling


PREDICTION_HORIZON = 34  # we can download 34 images in the future (thus 34*5 min)


def bytes_to_gray(bytes):
    fp = BytesIO(bytes)
    array = np.array(Image.open(fp).convert("RGBA"))
    return scaling.make_grayscale(array)


def downlaod_picture(instant):
    """Instant to png bytes"""
    timestr = instant.strftime("%Y%m%d%H%M")
    r = requests.get("http://api.buienradar.nl/image/1.0/webmercatorradarnl/png/?t=%s" % timestr)
    return r.content


def get_possible_instants():
    now = datetime.utcnow()
    delta = timedelta(
        minutes=(- now.minute % 5),
        seconds=-now.second,
        microseconds=-now.microsecond,
    )
    frame_time = now + delta

    return [frame_time + (i * timedelta(minutes=5)) for i in range(PREDICTION_HORIZON)]


def get_path_list():
    return [
        "data/%s.tiff" % int(instant.timestamp())
        for instant in get_possible_instants()
    ]
