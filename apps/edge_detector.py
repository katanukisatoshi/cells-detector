import cv2

class EdgeDetector:
    @staticmethod
    def detect_edges(gray_image, threshold1=50, threshold2=150):
        edges = cv2.Canny(gray_image, threshold1, threshold2, apertureSize=3)
        return edges
