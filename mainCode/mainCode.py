import vertexai

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Image,
    Part,
)

multimodal_model = GenerativeModel("gemini-1.0-pro-vision")

import http.client
import typing
import urllib.request

import IPython.display
from PIL import Image as PIL_Image
from PIL import ImageOps as PIL_ImageOps


def display_images(
    images: typing.Iterable[Image],
    max_width: int = 600,
    max_height: int = 350,
) -> None:
    for image in images:
        pil_image = typing.cast(PIL_Image.Image, image._pil_image)
        if pil_image.mode != "RGB":
            # RGB is supported by all Jupyter environments (e.g. RGBA is not yet)
            pil_image = pil_image.convert("RGB")
        image_width, image_height = pil_image.size
        if max_width < image_width or max_height < image_height:
            # Resize to display a smaller notebook image
            pil_image = PIL_ImageOps.contain(pil_image, (max_width, max_height))
        IPython.display.display(pil_image)


def get_image_bytes_from_url(image_url: str) -> bytes:
    with urllib.request.urlopen(image_url) as response:
        response = typing.cast(http.client.HTTPResponse, response)
        image_bytes = response.read()
    return image_bytes


def load_image_from_url(image_url: str) -> Image:
    image_bytes = get_image_bytes_from_url(image_url)
    return Image.from_bytes(image_bytes)


def get_url_from_gcs(gcs_uri: str) -> str:
    # converts gcs uri to url for image display.
    url = "https://console.cloud.google.com/" + gcs_uri.replace("gs://", "").replace(
        " ", "%20"
    )
    return url


def print_multimodal_prompt(contents: list):
    """
    Given contents that would be sent to Gemini,
    output the full multimodal prompt for ease of readability.
    """
    for content in contents:
        if isinstance(content, Image):
            display_images([content])
        elif isinstance(content, Part):
            url = get_url_from_gcs(content.file_data.file_uri)
            IPython.display.display(load_image_from_url(url))
        else:
            print(content)


# Load image from Cloud Storage URI
gcs_uri = "gs://bucket1forgenai/old t shirt.jpg"

# Prepare contents
image = Part.from_uri(gcs_uri, mime_type="image/jpeg")
prompt = "Describe the scene?"
contents = [image, prompt]

responses = multimodal_model.generate_content(contents, stream=False)

# Prepare contents
prompt = "Describe the object in the image, lowest amount of words possible with no article words"
contents = [image, prompt]

# Use a more deterministic configuration with a low temperature
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini
generation_config = GenerationConfig(
    temperature=0.0,          # higher = more creative (default 0.0)
    top_p=0,                # higher = more random responses, response drawn from more possible next tokens (default 0.95)
    top_k=0,                 # higher = more random responses, sample from more possible next tokens (default 40)
    candidate_count=1,
    max_output_tokens=1024,   # default = 2048
)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

#BLOCK_ONLY_HIGH - block when high probability of unsafe content is detected
#BLOCK_MEDIUM_AND_ABOVE - block when medium or high probablity of content is detected
#BLOCK_LOW_AND_ABOVE - block when low, medium, or high probability of unsafe content is detected
#BLOCK_NONE - always show, regardless of probability of unsafe content

responses = multimodal_model.generate_content(
    contents,
#    generation_config=generation_config,
    safety_settings=safety_settings,
    stream=True
)

#print("-------Prompt--------")
#print_multimodal_prompt(contents)

#print("\n-------Response--------")
for response in responses:
    reason = response.candidates[0].finish_reason
    #print(reason)
    if(reason==1):
        object = response.text #object detected by Gemini stored 
        print("Looks like a"+object)
        print("Instead of sending it to the landfill, here are some suggestions!\n")
    elif(reason !=1):
        print("Invalid or inappropriate photo")
        quit()

#Now to create the possible ways to repurpose the object.
from vertexai.generative_models import GenerativeModel, ChatSession
vertexai.init(project="glossy-premise-418818", location="us-central1")
model = GenerativeModel("gemini-1.0-pro")
chat = model.start_chat()

def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

#Check if it is repurposeable 
prompt = ("is"+object+"repurposeable? Output should be only yes or no, be realistic about the object and think about the state it is in, for example damages, condition, uses");
repurposable = (get_chat_response(chat, prompt))
if(repurposable=="no"):
   print("Unfortunately this is not repurposable, please recycle or dispose responsibly.")

if(repurposable=="yes"):
    prompt = ("instead of throwing"+object+"out, is there a way to repurpose this using DIY. print max 5 of them in a numbered ordered list with no title and lead each idea with the idea in bold, make sure not to repeat the same idea")
    print(get_chat_response(chat, prompt))


    
