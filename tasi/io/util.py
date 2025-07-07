import inspect
from typing import Tuple

import pandas as pd
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely import to_geojson


class FlatDict(dict):

    @classmethod
    def from_dict(
        cls,
        d: dict,
        nlevels: int | None = None,
        prefix: str | Tuple[str, ...] = tuple(),
    ):
        retval = as_flat_dict(d, nlevels=nlevels, prefix=prefix)

        return cls(retval)

    def as_dataframe(self):
        return pd.DataFrame([self], columns=self.as_index()).sort_index(axis=1)

    @property
    def depth(self) -> int:
        return max(map(lambda l: len(l) if isinstance(l, tuple) else 1, self))

    def as_index(self) -> pd.Index | pd.MultiIndex:
        if self.depth == 1:
            return pd.Index(self)
        return pd.MultiIndex.from_tuples(self)


def flatten_keys(din: dict, dout: dict, key: tuple = ()):

    for k, v in din.items():
        # prepend the previous key if available
        k_: tuple = key + (k,)

        if isinstance(v, dict):
            # run recursively to update the dict
            flatten_keys(v, dout, k_)

        elif isinstance(v, list):
            for i, v_ in enumerate(v):
                k__ = k_ + (i,)

                flatten_keys(v_, dout, k__)
        else:
            # just update the dictionary at the leaves
            dout.update({k_: v})


def as_flat_dict(
    d: dict,
    equal_length: bool = True,
    nlevels: int | None = None,
    prefix: str | Tuple[str, ...] = tuple(),
):

    d2 = {}

    if isinstance(prefix, str):
        prefix = (prefix,)

    flatten_keys(d, d2, key=prefix)

    if nlevels is not None:
        k_max = nlevels
    else:
        # ensure all keys have the same depth
        k_max = FlatDict(d2).depth

    if equal_length and k_max > 1:
        if k_max > 1:
            for k in list(d2.keys()):
                if len(k) < k_max:
                    d2[(*k, *[""] * (k_max - len(k)))] = d2.pop(k)

    if k_max == 1:
        for k in list(d2.keys()):
            d2[k[0]] = d2.pop(k)

    return d2


def get_return_type(method):
    sig = inspect.signature(method)
    if "return" in sig.return_annotation.__annotations__:
        return sig.return_annotation.__annotations__["return"]
    else:
        return None


def as_geojson(obj: WKBElement | str) -> str | None:

    if obj is None:
        # Probably unnecessary if field is not nullable
        result = None
    elif isinstance(obj, WKBElement):
        # e.g. session.get results in a `WKBElement`
        result = to_geojson(to_shape(obj))
    else:
        raise TypeError(f"Unsupported type {type(obj)}")

    return result
