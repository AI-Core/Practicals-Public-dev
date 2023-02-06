###############################################################################
###                    Don't change this part                               ###
###############################################################################
from image_segmentation_aicore.utils import (ImageSegmentation,
                                             perform_segmentation,
                                             decode_image,
                                             save_image_to_s3)
import fastapi
from fastapi import File, UploadFile
import uvicorn


model = ImageSegmentation('model.tar.gz')
api = fastapi.FastAPI() 

@api.post("/image") 
async def process_input(image_encoded: UploadFile = File(...)): 
    image_name = image_encoded.filename # Name of the image
    image = await image_encoded.read() # Read the encoded image

###############################################################################
    # Start your code at this point
    # Don't forget to keep the indentation, so you only modify this function

    decoded_image = decode_image(image)
    input_name = image_name.split('.')[0] + '/' + 'input.png'
    save_image_to_s3(decoded_image, input_name, bucket_name='data-aicore-test')
    segmented_image = perform_segmentation(model, decoded_image)
    output_name = image_name.split('.')[0] + '/' + 'output.png'
    save_image_to_s3(segmented_image, output_name, bucket_name='data-aicore-test')
    
    # print(decoded)
    # decoded = decode_image(image)
###############################################################################
###                    Don't change this part                               ###
###############################################################################
    return "Images uploaded successfully"

if __name__ == '__main__':
    uvicorn.run(api, host='127.0.0.1', port=8000, debug=True)