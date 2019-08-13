def foo(bar=False, options={}):
    options = dict({
        'configure_timeout': 15,
        'rename': True
    }, **(options or {}))

    for key in options.keys():
        print(options[key])
    print("bar is {0}".format(bar))


if __name__ == "__main__":
    foo(options={"bar": True})
