from main import second_price_auction, reverse_auction


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


def test_reverse_price_auction_1():
    bids = [10, 9, 8, 1]
    quality_scores = [1, 1, 1, 1]
    winner, price = reverse_auction(bids, quality_scores, 10)

    assert winner == 3
    assert price == 8


def test_reverse_price_auction_2():
    bids = [10, 9, 8, 0]
    quality_scores = [1, 1, 1, 1]
    winner, price = reverse_auction(bids, quality_scores, 10)

    assert winner == 2
    assert price == 9


def test_reverse_price_auction_3():
    bids = [10, 10]
    quality_scores = [0.5, 1.5]
    winner, price = reverse_auction(bids, quality_scores, 100)

    assert winner == 1
    assert price == 30


def test_reverse_price_auction_4():
    bids = [10, 0]
    quality_scores = [1.5, 0.5, 0.5, 0.5]
    winner, price = reverse_auction(bids, quality_scores, 20)

    assert winner == 0
    assert price == 60
