from main import second_price_auction


def test_second_price_auction_1():
    bids = [10, 9, 0, 0, 0, 0, 8]
    winner, price = second_price_auction(bids)

    assert winner == 0
    assert price == 9


def test_second_price_auction_2():
    bids = [10, 9, 0, 0, 0, 0, 9]
    winner, price = second_price_auction(bids)

    assert winner == 0
    assert price == 9


def test_second_price_auction_3():
    bids = [0, 1, 0, 0, 0, 0, 0]
    winner, price = second_price_auction(bids)

    assert winner == 1
    assert price == 0


def test_second_price_auction_4():
    bids = [0, 0, 0, 0, 0, 0, 0]
    _, price = second_price_auction(bids)

    assert price == 0
