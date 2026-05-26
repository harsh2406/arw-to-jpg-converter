import streamlit as st
import rawpy
from PIL import Image
import io
import zipfile
import datetime

st.set_page_config(page_title="ARW to JPG Converter", page_icon="📷")

st.title("Bulk ARW to JPG Converter")
st.write("Upload your Sony RAW (.arw) files, convert them to JPG, and download them all in a single ZIP file.")

# File uploader allows multiple files
uploaded_files = st.file_uploader("Choose ARW files", type=["arw"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Convert Images"):
        # Create an in-memory buffer for the ZIP file
        zip_buffer = io.BytesIO()
        
        # We use a progress bar for better user experience
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Open the ZIP file in write mode
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Converting {uploaded_file.name}...")
                
                try:
                    # rawpy needs a bytes-like object
                    file_bytes = io.BytesIO(uploaded_file.read())
                    
                    # Process the ARW file
                    with rawpy.imread(file_bytes) as raw:
                        rgb = raw.postprocess()
                    
                    # Convert numpy array to PIL Image
                    img = Image.fromarray(rgb)
                    
                    # Save image to an in-memory buffer as JPG
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="JPEG", quality=90)
                    
                    # Create the new filename
                    new_filename = uploaded_file.name.rsplit('.', 1)[0] + ".jpg"
                    
                    # Write the JPG buffer into the ZIP file
                    zip_file.writestr(new_filename, img_buffer.getvalue())
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
                
        status_text.text("Conversion complete!")
        
        # Generate timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"converted_images_{timestamp}.zip"
        
        # Provide the ZIP file for download
        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip"
        )

# Add custom footer with signature and Instagram button
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px;">
        <p style="font-size: 18px; font-weight: bold;">Created by Harshit😎</p>
        <a href="https://www.instagram.com/harshit_._arora/" target="_blank" style="text-decoration: none;">
            <button style="background-color: #E1306C; color: white; border: none; padding: 10px 24px; text-align: center; display: inline-block; font-size: 16px; font-weight: bold; margin: 4px 2px; cursor: pointer; border-radius: 8px;">
                Follow on Instagram
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
