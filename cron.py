import downloader
from PIL import Image


if __name__ == '__main__':
    for i, instant in enumerate(downloader.get_possible_instants()):
        original_bytes = downloader.downlaod_picture(instant)
        gray_array = downloader.bytes_to_gray(original_bytes)

        timestamp = int(instant.timestamp())
        Image.fromarray(gray_array).save("data/%s.tiff" % timestamp)
