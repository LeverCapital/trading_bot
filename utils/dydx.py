from dydx3 import Client
import dydx3.constants as consts
from dotenv import load_dotenv
import os
from web3 import Web3
import time


def setup_dydx():
    load_dotenv()
    # My Account 2 metamask address
    ETHEREUM_ADDRESS = '0x17C562B0E8Fa75354C1b45F4f5dD8a2b6f38d663'
    # Using Etthereum node hosted on ChainStack.
    # Exposing this key only for Sponsor verification purposes
    WEB_PROVIDER_URL = "https://nd-574-439-281.p2pify.com/80e424588b078029ae1526522a01f527"

    # TODO: Switch to socket conections to prevent request timeouts
    client = Client(
        network_id=consts.NETWORK_ID_ROPSTEN,
        host=consts.API_HOST_ROPSTEN,
        default_ethereum_address=ETHEREUM_ADDRESS,
        web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
        eth_private_key=os.getenv('ETH_PRIVATE_KEY')
    )

    # Set STARK key.
    stark_private_key = client.onboarding.derive_stark_key()
    client.stark_private_key = stark_private_key

    return client


def go_long(client, amount, stop_loss, roi):
    # Get our position ID.
    account_response = client.private.get_account()
    position_id = account_response.data['account']['positionId']

    eth_market = client.public.get_markets(market=consts.MARKET_ETH_USD)
    buy_price = eth_market.data['markets']['ETH-USD']['oraclePrice']

    # Make a market buy order
    order_params = {
        'position_id': position_id,
        'market': consts.MARKET_ETH_USD,
        'side': consts.ORDER_SIDE_BUY,
        'order_type': consts.ORDER_TYPE_MARKET,
        'post_only': False,
        'size': str(amount),
        'price': '%.1f' % float(buy_price),  # Set prceision to tick_size 0.1
        'limit_fee': '0.0015',
        'expiration_epoch_seconds': time.time() + 15000,
        'time_in_force': consts.TIME_IN_FORCE_IOC
    }
    market_buy_order = client.private.create_order(**order_params).data
    print(market_buy_order)

    buy_price = market_buy_order['order']['price']

    # Also make a stop loss order
    stop_limit_price = '%.1f' % (float(buy_price) * (1 - (stop_loss/100)))
    stoploss_order = client.private.create_order(
        position_id=position_id,
        market=consts.MARKET_ETH_USD,
        side=consts.ORDER_SIDE_SELL,
        order_type=consts.ORDER_TYPE_STOP,
        post_only=False,
        size=str(amount),
        price=stop_limit_price,
        trigger_price=stop_limit_price,
        limit_fee='0.015',
        expiration_epoch_seconds=time.time() + 15000,
    ).data
    print(stoploss_order)

    take_profit_price = '%.1f' % (float(buy_price) * (1 + (roi/100)))
    trigger_profit_price = '%.1f' % (float(buy_price) * (1 + (roi/200)))
    # Also make a take-profit order
    take_profit_order = client.private.create_order(
        position_id=position_id,
        market=consts.MARKET_ETH_USD,
        side=consts.ORDER_SIDE_SELL,
        order_type=consts.ORDER_TYPE_TAKE_PROFIT,
        post_only=False,
        size=str(amount),
        price=take_profit_price,
        trigger_price=trigger_profit_price,
        limit_fee='0.015',
        expiration_epoch_seconds=time.time() + 15000,
    ).data
    print(take_profit_order)

    return {
        "market_buy_order": market_buy_order,
        "stop_loss_order": stoploss_order,
        "take_profit_order": take_profit_order
    }


def get_stop_limit_price(sell_price, stop_loss):
    return float(sell_price) * (1 + (stop_loss/100))


def go_short(client, amount, stop_loss, roi):
    # Get our position ID.
    account_response = client.private.get_account()
    position_id = account_response.data['account']['positionId']

    # TODO: Market should be an argument.
    eth_market = client.public.get_markets(market=consts.MARKET_ETH_USD)
    sell_price = eth_market.data['markets']['ETH-USD']['indexPrice']
    slippage: float = 2.0

    # Make a market sell order
    order_params = {
        'position_id': position_id,
        'market': consts.MARKET_ETH_USD,
        'side': consts.ORDER_SIDE_SELL,
        'order_type': consts.ORDER_TYPE_MARKET,
        'post_only': False,
        'size': str(amount),
        # Lowest possible sell price with slippage included
        'price': '%.1f' % (float(sell_price) - slippage),
        'expiration_epoch_seconds': time.time() + 15000,
        'time_in_force': consts.TIME_IN_FORCE_FOK,
        'limit_fee': '0.015',
    }
    market_sell_order = client.private.create_order(**order_params).data

    # Also make a stop loss order
    stop_limit_price = '%.1f' % (get_stop_limit_price(sell_price, stop_loss))
    stoploss_order = client.private.create_order(
        position_id=position_id,
        market=consts.MARKET_ETH_USD,
        side=consts.ORDER_SIDE_BUY,
        order_type=consts.ORDER_TYPE_STOP,
        post_only=False,
        size=str(amount),
        price=stop_limit_price,
        trigger_price=stop_limit_price,
        limit_fee='0.015',
        expiration_epoch_seconds=time.time() + 15000,
    ).data

    take_profit_price = '%.1f' % (float(sell_price) * (1 - (roi/100)))
    trigger_profit_price = '%.1f' % (float(sell_price) * (1 - (roi/200)))
    # Also make a take-profit order
    take_profit_order = client.private.create_order(
        position_id=position_id,
        market=consts.MARKET_ETH_USD,
        side=consts.ORDER_SIDE_BUY,
        order_type=consts.ORDER_TYPE_TAKE_PROFIT,
        post_only=False,
        size=str(amount),
        price=take_profit_price,
        trigger_price=trigger_profit_price,
        limit_fee='0.015',
        expiration_epoch_seconds=time.time() + 15000,
    ).data

    return {
        "market_buy_order": market_sell_order,
        "stop_loss_order": stoploss_order,
        "take_profit_order": take_profit_order
    }


def check_if_pending(orders, dydx_client):
    # GEt current active orders
    # If none, return false
    # Else check for a buy order
    # if there, check status
    if orders == {}:
        print("No active orders!")
        return False
    # MAke sure the market buy order is not cancelled
    market_buy_order = dydx_client.private.get_order_by_id(
        orders['market_buy_order']['order']['id']).data
    # Else, clear out orders
    order_status = market_buy_order['order']['status']

    # If pending, return true
    if (order_status == consts.ORDER_STATUS_PENDING):
        print("buy order pending!")
        return True
    # If filled, check stop orders
    elif (order_status == consts.ORDER_STATUS_FILLED):
        print("buy order filled!")
        # Check if we've taken stop loss or profit
        stop_loss_order = dydx_client.private.get_order_by_id(
            orders['stop_loss_order']['order']['id']).data
        if stop_loss_order['order']['status'] == consts.ORDER_STATUS_FILLED:
            print("Target reached! Ready for new orders")
            # if we have, cancel the other order and return false
            dydx_client.private.cancel_order(
                order_id=orders['take_profit_order']['order']['id'])
            return False

        take_profit_order = dydx_client.private.get_order_by_id(
            orders['take_profit_order']['order']['id']).data
        if take_profit_order['order']['status'] == consts.ORDER_STATUS_FILLED:
            print("Target reached! Ready for new orders")
            # if we have, cancel the other order and return false
            dydx_client.private.cancel_order(
                order_id=orders['stop_loss_order']['order']['id'])
            return False

        if stop_loss_order['order']['status'] == consts.ORDER_STATUS_CANCELED or take_profit_order['order']['status'] == consts.ORDER_STATUS_CANCELED:
            print("One of the target orders canceled Ready for new orders")
            # clear out remaining sell orders
            try:
                dydx_client.private.cancel_order(
                    order_id=orders['stop_loss_order']['order']['id'])
                dydx_client.private.cancel_order(
                    order_id=orders['take_profit_order']['order']['id'])
                # TODO: Clear out the current position too
                dydx_client.private.cancel_order(
                    order_id=orders['market_buy_order']['order']['id'])
            except:
                print("One order was already canceled")
            return False
        # IF we haven't, keep waiting return true
        print("Waiting on profit/loss target")
        return True
    else:
        print("Buy order not fulfilled. Ready for new orders!")
        # clear out remaining sell orders
        dydx_client.private.cancel_order(
            order_id=orders['stop_loss_order']['order']['id'])
        dydx_client.private.cancel_order(
            order_id=orders['take_profit_order']['order']['id'])
        return False


def any_active_trades(dydx_client):
    # Check if there is an active buy or sell order (Not stop loss or take profit)
    # If yes, make sure brackets are set
    # Then return true
    market_side_orders = client.private.get_active_orders(
        market=consts.MARKET_ETH_USD,
    )
    print(market_side_orders)

    # Check if there is an active position
    # If yes, make sure brackets are set
    # If brackets not set, close position immediately
    # If no position
    # Then return false


if __name__ == "__main__":
    client = setup_dydx()
    go_short(client, amount=0.01, stop_loss=1, roi=1)
    print(any_active_trades())
