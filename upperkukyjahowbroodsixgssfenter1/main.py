import ccxt
import logging
import argparse
import time
import multiprocessing
from arb_logging_config import LOGGING

logging.config.dictConfig(LOGGING)
FEE = 0.0025
FEE_BID = 1-FEE
FEE_ASK = 1+FEE

MIN_VOLUMES = {
    "USD": 10,
    "USDT": 10,
    "ETH": 0.05,
    "BTC": 0.002
}

ARBITRAGE_POSSIBILITIES = {}


class Pair():
    def __init__(self, pair):
        self.primary = pair.split('/')[0]
        self.secondary = pair.split('/')[1]
        self.value = pair

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


def get_command_line_options():
    """
    Return the command line parameters required by the offboarding script
    :return: parser
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description='upperkukyjahowbroodsixgssfenter1')

    parser.add_argument('-d', '--debug',
                        help='Set the logging level to debug',
                        required=False,
                        default=False)
    parser.add_argument('-w', '--num_workers',
                        help='Number of python workers to monitor opps',
                        required=False,
                        default=20)
    return parser.parse_args()


def arbitrage(max_macro_workers, cycle_num=3, cycle_time=10):
    logger = logging.getLogger("main")
    logger.debug("Arbitrage Function Running")
    coins = ['BTC', 'LTC', 'ETH']  # Coins to Arbitrage
    exchange_list = ['bittrex']
    for exch in exchange_list:  # initialize Exchange
        exchange_obj = getattr(ccxt, exch)()
        if exch not in exchange_list:
            continue
        logger.info(f"Loading markets for exchange: {exchange_obj}")
        exchange_obj.load_markets()
        symbols = exchange_obj.symbols
        logger.debug(exchange_obj.symbols)
        if symbols is None:
            logger.info(f"Skipping Exchange {exch}")
            logger.info("\n-----------------\nNext Exchange\n-----------------")
        elif len(symbols) < 15:
            logger.debug("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
        else:
            logger.debug(exchange_obj)
            logger.info(f"------------Exchange: {exchange_obj.id}")
            closed_loops = get_closed_loops(symbols)
            # initialise_arb_opportunities_dict(closed_loops)
            subset_arb_monitor(closed_loops, exch)


def subset_arb_monitor(closed_loops, exch, cycle_num=3, cycle_time=10):
    """
    Monitor a smaller subset of closed loops for lower refresh rate
    :param closed_loops:
    :param cycle_num:
    :param cycle_time:
    :return:
    """
    logger = logging.getLogger("macro_arb_logger")
    logger.info(f"Process starting with closed loops subset {closed_loops}")
    exchange_obj = getattr(ccxt, exch)()

    while True:
        for closed_loop in closed_loops:
            order_books = []
            for sym in closed_loop:
                order_books.append(exchange_obj.fetch_order_book(symbol=str(sym)))
                # time.sleep(0.9)
            calculate_buy_cycle(order_books, closed_loop)
            calculate_sell_cycle(order_books, closed_loop)


def initialise_arb_opportunities_dict(closed_loops):
    """
        key is loop string with no spaces
        value is whether or not the loop is currently profitable
    """
    for loop in closed_loops:
        key = ", ".join(loop)
        ARBITRAGE_POSSIBILITIES[key] = False


def calculate_buy_cycle(order_books, loop):
    """
    """
    logger = logging.getLogger("micro_arb_logger")

    logger.debug("")
    logger.debug(f"Buy cycle on closed loop: {loop}")

    x_currency = loop[1].secondary

    order_book_list = [
        order_books[0]['asks'],
        order_books[1]['bids'],
        order_books[2]['asks']
    ]

    fee_cycle_list = [
        FEE_ASK,
        FEE_BID,
        FEE_ASK
    ]

    # Used to calculate volumes in terms of base currency
    vol_to_x_price_list = [
        order_books[1]['asks'][0][0] * FEE_ASK,
        order_books[1]['bids'][0][0] * FEE_BID,
        order_books[2]['asks'][0][0] * FEE_ASK
    ]

    avg_prices = []
    for i in range(3):
        total_vol = 0
        total_vol_in_x = 0
        total_order_cost = 0

        for order in order_book_list[i]:  # 100 returned in the call
            price = order[0] * fee_cycle_list[i]
            vol = order[1]
            order_cost = price * vol  # Total cost of order

            # To calculate average price of multiple orders
            total_vol += vol  # Volume
            total_order_cost += order_cost  # Keep running total order cost
            total_vol_in_x += vol * vol_to_x_price_list[i]  # Keep running total of volume in terms of X currency

            # If total volume (in X) reached, calculate average cost and return
            if total_vol_in_x >= MIN_VOLUMES[x_currency]:
                logger.debug(f"Vol of {loop[i]}: {total_vol_in_x} {x_currency}")
                avg_price = total_order_cost / total_vol
                logger.debug(f"Average Price: {avg_price}")
                avg_prices.append(avg_price)
                break

    logger.debug("=== Calculations")

    lhs = avg_prices[0]
    rhs = avg_prices[1] / avg_prices[2]
    if lhs < rhs:  # Cycle exists
        logger.info(f"Arbitrage Possibility: {loop[0]} ({lhs}) < {loop[1]} / {loop[2]} ({rhs})")
        logger.info(f"{loop[1].secondary} --> {loop[0].secondary} --> {loop[0].primary}")
        logger.info(f"Spread: {rhs/lhs}")
        logger.info(f"Minimum volume: {min(a_vol, b_vol, c_vol)} {loop[1].secondary}")
        if ARBITRAGE_POSSIBILITIES[", ".join(loop)] is False:
            ARBITRAGE_POSSIBILITIES[", ".join(loop)] = True
    else:
        logger.info(f"No Arbitrage possibility on {loop[1].secondary} --> {loop[0].secondary} --> {loop[0].primary}")


def calculate_sell_cycle(order_books, loop):
    logger = logging.getLogger("micro_arb_logger")

    logger.debug("")
    logger.debug(f"Sell cycle on closed loop: {loop}")

    x_currency = loop[1].secondary

    order_book_list = [
        order_books[0]['bids'],
        order_books[1]['asks'],
        order_books[2]['bids']
    ]

    fee_cycle_list = [
        FEE_BID,
        FEE_ASK,
        FEE_BID
    ]

    # Used to calculate volumes in terms of base currency
    vol_to_x_price_list = [
        order_books[1]['bids'][0][0] * FEE_BID,
        order_books[1]['asks'][0][0] * FEE_ASK,
        order_books[2]['bids'][0][0] * FEE_BID
    ]

    avg_prices = []
    for i in range(3):
        total_vol = 0
        total_vol_in_x = 0
        total_order_cost = 0

        for order in order_book_list[i]:  # 100 returned in the call
            price = order[0] * fee_cycle_list[i]
            vol = order[1]
            order_cost = price * vol  # Total cost of order

            # To calculate average price of multiple orders
            total_vol += vol  # Volume
            total_order_cost += order_cost  # Keep running total order cost
            total_vol_in_x += vol * vol_to_x_price_list[i]  # Keep running total of volume in terms of X currency

            # If total volume (in X) reached, calculate average cost and return
            if total_vol_in_x >= MIN_VOLUMES[x_currency]:
                logger.debug(f"Vol of {loop[i]}: {total_vol_in_x} {x_currency}")
                avg_price = total_order_cost / total_vol
                logger.debug(f"Average Price: {avg_price}")
                avg_prices.append(avg_price)
                break

    logger.debug("=== Calculations")

    lhs = avg_prices[0]
    rhs = avg_prices[1] / avg_prices[2]
    if lhs > rhs:  # Cycle exists
        logger.info(f"Arbitrage Possibility: {loop[0]} ({lhs}) > {loop[1]} / {loop[2]} ({rhs})")
        logger.info(f"{loop[1].secondary} --> {loop[0].primary} --> {loop[0].secondary}")
        logger.info(f"Spread: {rhs/lhs}")
        logger.info(f"Minimum volume: {min(a_vol, b_vol, c_vol)} {loop[1].secondary}")
        if ARBITRAGE_POSSIBILITIES[", ".join(loop)] is False:
            ARBITRAGE_POSSIBILITIES[", ".join(loop)] = True
    else:
        logger.info(f"No Arbitrage possibility on {loop[1].secondary} --> {loop[0].primary} --> {loop[0].secondary}")


def market_buy(starting_amount, exchange, symbol):
    """
    Calculates how much of a coin you can buy with a given starting amount
    """

    logger = logging.getLogger("dev_console")

    asks = exchange.fetch_order_book(symbol)['asks']
    funds = starting_amount
    total_amount_bought = 0

    for ask in asks:
        price, volume = ask
        order_total = price * volume
        total_fee = order_total * FEE
        order_total_inc_fee = order_total + total_fee
        logger.debug("============")
        logger.debug(f"Funds: {funds}")
        logger.debug(f"Price: {price}")
        logger.debug(f"Volume: {volume}")
        logger.debug(f"Order total: {order_total}")
        logger.debug(f"Fee: {total_fee}")
        logger.debug(f"Order total (inc fee): {order_total_inc_fee}")

        if order_total_inc_fee < funds:
            amount_bought = volume
            logger.debug(f"Amount bought on this order: {amount_bought}")
            total_amount_bought += amount_bought
            funds -= order_total_inc_fee
        else:
            percentage_of_order = funds / order_total_inc_fee
            amount_bought = percentage_of_order * volume
            logger.debug("Amount bought on this order: {amount_bought}")
            total_amount_bought += amount_bought
            funds -= order_total_inc_fee * percentage_of_order
            assert funds == 0, "There seems to be a miscalculation somewhere, exiting.."

        logger.debug("")
        logger.debug(f"Remaining funds: {funds} {symbol.split('/')[1]}")
        logger.debug(f"Total amount bought: {total_amount_bought} {symbol.split('/')[0]}")
        logger.debug("")

        if funds == 0:
            return total_amount_bought


def run_market_buy(exchange):
    logger = logging.getLogger("dev_console")

    starting_funds = 10000
    symbol = 'BTC/USD'
    total_amount_bought = market_buy(starting_funds, exchange, symbol)

    logger.info(f"Starting funds: {starting_funds} {symbol.split('/')[1]}")
    logger.info(f"Total amount bought: {total_amount_bought} {symbol.split('/')[0]}")


def get_closed_loops(symbols):
    # Find secondary currencies

    logger = logging.getLogger("main")

    secondary_currencies = []
    for sym in symbols:
        if sym.split('/')[1] not in secondary_currencies:
            secondary_currencies.append(sym.split('/')[1])

    logger.debug("Secondary currencies:")
    for sec in secondary_currencies:
        logger.debug(sec)

    # Find a valid triangular market loop
    market_loops = []
    for sym in symbols:
        for sec in secondary_currencies:
            pair_b = sym.split('/')[0] + '/' + sec
            pair_c = sym.split('/')[1] + '/' + sec
            if pair_b in symbols and pair_b != sym and pair_c in symbols and pair_c != sym:
                logger.debug("Triangular market found!")
                logger.debug(sym)
                logger.debug(pair_b)
                logger.debug(pair_c)
                logger.debug("============")
                market_loops.append([Pair(sym), Pair(pair_b), Pair(pair_c)])

    for loop in market_loops:
        logger.debug(loop)

    return market_loops


def run():
    """
    Do the thing
    """

    logger = logging.getLogger('main')

    cli_args = get_command_line_options()
    if cli_args.debug:
        logger.setLevel(logging.DEBUG)

    arbitrage(int(cli_args.num_workers))


if __name__ == '__main__':
    run()
