from transformers import BertTokenizerFast, BertModel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers import pre_tokenizers
import torch
import torch.nn as nn
from tqdm import tqdm

from torch.utils.data import TensorDataset, DataLoader, SequentialSampler


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = BertTokenizerFast.from_pretrained("neuralmind/bert-base-portuguese-cased", model_max_length=512)
pre_tokenizer = pre_tokenizers.Sequence([Whitespace()])
tokenizer.pre_tokenizer = pre_tokenizer
bert_model = BertModel.from_pretrained("neuralmind/bert-base-portuguese-cased").to(device)

def embed(sentence):
    # Encode input sentence using tokenizer
    encoded_data = tokenizer(sentence, 
                                               add_special_tokens=True,
                                               return_attention_mask=True,
                                               padding='longest',
                                               truncation=True,
                                               max_length=256,
                                               return_tensors='pt')
    
    input_ids = encoded_data['input_ids'].to(device)
    attention_masks = encoded_data['attention_mask'].to(device)
    
    # Create a TensorDataset and DataLoader
    dataset = TensorDataset(input_ids, attention_masks)
    dataloader = DataLoader(dataset, sampler=SequentialSampler(dataset), batch_size=750)
    
    context_embeddings = torch.empty((0, 768)).cpu()
    
    # Iterate through batches and generate embeddings
    for batch in dataloader:
        # Move data to the device
        input_ids, attention_mask = batch
        
        with torch.no_grad():
            # Forward pass through the model
            outputs = bert_model(input_ids=input_ids, attention_mask=attention_mask)
        
        # Extract embeddings (CLS token outputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        # Concatenate embeddings
        context_embeddings = torch.cat([context_embeddings.cpu(), embeddings.cpu()], dim=0)
    
    return context_embeddings

class ChunkDetector(nn.Module):
    def __init__(self, input_size,hidden_size = 200):
        super().__init__()
        self.hidden_size = torch.tensor(hidden_size).cuda()
        
        self.Potency = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.Sigmoid()
        )
        self.Sign = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.Tanh()
        )
        self.Value = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU()
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, context, sentence):
        context_key     = self.Potency(sentence)    * self.Sign(context)   +  self.Value(context)
        sentence_key    = self.Potency(context)     * self.Sign(sentence)  +  self.Value(sentence)

        context_key     = nn.functional.normalize(context_key, p=2, dim=1)
        sentence_key    = nn.functional.normalize(sentence_key, p=2, dim=1)
        
        similarity = torch.sum(context_key * sentence_key, dim=1)/torch.sqrt(self.hidden_size)
        similarity = self.sigmoid(similarity)
        return similarity    