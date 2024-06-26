import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import transformers
from torch.utils.data import DataLoader, Dataset
from torchsummary import summary
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


class BertDataset(Dataset):
    def __init__(self, tokenizer, max_length, data_path):
        super(BertDataset, self).__init__()
        self.root_dir = '.'
        self.train_csv = pd.read_csv(data_path)
        self.tokenizer = tokenizer
        self.target = self.train_csv.iloc[:, 1]
        self.max_length = max_length

    def __len__(self):
        return len(self.train_csv)

    def __getitem__(self, index):

        text1 = self.train_csv.iloc[index, 0]

        inputs = self.tokenizer.encode_plus(
            text1,
            None,
            pad_to_max_length=True,
            add_special_tokens=True,
            return_attention_mask=True,
            max_length=self.max_length,
        )
        ids = inputs["input_ids"]
        token_type_ids = inputs["token_type_ids"]
        mask = inputs["attention_mask"]

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            'target': torch.tensor(self.train_csv.iloc[index, 1], dtype=torch.long)
        }


# NOTE: BERT CLASS

class BERT(nn.Module):
    def __init__(self, num_classes, model_name="bert-base-uncased"):
        super(BERT, self).__init__()
        self.bert_model = transformers.BertModel.from_pretrained(
            model_name)
        self.out = nn.Linear(768, num_classes)

    def forward(self, ids, mask, token_type_ids):
        _, o2 = self.bert_model(ids, attention_mask=mask,
                                token_type_ids=token_type_ids, return_dict=False)

        out = self.out(o2)

        return out


# NOTE: FINETUNE FUNCTION HERE
def finetune(epochs, dataloader, model, loss_fn, optimizer):
    model.train()
    for epoch in range(epochs):
        print(epoch)

        for batch, dl in enumerate(dataloader):
            ids = dl['ids']
            token_type_ids = dl['token_type_ids']
            mask = dl['mask']
            label = dl['target']
            label = label.unsqueeze(1)
            optimizer.zero_grad()

            output = model(
                ids=ids,
                mask=mask,
                token_type_ids=token_type_ids)
            label = label.type_as(output)

            loss = loss_fn(output, label)
            loss.backward()

            optimizer.step()

            pred = np.where(output >= 0, 1, 0)

            num_correct = sum(1 for a, b in zip(pred, label) if a[0] == b[0])
            num_samples = pred.shape[0]
            accuracy = num_correct/num_samples

            print(
                f'Got {num_correct} / {num_samples} with accuracy {float(num_correct)/float(num_samples)*100:.2f}')

    return model


# testing orginially after custom dataset
# tokenizer = transformers.BertTokenizer.from_pretrained("bert-base-uncased")
# dataset = BertDataset(tokenizer, max_length=100,
#                       data_path='https://raw.githubusercontent.com/clairett/pytorch-sentiment-classification/master/data/SST2/train.tsv')
# dataloader = DataLoader(dataset=dataset, batch_size=32)


# testing orginially bert
# model = BERT(num_classes=1)
# loss_fn = nn.BCEWithLogitsLoss()
# optimizer = optim.Adam(model.parameters(), lr=0.0001)
# model=finetune(5, dataloader, model, loss_fn, optimizer)


finetune_parameters = {
    'lr': 0.0001,
    'optimizer': optim.Adam,
    'loss_func': nn.BCEWithLogitsLoss(),
}


class Finetune_encoder:
    def __init__(self, model_name: str, data_path, num_classes, tokenizer=None, finetune_parameters=finetune_parameters) -> None:
        self.model_name = 'bert-base-uncased'
        self.tokenizer = tokenizer if tokenizer else AutoTokenizer.from_pretrained(
            self.model_name)
        self.dataset = BertDataset(
            self.tokenizer, max_length=100, data_path=data_path)
        self.dataloader = DataLoader(dataset=self.dataset, batch_size=32)
        self.model = BERT(num_classes=num_classes)
        self.finetune_parameters = finetune_parameters

    def finetune(self, epochs):
        self.model.train()
        for epoch in range(epochs):
            print(epoch)

            for batch, dl in enumerate(self.dataloader):
                ids = dl['ids']
                token_type_ids = dl['token_type_ids']
                mask = dl['mask']
                label = dl['target']
                label = label.unsqueeze(1)

                optimizer = self.finetune_parameters['optimizer'](
                    self.model.parameters(), lr=finetune_parameters['lr'])
                optimizer.zero_grad()

                output = self.model(
                    ids=ids,
                    mask=mask,
                    token_type_ids=token_type_ids)
                label = label.type_as(output)

                loss = self.finetune_parameters['loss_func'](output, label)
                loss.backward()

                optimizer.step()

                pred = np.where(output >= 0, 1, 0)

                num_correct = sum(1 for a, b in zip(
                    pred, label) if a[0] == b[0])
                num_samples = pred.shape[0]
                accuracy = num_correct/num_samples

                print(
                    f'Got {num_correct} / {num_samples} with accuracy {float(num_correct)/float(num_samples)*100:.2f}')

        return self.model
