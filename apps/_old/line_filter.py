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
