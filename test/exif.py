import unittest
import os

import jason_gnss.exif as exif

class Test(unittest.TestCase):

    def test_get_images_in_path(self):
        images_names = exif.get_images_in_path('test\\data\\exif')

        assert images_names[0] == 'DJI_0001_small.JPG'
        assert images_names[1] == 'DJI_0002_small.JPG'
    
    def test_no_jpg_images_in_path(self):
        images_names = exif.get_images_in_path('test\\data')

        assert images_names == -1

    def test_get_image_exif(self):
        image_file = 'test\\data\\exif\\DJI_0001_small.JPG'
        exif_tags = exif.get_image_exif(image_file)

        assert exif_tags['Image XResolution'] == '1'
        assert exif_tags['EXIF DateTimeOriginal'] == '2020:03:10 12:44:13'

    def test_get_exif_tags_file(self):
        images_folder = 'test\\data\\exif'
        output_filename = 'images_metadata.json'
        exif_filepath = exif.get_exif_tags_file(images_folder, output_filename)

        assert exif_filepath == 'test\\data\\exif\\images_metadata.json'

    def test_get_exif_tags_no_images_in_path(self):
        images_folder = 'test\\data'
        output_filename = 'images_metadata.json'
        exif_filepath = exif.get_exif_tags_file(images_folder, output_filename)

        assert exif_filepath == -1
