import ccxt, logging, argparse, time, multiprocessing
from arb_logging_config import LOGGING

logging.config.dictConfig(LOGGING)
# from triangular_arb_bot import TriangularArbBot
FEE = 0.0025

ARBITRAGE_POSSIBILITIES = {}

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
    parser.add_argument('-f', '--fee_flag',
                        help='Turn the fee calculation on or off',
                        required=False,
                        default=True)
    parser.add_argument('-w', '--num_workers',
                        help='Number of python workers to monitor opps',
                        required=False,
                        default=20)
    return parser.parse_args()

def arbitrage(max_macro_workers, cycle_num=3, cycle_time=10, fee_flag=True):
    logger=logging.getLogger("main")
    logger.debug("Arbitrage Function Running")
    fee_percentage = 0.001          #divided by 100
    coins = ['BTC', 'LTC', 'ETH']   #Coins to Arbitrage
    exchange_list = ['bittrex']
    for exch in exchange_list:    #initialize Exchange
        exchange_obj = getattr (ccxt, exch) ()
        if exch not in exchange_list:
            continue
        logger.info(f"Loading markets for exchange: {exchange_obj}")
        exchange_obj.load_markets()
        symbols = exchange_obj.symbols
        logger.debug(exchange_obj.symbols)
        if symbols is None:
            logger.info(f"Skipping Exchange {exch}")
            logger.info("\n-----------------\nNext Exchange\n-----------------")
        elif len(symbols)<15:
            logger.debug("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
        else:
            logger.debug(exchange_obj)
            logger.info(f"------------Exchange: {exchange_obj.id}")
            closed_loops = get_closed_loops(symbols)
            initialise_arb_opportunities_dict(closed_loops)
            num_processes = max(max_macro_workers, 20)
            worker_max_loop_size=int(len(closed_loops) / num_processes)
            logger.info(f"Optimal worker loop size is {worker_max_loop_size}" \
                          f" for {len(closed_loops)} " \
                          f"closed_loops with {num_processes} processes")
            pool = multiprocessing.Pool(processes=num_processes+1)
            closed_loops_groups = [closed_loops[x:x+worker_max_loop_size] for x in range(0, len(closed_loops), worker_max_loop_size)]
            logger.info(f"Num closed loops {len(closed_loops_groups)}")
            logger.info(f"closed loop groups {closed_loops_groups}")
            for closed_loops_subset in closed_loops_groups:
                logger.info(f"Kicking off closed loops subset {closed_loops_subset}")
                pool.apply_async(subset_arb_monitor, args=(closed_loops_subset.copy(), exch))

            pool.close()
            pool.join()


def subset_arb_monitor(closed_loops, exch, cycle_num=3, cycle_time=10, fee_flag=True):
    """
    Monitor a smaller subset of closed loops for lower refresh rate
    :param closed_loops:
    :param cycle_num:
    :param cycle_time:
    :param fee_flag:
    :return:
    """
    logger = logging.getLogger("macro_arb_logger")
    logger.info(f"Process starting with closed loops subset {closed_loops}")
    exchange_obj = getattr (ccxt, exch) ()

    while True:
        for loop in closed_loops:
            order_books = []
            for sym in loop:
                order_books.append(exchange_obj.fetch_order_book(symbol=sym))
            calculate_buy_cycle(order_books, loop, fee_flag=fee_flag)
            # calculate_sell_cycle(order_books, loop, fee_flag=fee_flag)


def initialise_arb_opportunities_dict(closed_loops):
    """
        key is loop string with no spaces
        value is whether or not the loop is currently profitable
    """
    for loop in closed_loops:
        key = ", ".join(loop)
        ARBITRAGE_POSSIBILITIES[key] = False

def calculate_buy_cycle(order_books, loop, fee_flag=True):
    logger = logging.getLogger("micro_arb_logger")

    logger.info("")

    logger.info(f"Buy cycle on closed loop: {loop} fee: {fee_flag}")

    if fee_flag:
        fee_bid = 1-0.0025
        fee_ask = 1+0.0025
    else:
        fee_bid = 1
        fee_ask = 1

    # Get prices
    a_ask = order_books[0]['asks'][0][0] * fee_ask
    b_bid = order_books[1]['bids'][0][0] * fee_bid
    b_ask = order_books[1]['asks'][0][0] * fee_ask
    c_ask = order_books[2]['asks'][0][0] * fee_ask

    # Get volume
    a_vol = order_books[0]['asks'][0][1]
    b_vol = order_books[1]['bids'][0][1]
    c_vol = order_books[2]['asks'][0][1]
    logger.info("In primary currency")
    logger.info(f"a_vol: {a_vol}, b_vol: {b_vol}, c_vol: {c_vol}")

    # ['A/B', 'A/X', 'B/X']

    # Buy cycle
    # loop = [ETH/BTC, ETH/USD, BTC/USD]
    # a_vol = 5ETH  --> 5* order_books[1]['asks'][0][0]
    # b_vol = 1BTC  --> 1* order_books[2]['bids'][0][0]
    # c_vol = 5ETH  --> 5* order_books[1]['asks'][0][0]

    a_vol_in_sec = a_vol * b_ask
    b_vol_in_sec = b_vol * b_bid
    c_vol_in_sec = c_vol * c_ask
    logger.info(f"In terms of {loop[1].split('/')[1]}")
    logger.info(f"a_vol: {a_vol_in_sec}, b_vol: {b_vol_in_sec}, c_vol: {c_vol_in_sec}")
    logger.info(f"Minimum volume: {min(a_vol_in_sec, b_vol_in_sec, c_vol_in_sec)} {loop[1].split('/')[1]}")
    # Need to get volumes in the secondary currency

    # Compare to determine if Arbitrage opp exists
    # eg.
    # a = ETH/BTC, b = ETH/USD, c = BTC/USD
    #   ETH/BTC < (ETH/USD / BTC/USD)
    # = ETH/BTC < (ETH / BTC)
    lhs = a_ask
    rhs = b_bid / c_ask
    if lhs < rhs:  #  Cycle exists
        logger.info(f"Arbitrage Possibility: {loop[0]}: {lhs} < {loop[1]} / {loop[2]}: {rhs}")
        logger.info(f"{loop[1].split('/')[1]} --> {loop[0].split('/')[1]} --> {loop[0].split('/')[0]}")
        logger.info(f"Spread: {rhs/lhs}")
        if ARBITRAGE_POSSIBILITIES[", ".join(loop)] == False:
            ARBITRAGE_POSSIBILITIES[", ".join(loop)] = True
    else:
        logger.info(f"No Arbitrage possibility on {loop[1].split('/')[1]} --> {loop[0].split('/')[1]} --> {loop[0].split('/')[0]}")

def calculate_sell_cycle(order_books, loop, fee_flag=True):
    logger = logging.getLogger("micro_arb_logger")
    logger.info(f"Sell cycle on closed loop: {loop} fee: {fee_flag}")

    if fee_flag:
        fee_bid = 1-0.0025
        fee_ask = 1+0.0025
    else:
        fee_bid = 1
        fee_ask = 1

    a = order_books[0]['bids'][0][0] * fee_bid
    b = order_books[1]['asks'][0][0] * fee_ask
    c = order_books[2]['bids'][0][0] * fee_bid

    # Get volume
    a_vol = order_books[0]['bids'][0][1]
    b_vol = order_books[1]['asks'][0][1]
    c_vol = order_books[2]['bids'][0][1]

    # Compare to determine if Arbitrage opp exists
    # eg.
    # a = ETH/BTC, b = ETH/USD, c = BTC/USD
    #   ETH/BTC > (ETH/USD / BTC/USD)
    # = ETH/BTC > (ETH / BTC)
    lhs = a
    rhs = b / c
    if lhs > rhs:  #  Cycle exists
        logger.info(f"Arbitrage Possibility: {loop[0]}: {lhs} > {loop[1]} / {loop[2]}: {rhs}")
        logger.info(f"{loop[1].split('/')[1]} --> {loop[0].split('/')[0]} --> {loop[0].split('/')[1]}")
        logger.info(f"Spread: {lhs/rhs}")
        logger.info(f"Minimum volume: {min(a_vol, b_vol, c_vol)}")
    else:
        logger.info(f"No Arbitrage possibility on {loop[1].split('/')[1]} --> {loop[0].split('/')[0]} --> {loop[0].split('/')[1]}")

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
            pair_a = sym.split('/')[0] + '/' + sec
            pair_b = sym.split('/')[1] + '/' + sec
            if pair_a in symbols and pair_a != sym and pair_b in symbols and pair_b != sym:
                logger.debug("Triangular market found!")
                logger.debug(sym)
                logger.debug(pair_a)
                logger.debug(pair_b)
                logger.debug("============")
                market_loops.append([sym, pair_a, pair_b])

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
