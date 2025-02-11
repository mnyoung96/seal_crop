import streamlit as st
import os
from PIL import Image
from streamlit_cropper import st_cropper
import cv2
import numpy as np
from PIL import ImageEnhance

# Define image enhancement functions
def adjust_brightness_contrast(image, alpha, beta):
    return cv2.addWeighted(image, alpha, image, 0, beta)

def sharpen_image(image):
    kernel = np.array([[-1, -1, -1],
                       [-1, 9, -1],
                       [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

def adjust_brightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def adjust_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

# Step 1: Image Selection
st.title("Seal ID Photo Selector & Cropper")

if "selected_images" not in st.session_state:
    st.session_state.selected_images = []
if "cropping_stage" not in st.session_state:
    st.session_state.cropping_stage = False  # Controls if we move to the crop stage
if "cropped_images" not in st.session_state:
    st.session_state.cropped_images = {}

# Upload Multiple Images
uploaded_files = st.file_uploader("Upload multiple photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files and not st.session_state.cropping_stage:
    st.subheader("Select the Best 1-5 Photos")
    
    selected_images = []
    cols = st.columns(3)  # Arrange images in a grid

    for i, uploaded_file in enumerate(uploaded_files):
        image = Image.open(uploaded_file)
        with cols[i % 3]:  # Distribute images in columns
            st.image(image, caption=uploaded_file.name, use_container_width=True)  # Larger Image Display
            if st.checkbox(f"Select {uploaded_file.name}", key=uploaded_file.name):
                selected_images.append(uploaded_file)

    # Confirm Selection
    if st.button("OK - Proceed to Cropping"):
        if len(selected_images) == 0 or len(selected_images) > 5:
            st.warning("Please select 1-5 images.")
        else:
            st.session_state.selected_images = selected_images
            st.session_state.cropping_stage = True

# Step 2: Cropping Interface
if st.session_state.cropping_stage:
    st.subheader("Crop Selected Images")
    cropped_images = {}

    for uploaded_file in st.session_state.selected_images:
        image = Image.open(uploaded_file)

        st.write(f"**Crop {uploaded_file.name}**")
        cropped_image = st_cropper(image, aspect_ratio=None)  # Fixed incorrect function call

        # Convert PIL image to OpenCV format
        cropped_image_cv = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2BGR)

        # Image Editing Options
        st.write("### Enhance Image")
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0, key=f"brightness_{uploaded_file.name}")
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0, key=f"contrast_{uploaded_file.name}")
        sharpen = st.checkbox("Sharpen", key=f"sharpen_{uploaded_file.name}")

        # Apply Enhancements
        enhanced_image_cv = adjust_brightness_contrast(cropped_image_cv, contrast, brightness)
        if sharpen:
            enhanced_image_cv = sharpen_image(enhanced_image_cv)

        # Convert back to PIL format
        enhanced_image = Image.fromarray(cv2.cvtColor(enhanced_image_cv, cv2.COLOR_BGR2RGB))

        cropped_images[uploaded_file.name] = enhanced_image

        st.image(enhanced_image, caption=f"Enhanced {uploaded_file.name}")

    st.session_state.cropped_images = cropped_images

    # Step 3: Save & Download
    if st.button("OK - Save Cropped Images"):
        output_folder = "cropped_images"
        os.makedirs(output_folder, exist_ok=True)

        for filename, cropped_img in st.session_state.cropped_images.items():
            save_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_cropped.jpg")
            cropped_img.save(save_path)

            st.success(f"Saved: `{save_path}`")

    # Provide individual download buttons for each cropped image
    for filename, cropped_img in st.session_state.cropped_images.items():
        save_path = os.path.join("cropped_images", f"{os.path.splitext(filename)[0]}_cropped.jpg")
        if os.path.exists(save_path):
            with open(save_path, "rb") as file:
                st.download_button(label=f"Download {filename}_cropped", data=file, file_name=os.path.basename(save_path))

    # Button to return to the beginning
    if st.button("Start Over"):
        st.session_state.selected_images = []
        st.session_state.cropping_stage = False
        st.session_state.cropped_images = {}
