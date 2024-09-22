import streamlit as st
import pandas as pd
import torch
from transformers import BertTokenizer
from torch.nn import functional as F

# Load the model and tokenizer
@st.cache(allow_output_mutation=True)
def load_model():
    model = NepaliLegalClassifier.load_from_checkpoint('checkpoints/best-checkpoint.ckpt')
    model.eval()
    return model

@st.cache(allow_output_mutation=True)
def load_tokenizer():
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    return tokenizer

# Function to predict the class
def predict(text, model, tokenizer):
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=256,
        return_attention_mask=True,
        truncation=True,
        padding='max_length',
        return_tensors='pt'
    )
    
    input_ids = encoding['input_ids']
    attention_mask = encoding['attention_mask']
    
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs[1]
        preds = F.softmax(logits, dim=1)
        predicted_class = preds.argmax(dim=1).item()
        
    return predicted_class

# Streamlit app layout
st.title("Nepali Legal Text Classifier")
st.write("Enter a legal description below to classify it.")

# Text input
user_input = st.text_area("Legal Description", height=200)

# Load model and tokenizer
model = load_model()
tokenizer = load_tokenizer()

# Button to classify
if st.button("Classify"):
    if user_input:
        class_index = predict(user_input, model, tokenizer)
        class_name = label_encoder.inverse_transform([class_index])[0]  # Assuming you have label_encoder available
        st.success(f'The predicted class is: {class_name}')
    else:
        st.error("Please enter a legal description.")
