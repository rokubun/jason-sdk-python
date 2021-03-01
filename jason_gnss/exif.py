import argparse
import sys
import os
import exifread
import json

def get_images_in_path (images_path):
    images_names = []
    for image_name in os.listdir(images_path):
        if image_name.endswith(".JPG"):
            images_names.append(image_name)

    if images_names == []:
        images_names = -1
    
    return images_names

def get_image_exif(image_path):
    exif_tags = {}
    image = open(image_path, 'rb')

    tags = exifread.process_file(image, details = False)
    for tag in tags.keys():
        exif_tags[tag] = str(tags[tag])

    image.close()
    return exif_tags

def create_output_file(exif_tags_array, images_folder, output_filename=None):
    if output_filename is None:
        output_filename = "camera_metadata_file.json"
        
    exif_tags_filepath = os.path.join(images_folder, output_filename)

    with open (exif_tags_filepath, 'w') as json_file:
        json.dump(exif_tags_array, json_file)
        json_file.close()

    return exif_tags_filepath

def get_exif_tags_file(images_folder, output_filename=None):
    images_names = get_images_in_path(images_folder)

    if images_names == -1:
        exif_tags_filepath = -1
    
    else:
        exif_tags_array = {}
        for image_name in images_names:
            image_path = os.path.join(images_folder, image_name)
            exif_tags = get_image_exif(image_path)
            exif_tags_array[image_name] = exif_tags

        exif_tags_filepath = create_output_file(exif_tags_array, images_folder, output_filename)

    return exif_tags_filepath

if __name__ == "__main__":
    argParser = argparse.ArgumentParser(description= __doc__,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument('--images_folder_path', '-i', help='Introduce the path to the images folder to create a .json containing the metadata of all images.')
    argParser.add_argument('--output_filename', '-o', help='Introduce the filename of the .json with the metadata to be stored in the path.')
    args = argParser.parse_args()

    images_folder = args.images_folder_path
    output_filename = args.output_filename
    get_exif_tags_file(images_folder, output_filename)