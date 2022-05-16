from collections import UserDict

isa = isinstance


class Entity(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if not isa(key, str):
            raise TypeError(f"{key} is not a string")
        self.data[key] = value

    def __getitem__(self, key):
        if not isa(key, str):
            raise TypeError(f"{key} is not a string")
        elif key not in self.data:
            raise ValueError(f"{key} has not been set")
        else:
            raw = self.data[key]
            if "conditions" in self.data:
                for each in self.data["conditions"]:
                    if each["target"] == key:
                        raw = each["effect"](raw)
            return raw

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self.data[k] = v

    def get_unmodified(self, key):
        """Get value of a key without taking 'conditions' into account."""
        return self.data[key]


def main():
    def spelly(x):
        return x + 2

    def swordy(x):
        return x + 1

    joe = Entity(
        strength=10,
        conditions=[
            {
                "name": "strength buff",
                "source": "spell (Ox Strength)",
                "target": "strength",
                "effect": spelly,
            },
            {
                "name": "strength buff",
                "source": "magic sword",
                "target": "strength",
                "effect": swordy,
            },
        ],
    )
    print(joe)
    print("strength with no conditions:", joe.get_unmodified("strength"))
    print("strength with conditions applied:", joe["strength"])


if __name__ == "__main__":
    main()
