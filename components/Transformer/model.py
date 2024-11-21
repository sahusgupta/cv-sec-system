from transformer import Transformer
from torch import nn
import torch

class RouterTransformer(nn.Module):
    def __init__(self, transformers, config):
        super().__init__()
        self.transformers = nn.ModuleList(transformers)
        self.router = nn.Linear(config['input_config'], len(transformers))

    def forward(self, src, tgt):
        rout_weights = torch.softmax(self.router(src), dim=1)

        trans_outs = [
            transformer(src, tgt) for transformer in self.transformers
        ]

        comb_out = sum(
            output * weight.unsqueeze(-1).unsqueeze(-1) 
            for output, weight in zip(trans_outs, rout_weights.T)
        )

        return comb_out