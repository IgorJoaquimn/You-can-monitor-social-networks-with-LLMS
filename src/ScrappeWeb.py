from utils.keys import youTubeApiKey  # Import your YouTube API key from keys.py
from YouTubeVideoExtractor import YouTubeVideoExtractor
import time

start_time = time.time()

extractor = YouTubeVideoExtractor(api_key=youTubeApiKey)
channels_data = extractor.save_in_database(["FredCaldeira", "MarceloBechler1","TNTSportsBR"])

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Time taken: {elapsed_time} seconds")