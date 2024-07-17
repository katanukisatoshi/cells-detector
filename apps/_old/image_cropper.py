import cv2
import numpy as np

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
