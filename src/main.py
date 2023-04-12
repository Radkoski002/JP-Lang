def dupsko():
    return 1


def main():
    x = 1
    print(x + dupsko())
    y = 3
    print(y + dupsko())
    return x + y


if __name__ == "__main__":
    print(main())
