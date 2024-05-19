import re


class RegexDict(dict):
    """
    custom dict to allow regex based keys.
    """
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)

        for pattern in self.keys():
            if re.match(pattern, key):
                return super().__getitem__(pattern)
        raise KeyError(f"No key matching regex found for {key}")


