from dotenv import load_dotenv
from openai import OpenAI
import os

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


def create_music_prompt(music_genre, mood, day_or_night, date, state, artist):
    """
    Given details about the concert, the function creates the prompt 
    used for the create_image function.
    """

    prompt = f"Create an NFT-like image for the upcoming concert of {artist}\
               which primarly has the genre of {music_genre}, the NFT should\
               display the general mood of {mood}. Since the event will be held at\
               {day_or_night}, the image should have that lightning. The event will\
                be held in {state} so you may use some elements from that state."
    
    print(generate_image(prompt))
    
    






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

        create_music_prompt(**info)

    elif event_type == '1':
        pass
    else: 
        raise Exception("Event type not available")
    

if __name__ == "__main__":
    main()

"""
We want to create NFT images for the following categories: 
- Sports
    - Team mascot? (of preffered team)
    - Day or night?
    - State location?
    - Date?
- Concerts
    - Artist?
        - We can get the following info with this question:
        - Genre
        - "vibe"
    - Day or night?
    - Date?
    - State location?

I need to think about a "special element" that adds randonmness 
which will make all the NFTs unique. 



"""