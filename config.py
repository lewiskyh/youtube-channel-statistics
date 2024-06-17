import os
from dotenv import load_dotenv

## To load environment variable - YouTube API KEY
load_dotenv()


class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
