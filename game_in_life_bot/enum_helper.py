import enum


class StringFLagEnum(enum.Flag):
    def __eq__(self, other):
        if isinstance(other, str):
            other = getattr(self, other.upper())
        return super().__eq__(other)

    def __contains__(self, item):
        if isinstance(item, str):
            item = getattr(self, item.upper())
        return super().__contains__(item)
