# -*- coding: utf-8 -*-
"""home_office_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mRe79RzyDH3GxFK8J9SodFHll-k7UNq6
"""

import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

import cv2
import matplotlib.pyplot as plt
import torch
import torchvision
from PIL import Image
import gdown
import json
  
    


#initial page configuration
st.set_page_config(page_title='Office', page_icon='random', layout='centered', initial_sidebar_state='auto')


#logos for nural and hasty
nural_logo = 'images/Nural logo.png'
hasty_logo = 'images/Hasty.png'

#create columns for logos
col1, col2 = st.beta_columns(2)

#place the logos at the top of the page
with col1:
  st.image(nural_logo)
  st.write('Nural Research')

with col2:
  st.image(hasty_logo)

#title
st.title('Home office classifier project')
st.write('Use the sidebar on the left to upload your image and watch the magic happen')

with st.sidebar:
  my_expander = st.beta_expander('Upload image')
  with my_expander:
    
    uploaded_file = st.file_uploader("Upload an image")


@st.cache
def downloading_from_gdrive():
	with st.spinner('Downloading the model...'):
		url = 'https://drive.google.com/uc?id=1_ALUSj4aRHw3-lEGuxeDVOB-nJKb09PL'
		output = 'model.pt'
		gdown.download(url, output, quiet=False)
	return 

downloading_from_gdrive()

with open('class_mapping.json') as data:
    mappings = json.load(data)

class_mapping = {item['model_idx']: item['class_name'] for item in mappings}

if uploaded_file is not None:
  
  if __name__ == '__main__':
      device = torch.device('cpu' if not torch.cuda.is_available() else 'cuda')
      # Load the model
      model = torch.jit.load('/app/home-office-classifier/model.pt')
      model.to(device)

      image = Image.open(uploaded_file)
      # Resize your image if needed like so:
      # image = image.resize((some_width, some_height))
      image = np.array(image).astype(np.uint8)
      x = torch.from_numpy(image).permute(2, 0, 1).float()
      x = x.to(device)
      # Get predictions from model
      y = model([{'image': x}])

      # Post process the predicitons with nms:
      to_keep = torchvision.ops.nms(y['pred_boxes'], y['scores'], 0.2)
      y['pred_boxes'] = y['pred_boxes'][to_keep]
      y['pred_classes'] = y['pred_classes'][to_keep]

#create dictionary for the classes
      class_list = {}
      for i in range(6):
          class_list[i] = 0


      # Draw the predictions on the image
      for label, bbox in zip(y['pred_classes'], y['pred_boxes']):
          bbox = list(map(int, bbox))
          x1, y1, x2, y2 = bbox
          class_idx = label.item()
          class_name = class_mapping[class_idx] 
          cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), thickness=4)
          cv2.putText(
              image,
              class_name,
              (x1, y1),
              cv2.FONT_HERSHEY_SIMPLEX,
              1,
              (255, 0, 0)
          )
          class_list[label.item()] +=1
 
       

      plt.imshow(image)
      final = plt.gcf()

      #the below gives us the output after processing

      st.write('Your image with predicted items')
      st.write(final)

      st.write('In your image we see:')

      


      cols = st.beta_columns(2)

      cols[0].markdown('**Class type**')
      cols[1].markdown('**Number found in the image**')
      for i,j in enumerate(class_mapping):
          cols[0].markdown(class_mapping[j])
          cols[1].write(class_list[i])

