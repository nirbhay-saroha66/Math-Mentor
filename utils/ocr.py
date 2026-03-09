import easyocr
from PIL import Image
import io
import numpy as np
import streamlit as st


# ===============================
# Cached OCR Model
# ===============================
@st.cache_resource
def load_ocr_reader():
    print("Loading OCR model (first time)...")
    return easyocr.Reader(['en'])


def extract_text_from_image(image_file):

    try:

        reader = load_ocr_reader()

        image = Image.open(io.BytesIO(image_file.read()))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image_array = np.array(image)

        results = reader.readtext(image_array)

        text = '\n'.join([line[1] for line in results])

        return text

    except Exception as e:

        return f"Error extracting text: {str(e)}"