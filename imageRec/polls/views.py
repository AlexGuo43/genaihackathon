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


def homepage(request):
    context = {
        "UserForm": UserForm(),
        "object_detected": None,
        "repurposable": None,
        "repurpose_suggestions": None,
        "uploaded_image_url": None,
    }
    context = {
        "UserForm": UserForm(),
    }
    # Handling user info being submitted
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded image file
            image_file = request.FILES.get('userImage')
            if(image_file):
                print(f"Uploaded image file: {image_file.name}")
            project_id = 'glossy-premise-418818'
            # Initialize Google Cloud Storage client
            storage_client = storage.Client(project='glossy-premise-418818')

            # Specify your Google Cloud Storage bucket name
            bucket_name = 'bucket1forgenai'  # Replace 'your-bucket-name' with your actual GCS bucket name

            # Specify the destination path within the bucket to upload the file
            destination_blob_name = 'userUploads/' + image_file.name  # You can change the destination directory as needed

            # Upload the file to Google Cloud Storage
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_file(image_file)

            # Optionally, set the public access permission to the uploaded file
            blob.make_public()

            # Save the form data to your Django model or perform other actions
            form.save()

            vertexai.init(project="glossy-premise-418818", location="us-central1")

            # Get the public URL of the uploaded image
            uploaded_image_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
            context['uploaded_image_url'] = uploaded_image_url
            # Initialize GenerativeModel and prepare contents for API call
            multimodal_model = GenerativeModel("gemini-1.0-pro-vision")
            image = Part.from_uri(uploaded_image_url, mime_type="image/jpeg")
            prompt = "Describe the object in the image, lowest amount of words possible with no article words"
            contents = [image, prompt]

            # Configure generation settings and safety settings
            generation_config = GenerationConfig(
                temperature=0.0,
                top_p=0,
                top_k=0,
                candidate_count=1,
                max_output_tokens=1024,
            )
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            }

            # Generate content using the API
            responses = multimodal_model.generate_content(
                contents,
                safety_settings=safety_settings,
                stream=True
            )

            # Extract object description from API response
            for response in responses:
                object_detected = response.text
                context['object_detected'] = object_detected

            # Check if the object is repurposable
            repurposable_prompt = f"is {object_detected} repurposeable? Output should be only yes or no, be realistic about the object and think about the state it is in, for example damages"
            repurposable = get_chat_response(chat, repurposable_prompt)
            context['repurposable'] = repurposable

            # If repurposable, get DIY repurpose suggestions
            if repurposable == "yes":
                diy_repurpose_prompt = f"Instead of throwing {object_detected} out, is there a way to repurpose this using DIY. Print 5 of them in a numbered list with no title, make sure not to repeat the same idea"
                model = GenerativeModel("gemini-1.0-pro")
                chat = model.start_chat()
                repurpose_suggestions = get_chat_response(chat, diy_repurpose_prompt)
                context['repurpose_suggestions'] = repurpose_suggestions
        else:
            return render(request, 'polls/homepage.html', context)
    return render(request, 'polls/homepage.html', context)

def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)
