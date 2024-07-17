import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

class ImageLoader:
    @staticmethod
    def load_and_convert_image(image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image, gray_image

class ImageSaver:
    @staticmethod
    def save_image(image, output_path, file_name):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        cv2.imwrite(os.path.join(output_path, file_name), image)

class ImageDisplayer:
    @staticmethod
    def display_image(image, title):
        plt.figure(figsize=(8, 8))
        plt.title(title)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    @staticmethod
    def display_gray_image(gray_image, title):
        plt.figure(figsize=(8, 8))
        plt.title(title)
        plt.imshow(gray_image, cmap='gray')
        plt.axis('off')
        plt.show()

class ImageCropper:
    @staticmethod
    def cover_area_by_nearest_lines(image, nearest_top, nearest_bottom, nearest_left, nearest_right, color=(255, 0, 0), thickness=2):
        covered_image = np.copy(image)
        # Draw rectangle covering the area
        cv2.rectangle(covered_image, (nearest_left, nearest_top), (nearest_right, nearest_bottom), color, thickness)
        return covered_image

    @staticmethod
    def crop_area_with_margin(image, nearest_top, nearest_bottom, nearest_left, nearest_right, margin=20):
        top = max(0, nearest_top - margin)
        bottom = min(image.shape[0], nearest_bottom + margin)
        left = max(0, nearest_left - margin)
        right = min(image.shape[1], nearest_right + margin)
        
        cropped_image = image[top:bottom, left:right]
        return cropped_image
