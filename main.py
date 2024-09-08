from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import os
import requests


load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

def generate_image(user_prompt, model="dall-e-3", size="1024x1024",
                   quality="standard"):

    client = OpenAI(api_key=OPENAI_KEY)
    response = client.images.generate(
        model = model,
        prompt = user_prompt,
        size = size,
        quality = quality,
        n = 1
    )

    image_url = response.data[0].url
                                                                                                    
    return image_url

def format_dictionary(message:str) -> str:
    """
    Formats the output of ChatGPTs query_artist function.
    """

    genre_start = message.find("music_genre: ") + len("music_genre: ")
    mood_start = message.find(", mood: ")

    music_genre = message[genre_start:mood_start].strip()
    mood = message[mood_start + len(", mood: "):].strip()
    
    return music_genre, mood

def query_artist(artist:str) -> dict:
    """
    Given an artist or band we use ChatGPT API to
    gather information that is later used for the NFT
    image generation
    INPUT: artist (or band) name
    OUTPUT: dictionary 
    """
    artist_info = {"music_genre":None,
                   "mood":None}
    
    client = OpenAI(api_key=OPENAI_KEY)

    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", 
         "content": "You are a music expert, an user will give you a musician or band \
         and you must answer the following points in one sentence as a maximum: \
         What genre does the musician or band primarly play? What mood does his or \
         her music give (happy, sad, angry, brooding, calm, uplifting, etc)? \
         You must answer these two questions by using the following nomenclature: \
         music_genre: [answer], mood: [answer]."},
        {"role": "user", "content": f"Artist: {artist}"}
    ]
    )

    message = completion.choices[0].message.content
    genre, mood = format_dictionary(message)
    artist_info["music_genre"] = genre
    artist_info["mood"] = mood

    return artist_info

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

def create_music_prompt(music_genre, mood, day_or_night, date, state, artist) -> str:
    """
    Given details about the concert, the function creates the prompt 
    used for the create_image function.
    """

    prompt = f"Create an NFT-like image for the upcoming concert of {artist}\
               which primarly has the genre of {music_genre}, the NFT should\
               display the general mood of {mood}. Since the event will be held at\
               {day_or_night}, the image should have that lightning. The event will\
                be held in {state} so you may use some elements from that state."
    
    image_url = generate_image(prompt)

    return image_url

def get_image_bbox(*args, **kwargs):
    """
    Gets the bbox given the text and font objects.
    """
    text = kwargs['text']
    font = kwargs['font']
    # ImageDraw object
    draw = args[0]
    bbox = draw.textbbox((0,0), text, font=font)

    return bbox, draw


def image_dimensions(image):
    """
    Calculates images dimensions.
    """
    img_width, img_height = image.size

    return img_width, img_height


def calculate_text_dimensions(bbox):
    """
    Calculates the text width and height given 
    the bbox
    """
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    return text_width, text_height


def position_text(*args, **kwargs):
    """
    Returns the title, date and location text location
    for later placement. Considers all the logic for the text 
    placement given the type of text we are using.
    Returns (x,y)
    """
    placement = {'title':None, 'date':None, 'location':None}

    img_dims = args[0]
    img_w, img_h = img_dims[0], img_dims[1]

    new_dict = kwargs['values']

    for key,val in new_dict.items():
        # key is text type (ex 'title')
        t_width = val[3][0]
        t_height = val[3][1]

        if key == 'title':
            x = (img_w - t_width) // 2
            y = (img_h*0.1) # 10% of images height
        elif key == 'location':
            x = (img_w - t_width) // 2
            y = (img_h*0.1) + 80
        elif key == 'date':
            x = (img_w * 0.1)
            y = (img_h * 0.95)
        else: 
            raise Exception("Invalid text type. Check values")

        placement[key] = (x,y)
        
    return placement
        



def load_objects(title, date, location, path):
    """
    Loads fonts, Draw and the image needed for
    adding text to that specific image.
    """

    # Loads fonts
    t_font = ImageFont.truetype('arial.ttf', size=80)
    d_font = ImageFont.truetype('arial.ttf', size=40)
    l_font = ImageFont.truetype('arial.ttf', size=50)

    # Load image and create ImageDraw
    image = Image.open(path)
    draw = ImageDraw.Draw(image)

    values = {'title': [title, t_font],
              'date': [date, d_font],
              'location': [location, l_font]
              }
        # Calculate image size
    img_dims = image_dimensions(image)

    # Saves bboxes for all the text
    for key, val in values.items():
        # bbox value for 'key'
        bbox, draw = get_image_bbox(draw, text=val[0], font=val[1])
        values[key].append(bbox)

    # calculates text width and height given the bbox
    for key, val in values.items():
        bbox = values[key][2]
        width, height = calculate_text_dimensions(bbox)
        values[key].append((width, height))

    # values = {'title': [ttext, tfont, (bbox), (width,height)]}
    
    # calculates placement coordinates for the text
    # coords = {'title':(x,y), 'date':(x,y), ...}
    coords = position_text(img_dims, values=values)

    # draw on image
    # Draw the text on the image
    shadow_offset = 3

    # title
    draw.text((coords['title'][0] + shadow_offset, 
               coords['title'][1] + shadow_offset), 
               title, 
               font=values["title"][1], 
               fill="grey")  # Shadow
    draw.text((coords['title'][0], 
               coords['title'][1]), 
               title, 
               font=values['title'][1], 
               fill="white",
               stroke_width=2)  # Adjust the fill color as needed
    
    
    # draw the date on the image
    draw.text((coords['date'][0], coords['date'][1]), 
              date, font=values['date'][1], 
              fill='white')
    
    # draww the place on the image
    draw.text((coords['location'][0], coords['location'][1]), 
              location, font=values['location'][1], 
              fill='white')
    draw.text((coords['location'][0] + shadow_offset, 
               coords['location'][1] + shadow_offset), 
               location, 
               font=values["location"][1], 
               fill="grey")  # Shadow

    # Save the image
    new_path = path.replace('.jpg', '_t.jpg')
    image.save(new_path)




def add_text_to_image(**kwargs):
    """
    This function calls all the necessary functions
    to effectevily add the text to the images. 
    """
    artist = kwargs.get('artist')
    sport = kwargs.get('match')
    date = kwargs.get('date')
    location = kwargs.get('location')

    image_path = kwargs.get('image_path')

    if not image_path: 
        raise Exception("image path not provided")

    if (not artist) and (not sport):
        raise Exception("Not an artist or sport event chosen")
    else:
        if artist: 
            # music event
            title = artist 
        else:
            # sport event
            title = sport
    
    load_objects(title, date, location, image_path)
    






def main():
    
    event_type = input("\nSelect event type\n1 = Sports\n2 = Concert\n>> ")

    # Which type of event is it?
    if event_type == '2':
        artist = input("Enter artist/band name:\n>> ")
        info = query_artist(artist)
        time = input("Day or night?\n>> ")
        date = input("When will it happen?\n>> ")
        state = input("State location?\n>> ")

        info.update({'day_or_night':f'{time}',
                     'date':f'{date}', 'state':f'{state}',
                     'artist':f'{artist}'})

        url = create_music_prompt(**info)

    elif event_type == '1':
        pass
    else: 
        raise Exception("Event type not available")
    
    # We have valid url to download
    img_path = save_image(url, date, artist, event_name=None)
    add_text_to_image(image_path=img_path,
                      artist=artist,
                      date=date,
                      location=state)

if __name__ == "__main__":
    main()
