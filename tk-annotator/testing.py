import pandas as pd
import fiftyone as fo

df = pd.read_csv('ISIC_2020_Training_GroundTruth_v2.csv')

fo.delete_dataset("melanoma_dataset")  # dangerous?
dataset = fo.Dataset(name="melanoma_dataset")

# Add images with labels
for _, row in df.iterrows():
    sample = fo.Sample(filepath=f"train/{row['image_name']}.jpg")
    sample["label"] = fo.Classification(label=row["diagnosis"])  # Adjust column name if needed
    dataset.add_sample(sample)

dataset.persistent = True  # Keep dataset saved
session = fo.launch_app(dataset)
session.wait()