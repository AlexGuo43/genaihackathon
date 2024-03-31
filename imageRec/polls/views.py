from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from google.cloud import storage
from .forms import UserForm
import vertexai
import http.client
import typing
import urllib.request
import IPython.display
from PIL import Image as PIL_Image
from PIL import ImageOps as PIL_ImageOps
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold, Image, Part, GenerationConfig
from vertexai.generative_models import GenerativeModel, ChatSession


# Initialize Vertex AI
vertexai.init(project="glossy-premise-418818", location="us-central1")

# Function to get chat response


def get_chat_response(chat, prompt):
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)


def homepage(request):
    context = {
        "UserForm": UserForm(),
        "object_detected": None,
        "repurposable": None,
        "repurpose_suggestions": None,
        "uploaded_image_url": None
    }

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES.get('userImage')
            # Assume code to upload the image to Google Cloud Storage and get `uploaded_image_url` goes here

            # Upload the image to Google Cloud Storage
            project_id = 'glossy-premise-418818'
            storage_client = storage.Client(project='glossy-premise-418818')
            bucket_name = 'bucket1forgenai'
            destination_blob_name = 'userUploads/' + image_file.name
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_file(image_file)
            blob.make_public()

            # Initialize the GenerativeModel with your model
            multimodal_model = GenerativeModel("gemini-1.0-pro-vision")
            uploaded_image_url = f"gs://{
                bucket_name}/{destination_blob_name}"

            # Prepare the content for the model
            image = Part.from_uri(uploaded_image_url, mime_type="image/jpeg")
            prompt = "Describe the object in the image, the lowest amount of words possible with no article words"
            contents = [image, prompt]

            # Generate content with the model
            responses = multimodal_model.generate_content(
                contents,
                # Assuming safety_settings and generation_config are defined elsewhere
                safety_settings={},
                stream=True
            )

            # Extract object description from the response
            # This is a simplified extraction logic; adjust based on your actual response structure
            for response in responses:
                object_detected = response.text  # Simplified for demonstration
                break  # Assuming we take the first response for simplicity

            context['object_detected'] = object_detected

            # Further processing to check if the object is repurposable and get suggestions goes here...

    return render(request, 'polls/homepage.html', context)
