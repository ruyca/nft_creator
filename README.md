# nft_creator
## Overview
nft_creator is a Python-based project designed to generate tailored NFT images for upcoming concerts. Each NFT image is customized for specific artists performing at these events. The project integrates with the OpenAI API to automatically create unique, artist-specific images and includes a small Flask app that enables an endpoint for easy, on-demand image generation.

## Features
- **Tailored NFT Images**: Generate unique NFTs based on upcoming concerts and the artists performing.
-** OpenAI API Integration**: Uses OpenAI's API to create high-quality, artist-specific images.
- **Flask App**: A lightweight Flask app that provides an API endpoint to generate NFT images automatically.
- **NFT-Ready**: Images can be minted as NFTs and used for exclusive concert tickets or collectibles.


## Installation
Clone the repository:

1. Clone the repository:

```
git clone https://github.com/ruyca/nft_creator.git
cd nft_creator
```

2. Install the require dependencies:

```
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
4. Run the Flask app:
```
python app.py
```

## Usage
### API Endpoint
The Flask app exposes an API endpoint that can be used to request automatic NFT image generation. To create an NFT image for an artist, send a POST request with relevant information (e.g., artist name, concert details).

Example Request:

POST /generate_image
{
  "variables":{
    {"artist": artist,
    "location": location,
    "date": date
  }
}

The API will return the generated image in response.


## License
This project is licensed under the MIT License - see the LICENSE file for details.
