import cv2
import numpy as np

class LineDetector:
    @staticmethod
    def detect_lines(edges, threshold=100, min_line_length=100, max_line_gap=10):
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
        return lines

class LineMerger:
    @staticmethod
    def merge_nearest_lines(lines, image, threshold=15):
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

class LineFilter:
    @staticmethod
    def remove_lines_with_large_gap_top(horizontal_lines, gap_threshold=40):
        top_lines = horizontal_lines[:6]
        filtered_top_lines = [top_lines[0]]
        for i in range(1, len(top_lines)):
            if (top_lines[i] - top_lines[i-1]) <= gap_threshold:
                filtered_top_lines.append(top_lines[i])
        return filtered_top_lines

    @staticmethod
    def remove_lines_with_large_gap_bottom(horizontal_lines, gap_threshold=30):
        bottom_lines = horizontal_lines[-5:]
        filtered_bottom_lines = []
        for i in range(len(bottom_lines) - 1):
            if (bottom_lines[i+1] - bottom_lines[i]) <= gap_threshold:
                filtered_bottom_lines.append(bottom_lines[i])
                filtered_bottom_lines.append(bottom_lines[i+1])
        filtered_bottom_lines = list(set(filtered_bottom_lines))  # Remove duplicates
        filtered_bottom_lines.sort()  # Ensure the lines are sorted
        return filtered_bottom_lines

    @staticmethod
    def remove_lines_with_large_gap_right(vertical_lines, gap_threshold=30):
        right_lines = vertical_lines[-6:]
        filtered_right_lines = []
        for i in range(len(right_lines) - 1):
            if (right_lines[i+1] - right_lines[i]) <= gap_threshold:
                filtered_right_lines.append(right_lines[i])
                filtered_right_lines.append(right_lines[i+1])
        filtered_right_lines = list(set(filtered_right_lines))  # Remove duplicates
        filtered_right_lines.sort()  # Ensure the lines are sorted
        return filtered_right_lines

    @staticmethod
    def remove_lines_with_large_gap_left(vertical_lines, gap_threshold=30):
        left_lines = vertical_lines[:6]
        filtered_left_lines = []
        for i in range(len(left_lines) - 1):
            if (left_lines[i+1] - left_lines[i]) <= gap_threshold:
                filtered_left_lines.append(left_lines[i])
                filtered_left_lines.append(left_lines[i+1])
        filtered_left_lines = list(set(filtered_left_lines))  # Remove duplicates
        filtered_left_lines.sort()  # Ensure the lines are sorted
        return filtered_left_lines
