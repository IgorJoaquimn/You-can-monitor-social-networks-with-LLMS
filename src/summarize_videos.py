# %%
import pandas as pd

# %%
df = pd.read_json("../database/transcripts.json")
df.head()

# %%
import requests

url = "https://github.com/IgorJoaquimn/Automatic-Chunk-Detector-PT-BR/raw/main/models/ChunkDetector.ai"
PATH = "../models/ChunkDetector.ai"

response = requests.get(url)
with open(PATH, "wb") as file:
    file.write(response.content)

# %%
from utils.utils import *
model = ChunkDetector(768).cuda()
model.load_state_dict(torch.load(PATH))
model.eval()

# %%
for idx, video in tqdm(df.iterrows()):
    phrases = [phrase["text"] for phrase in video["transcript"]]
    embeddings = embed(phrases)

    paragraphs = []
    last = 0

    context = [phrases[0]]
    for i in range(1,len(embeddings)):
        similarity_score = model(embeddings[i - 1].view(1, -1).cuda(), embeddings[i].view(1, -1).cuda())
        pred = similarity_score >= 0.5
        if(pred):
            context.append(phrases[i])
        else:
            if(len(context) >= 3):
                paragraphs.append(" ".join(context))
            context = [phrases[i]]
    
    if len(context) >= 3:
        paragraphs.append(" ".join(context))

    paragraphs = " Frase: " + " Frase: ".join(paragraphs)
    df.loc[idx, "text"] = paragraphs

# %%
df["text"] = "Titulo: " + df["title"] + " Autor: " + df["channel_username"] + " " + df["text"]

# %%
# Get the values of the "text" column and join them with "\n\n"
text_content = "\n\n".join(df["text"].values)

# Write the text content to a file
with open("../documents/transcript.txt", "w") as f:
    f.write(text_content)


