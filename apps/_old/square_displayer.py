import cv2
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
    def show_cropped_squares(image, squares, margin=10, min_area_threshold=100):
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
        plt.show()
