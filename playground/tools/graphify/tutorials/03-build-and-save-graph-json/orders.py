def place_order(item):
    validate(item)
    return charge(item)


def validate(item):
    return item is not None
