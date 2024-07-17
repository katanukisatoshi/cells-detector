import cv2
import numpy as np

class LineHighlighter:
    @staticmethod
    def change_color_of_filtered_lines(image_with_merged_lines, filtered_lines, is_horizontal=True, color=(255, 0, 0), line_thickness=2):
        modified_image = np.copy(image_with_merged_lines)
        if is_horizontal:
            for y in filtered_lines:
                cv2.line(modified_image, (0, y), (modified_image.shape[1], y), color, line_thickness)
        else:
            for x in filtered_lines:
                cv2.line(modified_image, (x, 0), (x, modified_image.shape[0]), color, line_thickness)
        return modified_image

    @staticmethod
    def highlight_nearest_center_line_after_filtering(image, filtered_lines, is_horizontal=True, color=(0, 0, 255), line_thickness=2):
        center_y = image.shape[0] // 2
        center_x = image.shape[1] // 2

        if is_horizontal:
            # Find the nearest horizontal line to the center
            nearest_line = min(filtered_lines, key=lambda y: abs(y - center_y))
            cv2.line(image, (0, nearest_line), (image.shape[1], nearest_line), color, line_thickness)
        else:
            # Find the nearest vertical line to the center
            nearest_line = min(filtered_lines, key=lambda x: abs(x - center_x))
            cv2.line(image, (nearest_line, 0), (nearest_line, image.shape[0]), color, line_thickness)
        
        return image
