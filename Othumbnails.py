from PIL import Image
from PIL.PngImagePlugin import PngInfo
import glob
import os
import hashlib
from urllib.parse import urlparse
class ThumbnailMaker():
    def __init__(self,cache_dir):
        self.cache_dir=cache_dir

    def add_file_scheme(self,uri):
        """
        Adds 'file://' scheme to a URI if it's not already present.

        Args:
            uri (str): The URI string to process.

        Returns:
            str: The URI with the 'file://' scheme.
        """
        parsed_uri = urlparse(uri)
        if not parsed_uri.scheme:
            return "file://" + uri
        return uri

    def compute_md5(self,input_string):
        """
        Compute the MD5 hash of the input string.

        Args:
            input_string (str): The input string to compute the MD5 hash for.

        Returns:
            str: The MD5 hash of the input string as a hexadecimal digest.
        """

        input_bytes = input_string.encode('utf-8')
        md5_hash = hashlib.md5(input_bytes)
        hex_digest = md5_hash.hexdigest()

        return hex_digest

    def create_thumbnail(self,input_image_path, thumbnail_width=256):
        with Image.open(input_image_path) as image:
            metadata_dic = {
                "Thumb::URI": "file://" + input_image_path,
                "Thumb::MTime": os.path.getmtime(input_image_path),
                "Software": 'OpenGallery'
            }
            metadata = PngInfo()
            for key, value in metadata_dic.items():
                metadata.add_text(key, str(value))

            thumbnail_height = int(thumbnail_width * (image.height / image.width))
            thumbnail_image = image.resize((thumbnail_width, thumbnail_height))
            thumbnail_image.info.pop('icc_profile', None)
            thumbnail_name = self.compute_md5(self.add_file_scheme(input_image_path))
            thumbnail_path = self.cache_dir + thumbnail_name + '.png'
            thumbnail_image.save(thumbnail_path, pnginfo=metadata)

            # Set the modification time of the saved thumbnail to match the original image's modification time
            os.utime(thumbnail_path, (os.path.getatime(input_image_path), os.path.getmtime(input_image_path)))

    