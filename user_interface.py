import streamlit as st
import os
import subprocess
from PIL import Image

# Ensure the directories exist
input_dir = './data/input/'
cropped_dir = './data/cropped/'
output_dir = './data/output/'
os.makedirs(input_dir, exist_ok=True)
os.makedirs(cropped_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Streamlit app title
st.title('Green Cells Processing App')

# File uploader
uploaded_file = st.file_uploader('Upload an image', type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    # Parameters input
    st.sidebar.title('Parameters')
    edge_threshold1 = st.sidebar.slider('Edge Threshold 1', 0, 255, 50)
    edge_threshold2 = st.sidebar.slider('Edge Threshold 2', 0, 255, 110)
    hough_threshold = st.sidebar.slider('Hough Threshold', 0, 255, 100)
    min_line_length = st.sidebar.slider('Min Line Length', 0, 500, 100)
    max_line_gap = st.sidebar.slider('Max Line Gap', 0, 100, 10)
    merge_threshold = st.sidebar.slider('Merge Threshold', 0, 100, 20)
    gap_threshold_top = st.sidebar.slider('Gap Threshold Top', 0, 100, 40)
    gap_threshold_bottom = st.sidebar.slider('Gap Threshold Bottom', 0, 100, 30)
    gap_threshold_left = st.sidebar.slider('Gap Threshold Left', 0, 100, 30)
    gap_threshold_right = st.sidebar.slider('Gap Threshold Right', 0, 100, 30)
    margin = st.sidebar.slider('Margin', 0, 100, 10)
    aspect_ratio_tolerance = st.sidebar.slider('Aspect Ratio Tolerance', 0.0, 1.0, 0.2)
    min_area = st.sidebar.slider('Min Area', 0, 10000, 500)
    min_area_threshold = st.sidebar.slider('Min Area Threshold', 0, 1000, 100)

    # Process button
    if st.button('Process Image'):
        # Save uploaded image to a temporary file
        input_image_path = os.path.join(input_dir, uploaded_file.name)
        cropped_image_path = cropped_dir
        output_image_path = os.path.join(output_dir, 'output_' + uploaded_file.name)

        with open(input_image_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Call the main.py script with the parameters
        command = [
            'python3', 'main.py', 
            '--input_path', input_image_path,
            '--cropped_path', cropped_image_path, 
            '--output_path', output_image_path,
            '--edge_threshold1', str(edge_threshold1),
            '--edge_threshold2', str(edge_threshold2),
            '--hough_threshold', str(hough_threshold),
            '--min_line_length', str(min_line_length),
            '--max_line_gap', str(max_line_gap),
            '--merge_threshold', str(merge_threshold),
            '--gap_threshold_top', str(gap_threshold_top),
            '--gap_threshold_bottom', str(gap_threshold_bottom),
            '--gap_threshold_left', str(gap_threshold_left),
            '--gap_threshold_right', str(gap_threshold_right),
            '--margin', str(margin),
            '--aspect_ratio_tolerance', str(aspect_ratio_tolerance),
            '--min_area', str(min_area),
            '--min_area_threshold', str(min_area_threshold)
        ]
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            st.text(result.stdout)
            st.text(result.stderr)
            
            # Display the output image
            processed_image_path = os.path.join(cropped_image_path, 'cropped_' + uploaded_file.name)
            #if os.path.exists(processed_image_path) and os.path.exists(output_image_path):
                #cropped_image = Image.open(processed_image_path)
                #st.image(cropped_image, caption='Processed Image', use_column_width=True)
            if os.path.exists(output_image_path):
                output_image =  Image.open(output_image_path)
                st.image(output_image, caption='Detected Green Cells', use_column_width=True)
            else:
                st.error('Processing failed. Output image not found.')
        except subprocess.CalledProcessError as e:
            st.error(f'Error during processing: {e.stderr}')
        except Exception as e:
            st.error(f'An unexpected error occurred: {e}')
