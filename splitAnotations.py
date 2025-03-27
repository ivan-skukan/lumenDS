# Read csv pandas

import shutil
import pandas as pd
import os
metadata = pd.read_csv('data/ISIC_2020_Training_GroundTruth_v2.csv')
print(metadata.head())

# From metadata choose all the benign_malignant == malignant
malignants = metadata[metadata['benign_malignant'] == 'malignant']
print(len(malignants))

# Select benigns randomly so that |malignant + benign| = 2000
benigns = metadata[metadata['benign_malignant'] == 'benign'].sample(n=2000-len(malignants), random_state=1)
print(len(benigns))

# Join these 2 sets
metadata = pd.concat([malignants, benigns])

# Shuffle this list
metadata = metadata.sample(frac=1).reset_index(drop=True)

# There is a column named image_name, split the data into 4 sets named "neven", "stjepan", "ivan", "vedran" so that each contains 1000 images
neven = metadata[:1000]
stjepan = metadata[500:1500]
ivan = metadata[1000:2000]
vedran = pd.concat([metadata[1500:], metadata[:500]])
print(len(neven), len(stjepan), len(ivan), len(vedran))

if not os.path.exists('data/neven'):
    os.makedirs('data/neven')
if not os.path.exists('data/stjepan'):
    os.makedirs('data/stjepan')
if not os.path.exists('data/ivan'):
    os.makedirs('data/ivan')
if not os.path.exists('data/vedran'):
    os.makedirs('data/vedran')

# There is a column image_name, from folder of images data/train, copy those images to folders data/neven, data/stjepan, data/ivan, data/vedran
for index, row in neven.iterrows():
    shutil.copy(f'data/train/{row["image_name"]}.jpg', f'data/neven/{row["image_name"]}.jpg')
for index, row in stjepan.iterrows():
    shutil.copy(f'data/train/{row["image_name"]}.jpg', f'data/stjepan/{row["image_name"]}.jpg')
for index, row in ivan.iterrows():
    shutil.copy(f'data/train/{row["image_name"]}.jpg', f'data/ivan/{row["image_name"]}.jpg')
for index, row in vedran.iterrows():
    shutil.copy(f'data/train/{row["image_name"]}.jpg', f'data/vedran/{row["image_name"]}.jpg')
