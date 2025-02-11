import streamlit as st
import os
from PIL import Image
from streamlit_cropper import st_cropper
import zipfile

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

        cropped_images[uploaded_file.name] = cropped_image

    st.session_state.cropped_images = cropped_images

    # Step 3: Save & Download
    if st.button("OK - Save Cropped Images"):
        output_folder = "cropped_images"
        os.makedirs(output_folder, exist_ok=True)

        for filename, cropped_img in st.session_state.cropped_images.items():
            save_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_cropped.jpg")
            cropped_img.save(save_path)

            st.success(f"Saved: `{save_path}`")

        # Provide a button to download all images as a zip file
        zip_path = os.path.join(output_folder, "cropped_images.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in os.listdir(output_folder):
                if filename.endswith("_cropped.jpg"):
                    zipf.write(os.path.join(output_folder, filename), filename)
        
        with open(zip_path, "rb") as file:
            st.download_button(label="Download All Cropped Images", data=file, file_name="cropped_images.zip")
