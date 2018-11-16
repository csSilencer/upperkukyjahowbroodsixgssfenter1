import ccxt, logging, argparse
from triangular_arb_bot import TriangularArbBot

logging.basicConfig(format='%(asctime)s: %(processName)s: %(message)s')
logger = logging.getLogger('upperkuk')
logger.setLevel(logging.INFO)
FEE = 0.0025

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
    return parser.parse_args()

def market_buy(starting_amount, exchange, symbol):
    """
    Calculates how much of a coin you can buy with a given starting amount
    """
    asks = exchange.fetch_order_book(symbol)['asks']
    funds = starting_amount
    total_amount_bought = 0

    for ask in asks:
        price, volume = ask
        order_total = price * volume
        total_fee = order_total * FEE
        order_total_inc_fee = order_total + total_fee
        logger.debug("============")
        logger.debug("Funds: {funds}")
        logger.debug("Price: {price}")
        logger.debug("Volume: {volume}")
        logger.debug("Order total: {order_total}")
        logger.debug("Fee: {total_fee}")
        logger.debug("Order total (inc fee): {order_total_inc_fee}")

        if order_total_inc_fee < funds:
            amount_bought = volume
            logger.debug("Amount bought on this order: {amount_bought}")
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
        logger.debug("Remaining funds: {funds} {symbol.split('/')[1]}")
        logger.debug("Total amount bought: {total_amount_bought} {symbol.split('/')[0]}")
        logger.debug("")

        if funds == 0:
            return total_amount_bought


def run_market_buy(exchange):
    starting_funds = 10000
    symbol = 'BTC/USD'
    total_amount_bought = market_buy(starting_funds, exchange, symbol)

    logger.info("Starting funds: {starting_funds} {symbol.split('/')[1]}")
    logger.info("Total amount bought: {total_amount_bought} {symbol.split('/')[0]}")


def get_closed_loops(exchange):
    exchange.load_markets()
    symbols = exchange.symbols

    # Find secondary currencies
    secondary_currencies = []
    for sym in symbols:
        if sym.split('/')[1] not in secondary_currencies:
            secondary_currencies.append(sym.split('/')[1])

    logger.info("Secondary currencies:")
    for sec in secondary_currencies:
        logger.info(sec)

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
        logger.info(loop)


def run():
    """
    Do the thing
    """
    args = get_command_line_options()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    bittrex = ccxt.bittrex()
    # run_market_buy(bittrex)
    get_closed_loops(bittrex)


if __name__ == '__main__':
    run()
