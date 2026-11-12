from order_service import create_order


def run():
    return create_order(100.0, 0.10)


if __name__ == "__main__":
    print(run())