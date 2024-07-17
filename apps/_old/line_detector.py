import cv2
import numpy as np

class LineDetector:
    @staticmethod
    def detect_lines(edges, threshold=100, min_line_length=100, max_line_gap=10):
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
        return lines

    @staticmethod
    def merge_nearest_lines(lines, image, threshold=20):
        horizontal_lines = []
        vertical_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) < 10:  # Horizontal line
                horizontal_lines.append(y1)
            elif abs(x1 - x2) < 10:  # Vertical line
                vertical_lines.append(x1)

        horizontal_lines = sorted(set(horizontal_lines))
        vertical_lines = sorted(set(vertical_lines))

        def merge_lines(line_positions, threshold):
            merged_lines = []
            current_line = line_positions[0]

            for line in line_positions[1:]:
                if line - current_line <= threshold:
                    continue
                else:
                    merged_lines.append(current_line)
                    current_line = line

            merged_lines.append(current_line)
            return merged_lines

        merged_horizontal_lines = merge_lines(horizontal_lines, threshold)
        merged_vertical_lines = merge_lines(vertical_lines, threshold)

        image_with_merged_lines = np.copy(image)

        for y in merged_horizontal_lines:
            cv2.line(image_with_merged_lines, (0, y), (image.shape[1], y), (0, 255, 0), 2)

        for x in merged_vertical_lines:
            cv2.line(image_with_merged_lines, (x, 0), (x, image.shape[0]), (0, 255, 0), 2)

        return image_with_merged_lines, merged_horizontal_lines, merged_vertical_lines
