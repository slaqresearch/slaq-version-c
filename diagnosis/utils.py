"""Utility helpers for diagnosis app."""
from typing import Any

def sanitize_for_json(obj: Any) -> Any:
    """Recursively convert numpy/torch types to native Python types so objects
    are JSON-serializable for Django JSONField storage.

    Handles:
    - numpy scalars and arrays
    - torch tensors (if torch is installed)
    - dicts, lists, tuples
    - leaves Python primitives unchanged
    """
    try:
        import numpy as _np
    except Exception:
        _np = None

    try:
        import torch as _torch
    except Exception:
        _torch = None

    # None
    if obj is None:
        return None

    # numpy scalar
    if _np is not None and isinstance(obj, _np.generic):
        try:
            return obj.item()
        except Exception:
            try:
                return obj.tolist()
            except Exception:
                return str(obj)

    # torch tensor
    if _torch is not None and isinstance(obj, _torch.Tensor):
        try:
            arr = obj.detach().cpu().numpy()
            return sanitize_for_json(arr)
        except Exception:
            try:
                return float(obj.item()) if obj.numel() == 1 else [sanitize_for_json(v) for v in obj.tolist()]
            except Exception:
                return str(obj)

    # numpy array
    if _np is not None and isinstance(obj, _np.ndarray):
        try:
            return sanitize_for_json(obj.tolist())
        except Exception:
            return [sanitize_for_json(v) for v in obj]

    # dict
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}

    # list/tuple
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]

    # native Python types (bool/int/float/str)
    if isinstance(obj, (bool, int, float, str)):
        # Ensure bool is native bool, etc.
        if isinstance(obj, bool):
            return bool(obj)
        if isinstance(obj, int):
            return int(obj)
        if isinstance(obj, float):
            return float(obj)
        return obj

    # Fallback: convert to string
    try:
        return str(obj)
    except Exception:
        return None
