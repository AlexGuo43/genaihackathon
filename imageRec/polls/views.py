from django.shortcuts import render
from google.cloud import storage
from .forms import UserForm
# Create your views here.


def homepage(request):
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
            # Initialize Google Cloud Storage client
            storage_client = storage.Client()

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
        else:
            return render(request, 'polls/homepage.html', context)
    return render(request, 'polls/homepage.html', context)
