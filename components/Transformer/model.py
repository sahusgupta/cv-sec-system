from transformer import Transformer
from torch import nn
import torch
from torch import optim
class RouterTransformer(nn.Module):
    def __init__(self, transformers, config):
        super(RouterTransformer, self).__init__()
        self.transformers = nn.ModuleList(transformers)
        self.router = nn.Linear(config['input_config'], len(transformers))

    def forward(self, src, tgt):
        global_context = src.mean(dim=1)  # Shape: (batch_size, d_model).
        rout_weights = torch.softmax(self.router(global_context), dim=-1)  # Shape: (batch_size, num_transformers).
        trans_outs = torch.stack([transformer(src, tgt) for transformer in self.transformers], dim=1) # Collect outputs from each transformer (batch_size, num_transformers, seq_len, d_model).
        rout_weights = rout_weights.unsqueeze(-1).unsqueeze(-1) # Reshape routing weights to (batch_size, num_transformers, 1, 1).
        comb_out = (trans_outs * rout_weights).sum(dim=1) # Weighted combination: (batch_size, seq_len, d_model) after summing over transformers.

        return comb_out
    
    def back(self, src, tgt, tgt_labels, loss_fn, optimizer):
        optimizer.zero_grad()  # Clear previous gradients.

        # Forward pass.
        outputs = self.forward(src, tgt)

        # Reshape for loss calculation (batch_size * seq_len, vocab_size).
        outputs = outputs.view(-1, outputs.size(-1))
        tgt_labels = tgt_labels.view(-1)

        # Compute loss.
        loss = loss_fn(outputs, tgt_labels)
        loss.backward()  # Backpropagation.
        optimizer.step()  # Update weights.

        return loss.item()
    
if __name__ == "__main__":
    # Configuration.
    src_vocab_size = 5000
    tgt_vocab_size = 5000
    d_model = 512
    num_heads = 8
    num_layers = 6
    d_ff = 2048
    max_seq_length = 100
    dropout = 0.1

    # Instantiate 3 Transformer models.
    transformers = [
        Transformer(src_vocab_size, tgt_vocab_size, d_model, num_heads, num_layers, d_ff, max_seq_length, dropout)
        for _ in range(3)
    ]

    # Instantiate RouterTransformer.
    router_transformer = RouterTransformer(transformers, d_model)

    # Dummy input data.
    src_data = torch.randint(1, src_vocab_size, (64, max_seq_length))  # (batch_size, seq_length).
    tgt_data = torch.randint(1, tgt_vocab_size, (64, max_seq_length))  # (batch_size, seq_length).
    tgt_labels = torch.randint(1, tgt_vocab_size, (64, max_seq_length))  # Ground truth labels.

    # Define loss function and optimizer.
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # Assuming padding index is 0.
    optimizer = optim.Adam(router_transformer.parameters(), lr=0.0001)

    # Training loop.
    for epoch in range(10):  # Example of 10 epochs.
        loss = router_transformer.backpropagate(src_data, tgt_data[:, :-1], tgt_labels[:, 1:], criterion, optimizer)
        print(f"Epoch {epoch + 1}, Loss: {loss:.4f}")