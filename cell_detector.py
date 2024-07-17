import argparse
import cv2
import numpy as np
from apps.image_processor import ImageLoader
from apps.edge_detector import EdgeDetector
from apps.line_processor import LineDetector, LineMerger
from apps.intersection_finder import IntersectionFinder
from apps.square_processor import SquareIdentifier, SquareDisplayer

def main():
    parser = argparse.ArgumentParser(description='Process and display cropped squares from an image.')
    parser.add_argument('--image_path', type=str, help='Path to the input image')
    parser.add_argument('--margin', type=int, default=10, help='Margin to add around cropped squares')
    parser.add_argument('--aspect_ratio_tolerance', type=float, default=0.2, help='Tolerance for aspect ratio of squares')
    parser.add_argument('--min_area', type=int, default=500, help='Minimum area for detected squares')
    parser.add_argument('--min_area_threshold', type=int, default=100, help='Minimum area threshold for green cell detection')
    args = parser.parse_args()

    # Load and process the image
    image, gray_image = ImageLoader.load_and_convert_image(args.image_path)
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
    main()
