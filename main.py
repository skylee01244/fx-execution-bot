from bot.core import SaxoTradingBot

def main():
    print("FX Trading Bot")
    token = input("Paste your Saxo Bearer Token: ").strip()

    bot = SaxoTradingBot(token)
    bot.run()

if __name__ == "__main__":
    main()
