from transformers import CLIPModel, AutoProcessor
from PIL import Image
import torch

print('initializing model')
model_id = 'openai/clip-vit-base-patch32'
device = "cuda" if torch.cuda.is_available() else "cpu"

model = CLIPModel.from_pretrained(model_id).to(device)
image_processor = AutoProcessor.from_pretrained(model_id)



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

    return text_dict[torch.argmax(probs).item()]



def contrastive_reply(image, mode = 'helmet') :

    assert mode in ['helmet', 'count_people'], 'mode should be either "helmet" or "count_people"'

    img=None
    if type(img) == str :
        if img.startswith('http') :
            img = Image.open(requests.get(image, stream=True).raw)
        else :
            img = Image.open(image)

    else : 
        img = image
    
    if mode == 'helmet' :
        questions = ["a person wearing helmet", "a person not wearing helmet"]
    elif mode == 'count_people' :
        questions = ["more than 1 person", "1 person"]

    return process_image(img, questions)



    

