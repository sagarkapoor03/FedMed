"""Final Flower API details needed for the FedMed implementation."""

from __future__ import annotations

import inspect

from flwr.compat.common import typing as fct
from flwr.compat.server.app import Strategy

print("Status members:", fct.Status.OK, fct.Status.ERROR)
print()
print("FitIns:", inspect.signature(fct.FitIns.__init__))
print("EvaluateIns:", inspect.signature(fct.EvaluateIns.__init__))
print("GetParametersIns:", inspect.signature(fct.GetParametersIns.__init__))
print()
print("Strategy.aggregate_fit:", inspect.signature(Strategy.aggregate_fit))
print("Strategy.configure_fit:", inspect.signature(Strategy.configure_fit))
print("Strategy.initialize_parameters:", inspect.signature(Strategy.initialize_parameters))
print()
print("ParametersRecord:", [x for x in dir(fct) if "Record" in x])
print()
# How does flwr serialize Parameters? Check the serde to see if raw bytes pass through.
import flwr.common.serde as serde

src = inspect.getsource(serde)
i = src.find("tensor_type")
print("serde tensor_type usage:")
for line in src.splitlines():
    if "tensor_type" in line:
        print("   ", line.strip())
