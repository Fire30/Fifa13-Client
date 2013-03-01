#import Card
from Fifa13Client import FifaClient
import time
import ConfigParser


def doMain():
    try:
        config = ConfigParser.ConfigParser()
        config.read("accounts.ini")
        for section in config.sections():
            email = config.get(section, 'email')
            password = config.get(section, 'password')
            the_hash = config.get(section, 'hash')
            authdata = config.get(section, 'authdata')
            authdata = eval(authdata)
            client = FifaClient(email, password, the_hash, authdata)
            print('Total Coins = ' + str(client.getCoins()))
            print('Total Items In TradePile = ' + str(client.getTradePileLegnth()))
    except Exception, e:
        print e
        time.sleep(60)
        doMain()

if __name__ == "__main__":
    doMain()
