import matplotlib.pyplot as plt
import cv2

class ImageDisplayer:
    @staticmethod
    def display_image(image, title):
        plt.figure(figsize=(8, 8))
        plt.title(title)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    @staticmethod
    def display_gray_image(gray_image, title):
        plt.figure(figsize=(8, 8))
        plt.title(title)
        plt.imshow(gray_image, cmap='gray')
        plt.axis('off')
        plt.show()
