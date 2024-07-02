import cv2
import numpy as np
import argparse
import os

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

def process_image_and_detect_cells(image_path, num_squares='all', min_area_threshold=100):
    image, gray_image = load_and_convert_image(image_path)
    edges = detect_edges(gray_image)
    lines = detect_lines(edges)
    _, merged_horizontal_lines, merged_vertical_lines = merge_nearest_lines(lines, image)
    cropped_squares = index_and_crop_squares(image, merged_horizontal_lines, merged_vertical_lines)
    
    if num_squares == 'all':
        num_squares = len(cropped_squares)
    else:
        num_squares = int(num_squares)
    
    saved_squares = []
    cells_count = []
    save_dir = './data/preprocessing'
    os.makedirs(save_dir, exist_ok=True)
    
    for i in range(min(num_squares, len(cropped_squares))):
        square_index, square_image = cropped_squares[i]
        square_path = os.path.join(save_dir, f'square_{square_index}.jpg')
        cv2.imwrite(square_path, square_image)
        saved_squares.append(square_path)
        
        count, output_image = detect_green_cells(square_image, min_area_threshold)
        cells_count.append((square_index, count))
        output_path = os.path.join(save_dir, f'square_{square_index}_detected.jpg')
        cv2.imwrite(output_path, output_image)
    
    return saved_squares, cells_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an image to detect and count green cells.")
    parser.add_argument("image_path", type=str, help="Path to the input image")
    parser.add_argument("--num_squares", type=str, default='all', help="Number of squares to process (default: all)")
    parser.add_argument("--min_area_threshold", type=int, default=100, help="Minimum area threshold for detecting cells")

    args = parser.parse_args()

    saved_square_paths, cells_count = process_image_and_detect_cells(
        args.image_path,
        num_squares=args.num_squares,
        min_area_threshold=args.min_area_threshold
    )

    for path in saved_square_paths:
        print(f"Saved square image: {path}")
    
    for square_index, count in cells_count:
        print(f"Square {square_index}: {count} cells detected")
    
    # Clean up
    for path in saved_square_paths:
        os.remove(path)
        detected_path = path.replace('.jpg', '_detected.jpg')
        if os.path.exists(detected_path):
            os.remove(detected_path)
