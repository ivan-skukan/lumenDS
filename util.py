# Check if cuda works with torch
import torch


def torch_init():
    if torch.cuda.is_available():
        torch.set_default_tensor_type(torch.cuda.FloatTensor)
    print(f"Is cuda available: {torch.cuda.is_available()}")
    print(f"Current device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    x = torch.Tensor([1.0])
    print(f"Default device for tensors is : {x.device}")
