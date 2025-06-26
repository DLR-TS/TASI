from abc import abstractmethod

from pandas.core.indexing import _iLocIndexer, _LocIndexer


class LocatableEntity:

    @abstractmethod
    def _ensure_correct_type(self, df, key):  # pragma: no cover
        raise NotImplementedError()


class ILocator(_iLocIndexer):

    def __init__(self, obj: LocatableEntity) -> None:
        super().__init__("iloc", obj)

    def __getitem__(self, key):
        df = super().__getitem__(key)

        obj = self.obj._ensure_correct_type(df, key)

        return obj


class LocLocator(_LocIndexer):

    def __init__(self, obj: LocatableEntity) -> None:
        super().__init__("loc", obj)

    def __getitem__(self, key):
        df = super().__getitem__(key)

        try:
            # if the index consists only of timestamps, this is fine
            if df.index.nlevels != self.obj.index.nlevels:
                # if the levels do not match, try wrapping the key in a list
                try:
                    df = super().__getitem__([key])
                except Exception as err:
                    # this will not work for slices. Just ignore this.
                    print(err)
                    pass
            return self.obj._ensure_correct_type(df, key)
        except AttributeError:
            # if the result is no pandas object anymore. This occurs if the user selects specific table cell using any
            # of the indexers (loc, iloc) or especially when using iat or at.
            return df
