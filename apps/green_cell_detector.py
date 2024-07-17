import cv2
import numpy as np

class GreenCellDetector:
    @staticmethod
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
