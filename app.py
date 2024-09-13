from flask import Flask, request, send_file
from generate_image import generate_image, format_dictionary, \
                            query_artist, create_music_prompt
from pil_editing import get_image_bbox, image_dimensions,  \
                        calculate_text_dimensions, position_text, load_objects, add_text_to_image
from dotenv import load_dotenv
from openai import OpenAI
import os
import requests


def save_image(url:str, date, artist=None, event_name=None) -> None: 
    """
    Locally saves the image provided by ChatGPTs API.
    """

    # Replace slashes in date to avoid directory issues
    date = date.replace("/", "-")

    file_name = f"{artist}_{date}" if artist else f"{event_name}_{date}"
    file_name = file_name + ".jpg" 

    target_folder = "nft_images"

    file_path = os.path.join(target_folder, file_name)

    response = requests.get(url)

    if response.status_code == 200:
        # Open the file in binary mode: 
        with open(file_path, "wb") as file:
            file.write(response.content)
        print('Imaged save succesfully')
        return file_path
    else: 
        print(f"Failed to retrieve the image with status code: {response.status_code}")


load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
"""
INFO REQUIRED: 
    - Artist name
    - Date
    - State location
We obtain this information with the USER PROMPT
"""

app = Flask(__name__)

@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    data = request.json  # JSON data from the other site

    ##### recibimos info
    variables = data.get('variables')  # Extract the necessary variables    


    artist = variables["artist"]
    location = variables["location"]
    date = variables["date"]
    time = "night" ##### 


    info = query_artist(artist)

    info.update({'day_or_night':f'{time}',
                    'date':f'{date}', 'state':f'{location}',
                    'artist':f'{artist}'})

    url = create_music_prompt(**info) # creates music prompt, calls another fun
                                      # returns image url

    file_path = save_image(url, date, artist)


    new_path = add_text_to_image(image_path=file_path,
                      artist=artist,
                      date=date,
                      location=location)
    print(new_path)

    # Return the generated image file
    return new_path

if __name__ == '__main__':
    app.run(host='0.0.0.0')
