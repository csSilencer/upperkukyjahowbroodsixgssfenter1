import ccxt, logging, argparse, time
# from triangular_arb_bot import TriangularArbBot

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

def arbitrage(cycle_num=3, cycle_time=10):
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
            # Find 'closed loop' of currency rate pairs
            for loop in closed_loops:
                logger.info(f"Closed loop: {loop}")
                list_exch_rate_list = []
                i=0
                exch_rate_list = []
                buy_cycle = ['asks', 'bids', 'asks']
                sell_cycle = ['bids', 'asks', 'bids']
                for sym in loop:
                    logger.debug(sym)
                    if sym in symbols:
                        depth = exchange_obj.fetch_order_book(symbol=sym)
                        # if i % 2 == 0:
                        #     exch_rate_list.append(depth['asks'][0][0] * 1.0025)
                        # else:
                        #     exch_rate_list.append(depth['bids'][0][0] * 1.0025)
                        # i+=1
                        exch_rate_list.append(depth[buy_cycle[i]][0][0] * (1 + 0.0025))
                        i+=1
                    else:
                        exch_rate_list.append(0)

                exch_rate_list.append(time.time())      #change to Human Readable time
                logger.debug(exch_rate_list)

                #Compare to determine if Arbitrage opp exists
                lhs = exch_rate_list[0]
                rhs = exch_rate_list[1]/exch_rate_list[2]
                if lhs < rhs:  #  Cycle exists
                    # ETH/BTC < (ETH/USD / BTC/USD) === ETH/BTC < (ETH / BTC)
                    logger.info(f"Arbitrage Possibility: {loop[0]}: {lhs} < {loop[1]} / {loop[2]}: {rhs}")
                    logger.info(f"{loop[1].split('/')[1]} --> {loop[0].split('/')[1]} --> {loop[0].split('/')[0]}")
                    logger.info(f"Spread: {rhs/lhs}")
                else:
                    logger.info(f"Arbitrage Possibility: {loop[0]}: {lhs} < {loop[1]} / {loop[2]}: {rhs}")
                    logger.info(f"{loop[1].split('/')[1]} --> {loop[0].split('/')[1]} --> {loop[0].split('/')[0]}")
                    logger.info(f"Spread: {rhs/lhs}")

                #Format data (list) into List format (list of lists)
                list_exch_rate_list.append(exch_rate_list)
                logger.debug(list_exch_rate_list)
                #Create list from Lists for matplotlib format
                rateA = []      #Original Exchange Rate
                rateB = []      #Calculated/Arbitrage Exchange Rate
                rateB_fee = []  #Include Transaction Fee
                price1 = []     #List for Price of Token (Trade) 1
                price2 = []     #List for price of Token (Trade) 2
                time_list = []  #time of data collection
                #profit = []     #Record % profit
                for rate in list_exch_rate_list:
                    rateA.append(rate[0])
                    rateB.append(rate[1]/rate[2])
                    rateB_fee.append((rate[1]/rate[2])*(1-fee_percentage)*(1-fee_percentage))
                    price1.append(rate[1])
                    price2.append(rate[2])
                    #profit.append((rateB[-1]-rateA[-1])/rateA[-1])
                    time_list.append(rate[3])
                logger.debug(f"Rate A: {rateA} \n Rate B: {rateB} \n Rate C: {rateB_fee} \n")

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
    starting_funds = 10000
    symbol = 'BTC/USD'
    total_amount_bought = market_buy(starting_funds, exchange, symbol)

    logger.info(f"Starting funds: {starting_funds} {symbol.split('/')[1]}")
    logger.info(f"Total amount bought: {total_amount_bought} {symbol.split('/')[0]}")

def get_closed_loops(symbols):
    # Find secondary currencies
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
    args = get_command_line_options()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # bittrex = ccxt.bittrex()
    # run_market_buy(bittrex)
    # get_closed_loops(bittrex)
    arbitrage()

if __name__ == '__main__':
    run()
