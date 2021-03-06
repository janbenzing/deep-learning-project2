import torch

def tanh(x):
    return x.tanh()

def dtanh(x):
    return 4 * (x.exp() + x.mul(-1).exp()).pow(-2)

def relu(x):
    return torch.max(x, torch.zeros(x.size()))

def drelu(x):
    ones = torch.ones(x.shape)
    zeros = torch.zeros(x.shape)
    return torch.where((x > 0), ones, zeros)

def loss(v, t):
    n = t.shape[0]
    return (v - t).pow(2).sum() / n

def dloss(v, t):
    return 2 * (v - t)

def linear(input, weights, bias=None):
    """Applies a linear transformation to incoming data"""
    if bias is not None:
        return torch.addmm(bias, input, weights.t())
    else:
        return torch.mm(input, weights.t())