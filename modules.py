import torch
import functions
import math
import init

class Module(object):
    def forward(self, input):
        raise NotImplementedError
    def backward(self, gradswrtoutput):
        raise NotImplementedError
    def param(self):
        """Return a list of pairs, each composed of a parameter tensor,
        and a gradient tensor of same size. Typically passed to optimizer."""
        return []

class Linear(Module):
    """Applies a linear transformation to incoming data"""
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        self.weight = torch.zeros(out_features, in_features)
        self.dweight = torch.zeros(out_features, in_features)

        if bias:
            self.bias = torch.zeros(out_features)
            self.dbias = torch.zeros(out_features)
        else:
            self.bias = None
            self.dbias = None

        self.reset_parameters()

    def forward(self, input):
        self.input = input
        return functions.linear(self.input, self.weight, self.bias)

    def backward(self, gradwrtoutput):
        """Returns the loss derived with respect to the input and computes
        the derivatives of the loss with respect to the parameters"""
        self.gradwrtoutput = gradwrtoutput
        # Derivatives of loss wrt parameters
        self.dweight = gradwrtoutput.t().mm(self.input)
        self.dbias = self.gradwrtoutput.t().sum(1)
        return gradwrtoutput.mm(self.weight)

    def param(self):
        if self.bias is None and self.dbias is None:
            return [(self.weight, self.dweight)]
        else:
            return [(self.weight, self.dweight), (self.bias, self.dbias)]

    def reset_parameters(self):
        """Initialize weights using normal distribution"""
        epsilon = 1e-6
        self.weight = init.xavier_normal_(self.weight)
        if self.bias is not None:
            self.bias = self.bias.normal_(0, epsilon)

class ReLU(Module):
    def __init__(self):
        super().__init__()

    def forward(self, input):
        # s
        self.input = input
        return functions.relu(input)

    def backward(self, gradwrtoutput):
        """Returns the loss derived with respect to the output"""
        # dlds
        return gradwrtoutput * functions.drelu(self.input)

    def param(self):
        return []

class TanH(Module):
    def __init__(self, *args):
        super().__init__()

    def forward(self, input):
        self.input = input
        return functions.tanh(input)

    def backward(self, gradwrtoutput):
        """Returns the loss derived with respect to the output"""
        # dlds
        return gradwrtoutput * functions.dtanh(self.input)

    def param(self):
        return []

class Sequential(Module):
    def __init__(self, *args):
        super().__init__()
        for idx, module in enumerate(args):
            # TODO fix str(idx)
            setattr(self, module.__class__.__name__ + str(idx), module)

    def forward(self, input):
        """Apply forward pass sequentially on every module."""
        for module in self.__dict__.values():
            input = module.forward(input)
        return input

    def backward(self, gradwrtoutput):
        """Apply backward pass sequentially on every module."""
        for module in list(self.__dict__.values())[::-1]:
            gradwrtoutput = module.backward(gradwrtoutput)
        return gradwrtoutput

    def param(self):
        """Return a list of pairs, each composed of a parameter tensor,
        and a gradient tensor of same size. Typically passed to optimizer."""
        params = []
        for module in self.__dict__.values():
            params.extend(module.param())
        return params

class MSELoss(Module):
    def __init__(self):
        super().__init__()

    def forward(self, output, target):
        self.output = output
        self.target = target
        return functions.loss(output.float(), target.float())

    def backward(self, gradswrtoutput=1):
        return gradswrtoutput * functions.dloss(self.output, self.target)
