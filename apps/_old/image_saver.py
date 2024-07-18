import cv2
import os

class ImageSaver:
    @staticmethod
    def save_image(image, output_path, file_name):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        cv2.imwrite(os.path.join(output_path, file_name), image)
