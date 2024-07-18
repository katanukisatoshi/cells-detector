import argparse
import os
import numpy as np
import cv2
from apps.image_processor import ImageLoader, ImageSaver, ImageDisplayer, ImageCropper
from apps.edge_detector import EdgeDetector
from apps.line_processor import LineDetector, LineMerger, LineFilter, LineHighlighter
from apps.intersection_finder import IntersectionFinder
from apps.square_processor import SquareIdentifier, SquareDisplayer

def main(image_path, output_path, edge_threshold1, edge_threshold2, hough_threshold, min_line_length, max_line_gap, merge_threshold, gap_threshold_top, gap_threshold_bottom, gap_threshold_left, gap_threshold_right, margin, aspect_ratio_tolerance, min_area, min_area_threshold):

    # Step 1: Preprocess the original image and crop potential area
    image, gray_image = ImageLoader.load_and_convert_image(image_path)

    # Display the original image
    ImageDisplayer.display_image(image, 'Original Image')

    # Display the grayscale image
    #ImageDisplayer.display_gray_image(gray_image, 'Grayscale Image')

    # Detect edges in the grayscale image
    edges = EdgeDetector.detect_edges(gray_image, threshold1=edge_threshold1, threshold2=edge_threshold2)
    #ImageDisplayer.display_gray_image(edges, 'Edge Detection')

    # Detect lines in the edge-detected image
    lines = LineDetector.detect_lines(edges, threshold=hough_threshold, min_line_length=min_line_length, max_line_gap=max_line_gap)
    if lines is not None:
        image_with_lines = np.copy(image)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image_with_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #ImageDisplayer.display_image(image_with_lines, 'Detected Lines')
    else:
        print("No lines detected")

    # Merge nearest lines
    if lines is not None:
        image_with_merged_lines, merged_horizontal_lines, merged_vertical_lines = LineMerger.merge_nearest_lines(lines, image, threshold=merge_threshold)
        ImageDisplayer.display_image(image_with_merged_lines, 'Merged Lines')

        # Filter and highlight nearest lines to center in each step
        # Top lines
        filtered_top_lines = LineFilter.remove_lines_with_large_gap_top(merged_horizontal_lines, gap_threshold=gap_threshold_top)
        image_with_filtered_top_lines = LineHighlighter.change_color_of_filtered_lines(image_with_merged_lines, filtered_top_lines, is_horizontal=True)
        image_with_filtered_top_lines = LineHighlighter.highlight_nearest_center_line_after_filtering(image_with_filtered_top_lines, filtered_top_lines, is_horizontal=True)
        #ImageDisplayer.display_image(image_with_filtered_top_lines, 'Filtered Top Lines Colored and Nearest Highlighted')

        # Bottom lines
        filtered_bottom_lines = LineFilter.remove_lines_with_large_gap_bottom(merged_horizontal_lines, gap_threshold=gap_threshold_bottom)
        image_with_filtered_bottom_lines = LineHighlighter.change_color_of_filtered_lines(image_with_filtered_top_lines, filtered_bottom_lines, is_horizontal=True)
        image_with_filtered_bottom_lines = LineHighlighter.highlight_nearest_center_line_after_filtering(image_with_filtered_bottom_lines, filtered_bottom_lines, is_horizontal=True)
        #ImageDisplayer.display_image(image_with_filtered_bottom_lines, 'Filtered Bottom Lines Colored and Nearest Highlighted')

        # Right lines
        filtered_right_lines = LineFilter.remove_lines_with_large_gap_right(merged_vertical_lines, gap_threshold=gap_threshold_right)
        image_with_filtered_right_lines = LineHighlighter.change_color_of_filtered_lines(image_with_filtered_bottom_lines, filtered_right_lines, is_horizontal=False)
        image_with_filtered_right_lines = LineHighlighter.highlight_nearest_center_line_after_filtering(image_with_filtered_right_lines, filtered_right_lines, is_horizontal=False)
        #ImageDisplayer.display_image(image_with_filtered_right_lines, 'Filtered Right Lines Colored and Nearest Highlighted')

        # Left lines
        filtered_left_lines = LineFilter.remove_lines_with_large_gap_left(merged_vertical_lines, gap_threshold=gap_threshold_left)
        image_with_filtered_left_lines = LineHighlighter.change_color_of_filtered_lines(image_with_filtered_right_lines, filtered_left_lines, is_horizontal=False)
        image_with_filtered_left_lines = LineHighlighter.highlight_nearest_center_line_after_filtering(image_with_filtered_left_lines, filtered_left_lines, is_horizontal=False)
        #ImageDisplayer.display_image(image_with_filtered_left_lines, 'Filtered Left Lines Colored and Nearest Highlighted')
        
        ImageDisplayer.display_image(image_with_filtered_left_lines, 'Filtered All Lines Colored and Nearest Highlighted')

        # Find the nearest lines to the center from each side
        nearest_top_line = min(filtered_top_lines, key=lambda y: abs(y - image.shape[0] // 2))
        nearest_bottom_line = min(filtered_bottom_lines, key=lambda y: abs(y - image.shape[0] // 2))
        nearest_left_line = min(filtered_left_lines, key=lambda x: abs(x - image.shape[1] // 2))
        nearest_right_line = min(filtered_right_lines, key=lambda x: abs(x - image.shape[1] // 2))

        # Cover the area created by those nearest highlighted lines
        image_with_covered_area = ImageCropper.cover_area_by_nearest_lines(image_with_filtered_left_lines, nearest_top_line, nearest_bottom_line, nearest_left_line, nearest_right_line, color=(255, 0, 0), thickness=-1)
        ImageDisplayer.display_image(image_with_covered_area, 'Covered Area by Nearest Highlighted Lines')

        # Crop the area created by those nearest highlighted lines with an added margin of 20 pixels
        cropped_image_with_margin = ImageCropper.crop_area_with_margin(image, nearest_top_line, nearest_bottom_line, nearest_left_line, nearest_right_line, margin=20)
        ImageDisplayer.display_image(cropped_image_with_margin, 'Cropped Area with 20 Pixel Margin')

        # Extract the base name and extension of the file
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        # Create the new file name with '_cropped' added
        output_filename = f"{base_name}_cropped{ext}"
        ImageSaver.save_image(cropped_image_with_margin, output_path, output_filename)

    else:
        print("No lines to merge")

    # Step 2: Load and process the cropped image
    image, gray_image = ImageLoader.load_and_convert_image(output_path + output_filename)
    edges = EdgeDetector.detect_edges(gray_image)
    lines = LineDetector.detect_lines(edges)

    # Merge nearest lines with a threshold of 15 and draw them on the image
    if lines is not None:
        image_with_merged_lines, merged_horizontal_lines, merged_vertical_lines = LineMerger.merge_nearest_lines(lines, image, threshold=15)

        # Find intersections of the horizontal and vertical lines
        intersections = IntersectionFinder.find_intersections(merged_horizontal_lines, merged_vertical_lines)

        # Identify and label squares based on intersections
        image_with_squares, squares = SquareIdentifier.identify_and_label_squares(image_with_merged_lines, intersections, merged_horizontal_lines, merged_vertical_lines, aspect_ratio_tolerance=args.aspect_ratio_tolerance, min_area=args.min_area)

        # Show the cropped squares with margin and detected green cells
        SquareDisplayer.show_cropped_squares(image, squares, margin=args.margin, min_area_threshold=args.min_area_threshold)
    else:
        print("No lines were detected.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process and detect lines in an image.')
    parser.add_argument('--image_path', type=str, required=True, help='Path to the image file')
    parser.add_argument('--output_path', type=str, default='./data/cropped/', help='Path to the output directory')
    parser.add_argument('--edge_threshold1', type=int, default=50, help='First threshold for the Canny edge detector')
    parser.add_argument('--edge_threshold2', type=int, default=150, help='Second threshold for the Canny edge detector')
    parser.add_argument('--hough_threshold', type=int, default=100, help='Threshold for the Hough line transform')
    parser.add_argument('--min_line_length', type=int, default=100, help='Minimum line length for the Hough line transform')
    parser.add_argument('--max_line_gap', type=int, default=10, help='Maximum line gap for the Hough line transform')
    parser.add_argument('--merge_threshold', type=int, default=20, help='Threshold for merging nearby lines')
    parser.add_argument('--gap_threshold_top', type=int, default=40, help='Gap threshold for top lines')
    parser.add_argument('--gap_threshold_bottom', type=int, default=30, help='Gap threshold for bottom lines')
    parser.add_argument('--gap_threshold_left', type=int, default=30, help='Gap threshold for left lines')
    parser.add_argument('--gap_threshold_right', type=int, default=30, help='Gap threshold for right lines')
    parser.add_argument('--margin', type=int, default=10, help='Margin to add around cropped squares')
    parser.add_argument('--aspect_ratio_tolerance', type=float, default=0.2, help='Tolerance for aspect ratio of squares')
    parser.add_argument('--min_area', type=int, default=500, help='Minimum area for detected squares')
    parser.add_argument('--min_area_threshold', type=int, default=100, help='Minimum area threshold for green cell detection')
    args = parser.parse_args()

    main(args.image_path, args.output_path, args.edge_threshold1, args.edge_threshold2, args.hough_threshold, args.min_line_length, args.max_line_gap, args.merge_threshold, args.gap_threshold_top, args.gap_threshold_bottom, args.gap_threshold_left, args.gap_threshold_right, args.margin, args.aspect_ratio_tolerance, args.min_area, args.min_area_threshold)