from services.youtube.key import YTB_API_KEY
from services.youtube.YouTubeVideoExtractor import YouTubeVideoExtractor
import time

start_time = time.time()

extractor = YouTubeVideoExtractor(api_key=YTB_API_KEY,days_to_consider=7,db_location="../database/transcripts.json")
channels_data = extractor.collect_channels(["FredCaldeira", "MarceloBechler1","TNTSportsBR"])

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Time taken: {elapsed_time:.2f} seconds")