import streamlit as st
from PIL import Image
import io
import requests

st.title("Saudi Car License Plate Recognition")


uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# def convert_type_of_files(files):
#     converted_files = []
#     for file in files:
#         image_data = file.read()
#         converted_files.append((file.name,image_data))
        
#     return converted_files
        
# files = convert_type_of_files(uploaded_files)       
#print(files)

if uploaded_file is not None:
    
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    st.image(image, caption='Loading...', use_column_width=True)

    url = 'http://127.0.0.1:8000/analyze/'
    files = {'files': (uploaded_file.name,image_bytes)}
    response = requests.post(url,files= files)
    print(response)
    english_text = response.json()['results'][0][0]['english_text']
    arabic_text = response.json()['results'][0][0]['arabic_text']
    st.text_area("The Recognized license Plate in image","Arabic Text:\t"+ arabic_text + "\nEnglish Text:\t " + english_text)
    
    
    