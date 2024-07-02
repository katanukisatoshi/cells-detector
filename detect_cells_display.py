import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import apps.edata_tools as tools

def load_and_convert_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray_image

def detect_edges(gray_image, threshold1=50, threshold2=150):
    edges = cv2.Canny(gray_image, threshold1, threshold2, apertureSize=3)
    return edges

def detect_lines(edges, threshold=100, min_line_length=100, max_line_gap=10):
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
    return lines

def merge_nearest_lines(lines, image, threshold=50):
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

def index_and_crop_squares(image, horizontal_lines, vertical_lines):
    index = 1
    horizontal_lines_excluding_top = horizontal_lines[1:]
    cropped_squares = []

    for i in range(len(horizontal_lines_excluding_top) - 1):
        for j in range(len(vertical_lines) - 1):
            top_left = (vertical_lines[j], horizontal_lines_excluding_top[i])
            bottom_right = (vertical_lines[j + 1], horizontal_lines_excluding_top[i + 1])
            # Crop the square
            cropped_square = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            cropped_squares.append((index, cropped_square))
            index += 1
    return cropped_squares

def detect_green_cells(image, min_area_threshold=100):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([30, 30, 30])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
    kernel = np.ones((3, 3), np.uint8)
    mask_green_morphed = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
    mask_green_morphed = cv2.morphologyEx(mask_green_morphed, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask_green_morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area_threshold]
    output_image = image.copy()
    for cnt in filtered_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.drawContours(output_image, [cnt], -1, (0, 255, 0), 2)
        cv2.rectangle(output_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        area = cv2.contourArea(cnt)
        cv2.putText(output_image, f'Area: {area}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    return len(filtered_contours), output_image

def index_squares(image, horizontal_lines, vertical_lines):
    index = 1
    horizontal_lines_excluding_top = horizontal_lines[1:]

    for i in range(len(horizontal_lines_excluding_top) - 1):
        for j in range(len(vertical_lines) - 1):
            top_left = (vertical_lines[j], horizontal_lines_excluding_top[i])
            bottom_right = (vertical_lines[j + 1], horizontal_lines_excluding_top[i + 1])
            # Draw the index on the image
            cv2.putText(image, str(index), 
                        (top_left[0] + 5, top_left[1] + 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            index += 1
    return image

def process_and_display_images(image_path, num_squares='all', min_area_threshold=100):
    image, gray_image = load_and_convert_image(image_path)

    # Figure 01: Original, Edges, Detected Lines & Merged Line
    plt.figure(figsize=(15, 10))
    plt.subplot(2, 2, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title('Original Image')

    edges = detect_edges(gray_image)
    plt.subplot(2, 2, 2)
    plt.imshow(edges, cmap='gray')
    plt.title('Edges')

    lines = detect_lines(edges)
    image_with_lines = image.copy()
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image_with_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)
    plt.subplot(2, 2, 3)
    plt.imshow(cv2.cvtColor(image_with_lines, cv2.COLOR_BGR2RGB))
    plt.title('Detected Lines')

    merged_image, merged_horizontal_lines, merged_vertical_lines = merge_nearest_lines(lines, image)
    plt.subplot(2, 2, 4)
    plt.imshow(cv2.cvtColor(merged_image, cv2.COLOR_BGR2RGB))
    plt.title('Merged Lines')
    plt.tight_layout()
    plt.show()

    # Figure 02: Indexed Squares
    plt.figure(figsize=(10, 10))
    indexed_image = index_squares(merged_image.copy(), merged_horizontal_lines, merged_vertical_lines)
    plt.imshow(cv2.cvtColor(indexed_image, cv2.COLOR_BGR2RGB))
    plt.title('Indexed Squares')
    plt.tight_layout()
    plt.show()

    cropped_squares = index_and_crop_squares(image, merged_horizontal_lines, merged_vertical_lines)
    if num_squares == 'all':
        num_squares = len(cropped_squares)
        print(num_squares)
    else:
        num_squares = int(num_squares)

    # Figure 03: All Sample Cropped Squares
    plt.figure(figsize=(15, 15))
    for i in range(min(num_squares, len(cropped_squares))):
        square_index, square_image = cropped_squares[i]
        plt.subplot(5, 6, i + 1)  # Adjust the grid size accordingly
        plt.imshow(cv2.cvtColor(square_image, cv2.COLOR_BGR2RGB))
        plt.title(f'Square {square_index}')
    plt.tight_layout()
    plt.show()

    # Figure 04: All Detected Green Cells
    cells_count = []
    plt.figure(figsize=(15, 15))
    for i in range(min(num_squares, len(cropped_squares))):
        square_index, square_image = cropped_squares[i]
        count, output_image = detect_green_cells(square_image, min_area_threshold)
        cells_count.append((square_index, count))
        plt.subplot(5, 6, i + 1)  # Adjust the grid size accordingly
        plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
        plt.title(f'Square {square_index} - Cells: {count}')
    plt.tight_layout()
    plt.show()

    return cropped_squares, cells_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process an image to detect green cells in grid squares.')
    parser.add_argument('--image_path', type=str, help='Path to the input image')
    parser.add_argument('--num_squares', default='all', help='Number of squares to process (default: all)')
    parser.add_argument('--min_area_threshold', type=int, default=100, help='Minimum area threshold for detecting green cells (default: 100)')

    args = parser.parse_args()

    # Run the function with arguments from argparse
    cropped_squares, cells_count = process_and_display_images(args.image_path, num_squares=args.num_squares, min_area_threshold=args.min_area_threshold)

    # Convert the list to a DataFrame
    cells_count_df = pd.DataFrame(cells_count, columns=['Square Index', 'Cell Count'])
    tools.display_dataframe_to_user(name="Cropped Squares and Cells Count", dataframe=cells_count_df)