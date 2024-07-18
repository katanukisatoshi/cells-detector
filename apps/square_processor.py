import cv2
import numpy as np
import matplotlib.pyplot as plt
from apps.green_cell_detector import GreenCellDetector

class SquareDisplayer:
    @staticmethod
    def add_margin(x, y, width, height, image_shape, margin=10):
        x_start = max(0, x - margin)
        y_start = max(0, y - margin)
        x_end = min(image_shape[1], x + width + margin)
        y_end = min(image_shape[0], y + height + margin)
        return x_start, y_start, x_end - x_start, y_end - y_start

    @staticmethod
    def show_cropped_squares(image, squares, margin=10, min_area_threshold=100, save_path=None):
        num_squares = len(squares)
        cols = 4  # Number of columns in the grid
        rows = num_squares // cols + (num_squares % cols > 0)  # Calculate the number of rows based on the number of images and columns
    
        plt.figure(figsize=(15, 15))
        
        for i, (pts, (x, y, width, height)) in enumerate(squares):
            x, y, width, height = SquareDisplayer.add_margin(x, y, width, height, image.shape, margin)
            cropped_image = image[y:y+height, x:x+width]
            green_cells_count, output_image = GreenCellDetector.detect_green_cells(cropped_image, min_area_threshold=min_area_threshold)
            plt.subplot(rows, cols, i + 1)
            plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.title(f'Square {i+1} (Cells: {green_cells_count})')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

class SquareIdentifier:
    @staticmethod
    def identify_and_label_squares(image, intersections, horizontal_lines, vertical_lines, aspect_ratio_tolerance=0.2, min_area=500):
        intersections = sorted(intersections, key=lambda pt: (pt[1], pt[0]))  # Sort by y, then by x
        squares = []
        index = 1

        for i in range(len(horizontal_lines) - 1):
            for j in range(len(vertical_lines) - 1):
                top_left = (vertical_lines[j], horizontal_lines[i])
                top_right = (vertical_lines[j+1], horizontal_lines[i])
                bottom_left = (vertical_lines[j], horizontal_lines[i+1])
                bottom_right = (vertical_lines[j+1], horizontal_lines[i+1])

                if top_left in intersections and top_right in intersections and bottom_left in intersections and bottom_right in intersections:
                    width = vertical_lines[j+1] - vertical_lines[j]
                    height = horizontal_lines[i+1] - horizontal_lines[i]
                    area = width * height
                    aspect_ratio = float(width) / height

                    if 1 - aspect_ratio_tolerance <= aspect_ratio <= 1 + aspect_ratio_tolerance and area >= min_area:
                        pts = np.array([top_left, top_right, bottom_right, bottom_left])
                        squares.append((pts, (vertical_lines[j], horizontal_lines[i], width, height)))
                        cv2.polylines(image, [pts], isClosed=True, color=(255, 0, 0), thickness=2)
                        center_x = (top_left[0] + bottom_right[0]) // 2
                        center_y = (top_left[1] + bottom_right[1]) // 2
                        cv2.putText(image, str(index), (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        index += 1

        return image, squares
