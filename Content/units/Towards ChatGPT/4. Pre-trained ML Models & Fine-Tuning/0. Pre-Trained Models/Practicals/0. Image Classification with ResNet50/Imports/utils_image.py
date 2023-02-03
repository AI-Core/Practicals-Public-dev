from google.colab import files
from PIL import Image

def open_user_image():
    '''function to open the image, apply a transform, and return the image as a torch tensor'''
    print('Upload an image, or cancel to use the default image.')
    uploaded_file = files.upload()
    if uploaded_file:
        file_path = list(uploaded_file.keys())[0]
        file_extension = file_path.split('.')[-1]
        assert file_extension in ['jpg', 'jpeg', 'png'], 'File must be a jpg, jpeg, or png.'
        img = Image.open(file_path).convert('RGB')
        print('Using the uploaded image.')
        display(img)
    else:
        print('Using default image.')
        img = Image.open('duck.jpg').convert('RGB')
        display(img)
    img_tensor = transform(img).unsqueeze(0)
    return img_tensor