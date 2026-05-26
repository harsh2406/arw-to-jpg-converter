import streamlit as st
import rawpy
from PIL import Image
import io
import zipfile
import datetime
import gc
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Fast ARW to JPG Converter", page_icon="📷")

st.title("Bulk ARW to JPG Converter (Turbo Mode)")
st.write("Convert your Sony RAW (.arw) files to JPG in parallel using multi-threading.")

# File uploader
uploaded_files = st.file_uploader("Choose ARW files", type=["arw"], accept_multiple_files=True)

# This function handles a single file conversion
def convert_single_file(uploaded_file):
    try:
        # Read file bytes into memory
        file_bytes = io.BytesIO(uploaded_file.read())
        
        # Process the ARW file using rawpy
        with rawpy.imread(file_bytes) as raw:
            # half_size=True speeds up decoding by 4x if you just need quick previews/sharing.
            # Remove half_size=True if you absolutely need maximum print resolution.
            rgb = raw.postprocess(half_size=True) 
        
        # Convert numpy array to PIL Image
        img = Image.fromarray(rgb)
        
        # Save image to buffer as JPEG
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG", quality=85) # 85 quality drastically reduces file size while keeping details
        
        # Generate new filename
        new_filename = uploaded_file.name.rsplit('.', 1)[0] + ".jpg"
        
        data = img_buffer.getvalue()
        
        # Explicit cleanup for this thread
        del file_bytes, rgb, img, img_buffer
        gc.collect()
        
        return new_filename, data
    except Exception as e:
        return None, f"Error processing {uploaded_file.name}: {e}"

if uploaded_files:
    if st.button("Convert Images Fast ⚡"):
        zip_buffer = io.BytesIO()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        num_files = len(uploaded_files)
        status_text.text(f"Starting parallel processing for {num_files} files...")
        
        converted_results = []
        
        # Max_workers=4 processes 4 images at the exact same time
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Map the conversion function across all uploaded files
            results = executor.map(convert_single_file, uploaded_files)
            
            for i, result in enumerate(results):
                filename, data = result
                if filename:
                    converted_results.append((filename, data))
                else:
                    st.error(data) # Contains the error message string if failed
                
                # Update progress bar smoothly
                progress_bar.progress((i + 1) / num_files)
        
        status_text.text("Zipping converted images...")
        
        # Write everything into the ZIP file quickly
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for filename, data in converted_results:
                zip_file.writestr(filename, data)
                
        status_text.text("Conversion and Zipping complete!")
        
        # Generate timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"converted_images_{timestamp}.zip"
        
        # Download button
        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip"
        )

# Custom footer with signature and clickable Instagram logo
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
