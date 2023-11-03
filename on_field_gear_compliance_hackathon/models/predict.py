from transformers import CLIPModel, AutoProcessor
from PIL import Image
import numpy as np
from on_field_gear_compliance_hackathon.constants import DATA_DIR
from deepface import DeepFace
import uuid
import torch
import os

print('initializing model')
model_id = 'openai/clip-vit-base-patch32'
device = "cuda" if torch.cuda.is_available() else "cpu"

model = CLIPModel.from_pretrained(model_id).to(device)
image_processor = AutoProcessor.from_pretrained(model_id)

verified_images = os.path.join(DATA_DIR, 'verified_images')


def get_image(image) :

    img=None
    # print(type(image))
    if type(image) == str :
        if image.startswith('http') :
            img = Image.open(requests.get(image, stream=True).raw)
        else :
            img = Image.open(image)

    else : 
        img = image

    return img


def process_image(img, text) :

    assert type(text) == list, 'text should pe passed as a list'
    assert len(text) > 1, 'text should contain more than 1 statements'

    text_dict = {idx : items for idx, items in enumerate(text)}
    # print(text)
    # print(img)
    inputs = image_processor(
        text=text, images=img, return_tensors="pt", padding=True
    ).to(device)
    # print(inputs)

    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    print(probs)

    return text_dict[torch.argmax(probs).item()]



def contrastive_reply(image, mode = 'helmet') :

    assert mode in ['helmet', 'count_people'], 'mode should be either "helmet" or "count_people"'

    img = get_image(image)
    
    if mode == 'helmet' :
        questions = ["a person wearing helmet", "a person not wearing helmet"]
    elif mode == 'count_people' :
        questions = ["a photo with more than 1 person", "a photo with 1 person", "a photo with no person"]

    return process_image(img, questions)



def add_face(image, name) :

    assert type(name) == str, 'name should be a string'

    img = get_image(image)
    pil_img = Image.fromarray(np.uint8(img)).convert('RGB')

    pil_img.save(os.path.join(DATA_DIR, f'verified_images/{name}.jpeg'))

    return "!!!Person added successfully!!!"


def recognize(image) :

    img = get_image(image)
    pil_img = Image.fromarray(np.uint8(img)).convert('RGB')
    path = os.path.join(DATA_DIR, f'raw_images/{uuid.uuid4().hex}.jpeg')
    pil_img.save(path)

    recognition = DeepFace.find(img_path = path, db_path=verified_images, enforce_detection =False)[0]
    recognition = recognition.sort_values('VGG-Face_cosine', ascending = False)
    img_path = recognition.head(1).identity.values[0]
    print(img_path)
    print(recognition.identity)
    print(recognition['VGG-Face_cosine'])

    recognized_person = Image.open(img_path)    

    return recognized_person

