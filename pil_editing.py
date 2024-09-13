from PIL import Image, ImageDraw, ImageFont
import os

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

    return new_path




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
    
    new_path = load_objects(title, date, location, image_path)

    full_path = os.path.abspath(new_path)
    
    return full_path