import os
import requests
from urllib.parse import urlparse, unquote
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageFilter
import pandas as pd
import certifi

# Set the path to your Tesseract-OCR executable
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'  # Update this path as necessary

# Directory to store downloaded PDFs
pdf_directory = 'pdfs'
os.makedirs(pdf_directory, exist_ok=True)

def download_pdf(url):
    """Download a PDF from a URL and save it to a file, selectively disabling SSL verification."""
    parsed_url = urlparse(url)
    file_name = os.path.basename(unquote(parsed_url.path))
    file_path = os.path.join(pdf_directory, file_name)

    try:
        # Using certifi to handle SSL certificate verification
        # Disable verification only for specific trusted URLs
        if "supremecourt.gov.np" in url:
            response = requests.get(url, stream=True, verify=False)  # Insecure, use with caution
        else:
            response = requests.get(url, stream=True, verify=certifi.where())

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            print(f"Failed to download {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def clean_image(image):
    """Crop the image to remove headers and footers."""
    width, height = image.size
    header_height = 50  # pixels to remove from the top
    footer_height = height - 50  # start of footer to remove from the bottom
    return image.crop((0, header_height, width, footer_height))

def remove_watermarks(image):
    """Applies a median filter to reduce or remove watermarks."""
    gray = image.convert('L')  # Convert image to grayscale
    return gray.filter(ImageFilter.MedianFilter(size=3))

def enhance_image(image):
    """Enhance the image to improve OCR accuracy."""
    enhanced_image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
    return enhanced_image

def process_pdf(file_path):
    """Convert PDF to images, preprocess them, and perform OCR."""
    images = convert_from_path(file_path, dpi=300)
    text_outputs = []
    for image in images:
        clean_img = clean_image(image)
        no_watermark_img = remove_watermarks(clean_img)
        enhanced_img = enhance_image(no_watermark_img)
        text = pytesseract.image_to_string(enhanced_img, lang='nep')
        text_outputs.append(text)
    return '\n'.join(text_outputs)

# Path to the Excel file
excel_path = './courtdata_update.xlsx'
df = pd.read_excel(excel_path)
df['description'] = ''

for index, row in df.iterrows():
    pdf_url = row['pdf_link']
    local_pdf_path = download_pdf(pdf_url)
    if local_pdf_path:
        extracted_text = process_pdf(local_pdf_path)
        df.at[index, 'description'] = extracted_text

# Save the updated DataFrame
df.to_excel('./court_data_add_description.xlsx', index=False)

