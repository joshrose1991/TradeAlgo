from alpaca.trading.client import TradingClient
Trading_Client = TradingClient("PKPPJM2YUA2TLFFHV6OW","9HjwRnheDOQA64Z2pil8oxDZKTWNgeSgIZJc606s")
print(Trading_Client.get_account().account_number)