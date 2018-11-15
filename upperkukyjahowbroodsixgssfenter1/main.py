import ccxt, logging
from triangular_arb_bot import TriangularArbBot

logging.basicConfig(format='%(asctime)s: %(processName)s: %(message)s')
logger = logging.getLogger('upperkuk')
logger.setLevel(logging.DEBUG)
# logger.disabled = True
FEE = 0.0025

def market_order(starting_amount, exchange, ticker, order_type):

    # if
    btc_usd_bids = exchange.fetch_order_book(ticker)['bids']
    btc_usd_asks = exchange.fetch_order_book(ticker)['asks']

    funds = starting_amount
    total_btc_bought = 0

    for ask in btc_usd_asks:
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
            btc_bought = volume
            logger.debug(f"BTC bought on this order: {btc_bought}")
            total_btc_bought += btc_bought
            funds -= order_total_inc_fee
        else:
            percentage_of_order = funds / order_total_inc_fee
            btc_bought = percentage_of_order * volume
            logger.debug(f"BTC bought on this order: {btc_bought}")
            total_btc_bought += btc_bought
            logger.debug(f"Cost of this order: {order_total_inc_fee * percentage_of_order}")
            funds -= order_total_inc_fee * percentage_of_order

        logger.debug("")
        logger.debug(f"Remaining funds: {funds}")
        logger.debug(f"Total BTC bought: {total_btc_bought}")
        logger.debug("")

        if funds == 0:
            return total_btc_bought

def run():
    """
    Do the thing
    """
    bittrex = ccxt.bittrex()
    starting_funds = 10000
    total_btc_bought = market_order(starting_funds, bittrex, 'BTC/USD', "buy")
    logger.info(f"Starting funds: {starting_funds}")
    logger.info(f"Total BTC bought: {total_btc_bought}")


if __name__ == '__main__':
    run()
