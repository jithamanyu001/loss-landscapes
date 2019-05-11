"""
Basic linear algebra operations as defined on lists of numpy arrays.

We can think of these list as a single vectors consisting of all the individual
parameter values. The functions in this module implement basic linear algebra
operations on such lists.

The operations defined in the module follow the PyTorch convention of appending
the '__' suffix to the name of in-place operations.
"""

import math
import torch
import torch.nn
import numpy as np
from loss_landscapes.model_interface.model_tensor import ParameterTensor
from loss_landscapes.model_interface.torch.torch_vector import TorchParameterVector


class TorchNamedParameterTensor(ParameterTensor):
    def __init__(self, parameters: list):
        if not isinstance(parameters, list) and all(isinstance(p, torch.nn.parameter.Parameter) for p in parameters):
            raise AttributeError('Argument to ParameterVector is not a list of numpy arrays.')

        self.parameters = parameters

    def __len__(self) -> int:
        return len(self.parameters)

    def __getitem__(self, index) -> torch.nn.Parameter:
        return self.parameters[index]

    def __add__(self, other) -> 'TorchNamedParameterTensor':
        return TorchNamedParameterTensor([self[idx] + other[idx] for idx in range(len(self))])

    def __radd__(self, other) -> 'TorchNamedParameterTensor':
        return self.__add__(other)

    def add_(self, vector):
        for idx in range(len(self)):
            self.parameters[idx] += vector[idx]

    def __sub__(self, other) -> 'TorchNamedParameterTensor':
        return TorchNamedParameterTensor([self[idx] - other[idx] for idx in range(len(self))])

    def __rsub__(self, other) -> 'TorchNamedParameterTensor':
        return self.__sub__(other)

    def sub_(self, vector):
        for idx in range(len(self)):
            self.parameters[idx] -= vector[idx]

    def __mul__(self, scalar) -> 'TorchNamedParameterTensor':
        return TorchNamedParameterTensor([self[idx] * scalar for idx in range(len(self))])

    def __rmul__(self, scalar) -> 'TorchNamedParameterTensor':
        return self.__mul__(scalar)

    def mul_(self, scalar):
        for idx in range(len(self)):
            self.parameters[idx] *= scalar

    def __truediv__(self, scalar) -> 'TorchNamedParameterTensor':
        return TorchNamedParameterTensor([self[idx] / scalar for idx in range(len(self))])

    def truediv_(self, scalar):
        for idx in range(len(self)):
            self.parameters[idx] /= scalar

    def __floordiv__(self, scalar) -> 'TorchNamedParameterTensor':
        return TorchNamedParameterTensor([self[idx] // scalar for idx in range(len(self))])

    def floordiv_(self, scalar):
        for idx in range(len(self)):
            self.parameters[idx] //= scalar

    def __matmul__(self, other) -> 'TorchNamedParameterTensor':
        raise NotImplementedError()

    def model_normalize_(self, order=2):
        norm = self._model_norm(order)
        for parameter in self.parameters:
            parameter /= norm

    def layer_normalize_(self, order=2):
        layer_norms = self._layer_norms(order)
        # in-place normalize each parameter
        for layer_idx, parameter in enumerate(self.parameters, 0):
            parameter /= layer_norms[layer_idx]

    def filter_normalize_(self, order=2):
        raise NotImplementedError()

    def _model_norm(self, order=2) -> float:
        n = 0.0
        for parameter in self.parameters:
            n += torch.pow(parameter, order).sum().item()
        return math.pow(n, 1.0 / order)

    def _layer_norms(self, order=2) -> list:
        # use pytorch to compute each layer tensor's norm
        return [torch.norm(parameter, p=('fro' if order == 2 else order)).item() for parameter in self.parameters]

    def _filter_norms(self, order=2) -> list:
        # todo once figured out how to isolate filters
        raise NotImplementedError()

    def as_numpy_list(self) -> list:
        # list of numpy arrays
        return [p.clone().detach().numpy() for p in self.parameters]

    def as_vector(self) -> TorchParameterVector:
        # todo once figured out if vector view is useful
        raise NotImplementedError()

    def _get_parameters(self) -> list:
        return self.parameters


def rand_u_like(example_vector) -> TorchNamedParameterTensor:
    new_vector = []

    for param in example_vector:
        new_vector.append(np.random.uniform(size=np.size(param)))

    return TorchNamedParameterTensor(new_vector)
