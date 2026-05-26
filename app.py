import streamlit as st
import rawpy
from PIL import Image
import io
import zipfile
import datetime
import gc  # Garbage collection to clear memory

st.set_page_config(page_title="ARW to JPG Converter", page_icon="📷")

st.title("Bulk ARW to JPG Converter")
st.write("Upload your Sony RAW (.arw) files, convert them to JPG, and download them all in a single ZIP file.")

# File uploader allows multiple files
uploaded_files = st.file_uploader("Choose ARW files", type=["arw"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Convert Images"):
        # Create an in-memory buffer for the ZIP file
        zip_buffer = io.BytesIO()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Open the ZIP file in write mode
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Converting {uploaded_file.name} ({i+1}/{len(uploaded_files)})...")
                
                try:
                    # Read bytes
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
                    
                    # --- INTENSE MEMORY CLEANUP ---
                    del file_bytes
                    del rgb
                    del img
                    del img_buffer
                    gc.collect()  # Force Python to clear RAM instantly
                    
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

# Add custom footer with signature and clickable Instagram logo
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px;">
        <p style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Created by Harshit😎</p>
        <a href="https://www.instagram.com/harshit_._arora/" target="_blank" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="45" alt="Instagram" style="border-radius: 10px; transition: 0.3s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
