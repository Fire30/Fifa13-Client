# Fire30
from Card import Card
import time
#import Functions
import json
import urllib2
import ConfigParser


"""Make sure to change false to False"""


class UrlRequestor(object):
        def __init__(self, url, headers, data):
                self.url = url
                self.headers = headers
                self.request = urllib2.Request(url)
                self.data = data
                if self.data:
                        self.request.add_data(self.data)
                for headerName, headerContent in self.headers.iteritems():
                        
                        self.request.add_header(headerName, headerContent)
        def open(self):
                self.content = urllib2.urlopen(self.request)
        def getHeader(self, headerName):
                return self.content.info().getheader(headerName)
        def getReturnData(self):
                return dict(json.loads(self.content.read()))
        
class FifaClient(object):
        
        def __init__(self,username,password,securityHash,authData):
                self.username = username
                self.password = password
                self.securityHash = securityHash
                self.authData = json.dumps(authData, separators=(',',':'))
                self.start = 9000
                self.doLogin()
                self.quicksellList = list()
                self.client = self
                
        def doLogin(self):
                '''
                securityHash is the Respone data sent entering your security question at this adress:
                 http://www.ea.com/p/fut/a/card-360/l/en/s/p/ut/game/fifa13/phishing/validate

                authdata is the POST data from:
                http://www.ea.com/p/fut/a/card-360/l/en/s/p/ut/auth
                it looks something like this
                { "isReadOnly": false, "sku": "###, "clientVersion": 3, "nuc": ###, "nucleusPersonaId": ###, "nucleusPersonaDisplayName": "GT", "nucleusPersonaPlatform": "360", "locale": "en-GB", "method": "idm", "priorityLevel":4, "identification": { "EASW-Token": "" } }
                Yes you take the whole thing

                '''
                
                content ="email="+self.username+"&password="+self.password+"&=Sign+In"
                requestor = UrlRequestor("https://www.ea.com/uk/football/services/authenticate/login", {'Content-Type': 'application/x-www-form-urlencoded','Referer': 'http://www.ea.com/uk/football/login?redirectUrl=http://www.ea.com/uk/football/fifa-ultimate-team'}, content)
                requestor.open()
                # logs in and gets EASW_KEY
                self.EASW_KEY = requestor.getHeader('Set-Cookie')  # gets EASW_KEY from the cookies
                self.EASF_SESS = self.EASW_KEY.split('easf_sess_com=')[1]
                self.EASF_SESS = self.EASF_SESS.split(';')[0]

                self.EASF_SESS = 'easf_sess_com=' + self.EASF_SESS
                self.EASW_KEY = self.EASW_KEY.split(';')[0]
                print self.EASW_KEY
        
                
        # Grabs X-UT-SID
                
                requestor = UrlRequestor("http://www.ea.com/p/fut/a/card-360/l/en_US/s/p/ut/auth", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + ";"}, self.authData)
                requestor.open()
                self.XUT_SID = requestor.getHeader('X-UT-SID')
                print self.XUT_SID
                
                
        # Submits Security question and grabs FUTPHISHING key
                requestor = UrlRequestor("http://www.ea.com/p/fut/a/card-360/l/en_US/s/p/ut/game/fifa13/phishing/validate", {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie' : self.EASW_KEY + ";", 'X-UT-SID' :self.XUT_SID}, 'answer=' + self.securityHash)
                requestor.open()
                self.FUTPHISHING = requestor.getHeader('Set-Cookie').split(';')[0]
                
                
        def buyItem(self,trade, value):

                bidURL = 'https://utas.fut.ea.com/ut/game/fifa13/trade/'+str(trade)+'/bid'
                value = {"bid":value}
                value = json.dumps(value, separators=(','':'))
                
                req = urllib2.Request(bidURL)
                req.add_data(value)
                req.add_header('Cookie', self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; "  )
                req.add_header('Content-Type', 'application/json')
                req.add_header('x-http-method-override', 'PUT')
                req.add_header('Content-Length', len(value))
                req.add_header('X-UT-SID', self.XUT_SID)
                d = urllib2.urlopen(req)
                
                searchXML =  dict(json.loads(d.read()))
                
                if searchXML.get('string') == 'Permission Denied':
                        return False
                else:
                        return True
        
        def quickSell(self,itemID):
                requestor = UrlRequestor('https://utas.fut.ea.com/ut/game/fifa13/item/' + str(itemID), {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' : self.XUT_SID, 'x-http-method-override':'DELETE', 'X-UT-Embed-Error' : True},"")     
                requestor.open()
        
        def removeExpired(self,tradeID):
                requestor = UrlRequestor('https://utas.fut.ea.com/ut/game/fifa13/watchlist?tradeId=' + str(tradeID),{'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' : self.XUT_SID, 'x-http-method-override':'DELETE', 'X-UT-Embed-Error' : True},"")
                requestor.open()
                
        def getExpiredCards(self):
                watchListId = list()
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/watchlist", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'GET'}, '')
                requestor.open()
                for card in requestor.getReturnData().get('auctionInfo'):
                        if card.get('bidState') == 'outbid':
                                watchListId.append(Card(card, self))
                return watchListId
        
        def getBoughtCardsInWatchList(self):
                watchListId = list()
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/watchlist", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'GET'}, '')
                requestor.open()
                for card in requestor.getReturnData().get('auctionInfo'):
                        if card.get('bidState') == 'highest' and card.get('tradeState') == 'closed':
                                watchListId.append(Card(card, self))
                return watchListId
        
        def getTradePileId(self):
                # returns the list of Item ID's in your TradePile
                cardIDList = list()
                previousBuyNowPrice = list()
                previousStartingBid = list()
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/tradepile", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'GET'}, '')
                requestor.open()
                
                for card in requestor.getReturnData().get('auctionInfo'):
                        cardIDList.append(card.get('itemData').get('id'))
                        previousBuyNowPrice.append(card.get('buyNowPrice'))
                        previousStartingBid.append(card.get('startingBid'))     
                return (cardIDList, previousBuyNowPrice, previousStartingBid)
        
        def getTradePileLegnth(self):
                return len(self.getTradePileId()[0])
        
        def moveCard(self, itemID, pile):
                data = json.dumps({"itemData":[{"id": itemID , "pile":"trade"}]}, separators=(',',':'))
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/item", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'PUT'}, data)
                requestor.open()
                if requestor.getReturnData().get('itemData') != "": return True
                return False
        
        def postTrade(self , itemID, startBid, buyNowPrice, duration):
                
                content = {"duration":str(duration), "itemData":{"id":str(itemID)}, "buyNowPrice":str(buyNowPrice), "startingBid":str(startBid)};
                data = json.dumps(content, separators=(',',':'))
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/auctionhouse", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'POST'}, data)
                requestor.open()
                if requestor.getReturnData().get('string') == "Bad Request":return False
                return True
        
        
        def playerSearch(self, start, count , level, formation, position, nationality, league, team, minBid, maxBid, minBIN, maxBIN):
                '''
                level - gold,silver,bronze
                formation- f then formation. Ex. f433, f3412
                position-Can be the zone, ex defense, midfield, or attacker, or the actual position, ex RB or ST
                nationality- integer, ex. 14-England 20-spain
                league- integer, ex. serie A - 31, Liga BBVA - 53, Premier League - 13
                Team- integer
                Rest- what the Name implies
                '''
                
                searchstring = ""
                cardList = list()
                
                if level != "" and level != "any": searchstring += "&lev=" + level
                if formation != "" and formation != "any":searchstring += "&form=" + formation
                if position != "" and position != "any":
                        if position == "defense" or position == "midfield" or position == "attacker":
                                searchstring += "&zone=" + position
                        else:
                                searchstring += "&pos=" + position
                if nationality > 0:searchstring += "&nat=" + str(nationality)
                if league > 0:searchstring += "&leag=" + str(league)
                if team > 0:searchstring += "&team=" + str(team)
                if minBIN > 0:searchstring += "&minb=" + str(minBIN)
                if maxBIN > 0:searchstring += "&maxb=" + str(maxBIN)
                if minBid > 0:searchstring += "&micr=" + str(minBid)
                if maxBid > 0:searchstring += "&macr=" + str(maxBid)
                
                
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/auctionhouse?type=player&start=" + str(start) + "&num=" + str(count) + searchstring, {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'GET'}, "")
                requestor.open()
                lol = requestor.getReturnData().get('auctionInfo')
                
                
                
                for card in lol:
                        cardList.append(Card(card, self))
                return cardList
                
        
        def getUnAssignedIDs(self):
                watchListId = list()
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/purchased/items", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'GET'}, '')
                requestor.open()
                
                for card in requestor.getReturnData().get('itemData'):
                        watchListId.append(card.get('id'))
                return watchListId
                
        def sellItemsInTradePile(self):
                        
                ItemIds = self.getTradePileId()
                
                previousBuyItNow = ItemIds[1]
                previousStartingBid = ItemIds[2]
                ItemIds = list(ItemIds[0])
                x = 0
                for ids in ItemIds:
                        self.postTrade(str(ids), str(previousStartingBid[x]), str(previousBuyItNow[x]), str(3600))
                        x += 1
                        
        def getCoins(self):
                requestor = UrlRequestor("https://utas.fut.ea.com/ut/game/fifa13/user/credits", {'Content-Type': 'application/json', 'Cookie' : self.EASW_KEY + "; " + self.EASF_SESS + "; " + self.FUTPHISHING + "; ", 'X-UT-SID' :self.XUT_SID, 'x-http-method-override':'GET'}, "")
                requestor.open()        
                return  requestor.getReturnData().get('credits')
        

def autobuyContracts():

        client = FifaClient(EMAIL, PASSWORD, HASH, AUTHDATA)
        while client.getCoins() > 500 and len(client.getTradePileId()[0]) < 30:
                searchURL = "https://utas.fut.ea.com/ut/game/fifa13/auctionhouse?type=development&num=16&start=0&maxb=200&blank=10&cat=contract&lev=gold"
                req = urllib2.Request(searchURL)
                req.add_header('Cookie', client.EASW_KEY + "; " + client.EASF_SESS + "; " + client.FUTPHISHING + "; ")
                req.add_header('Content-Type', 'application/json')
                req.add_header('x-http-method-override', 'GET')
                req.add_header('X-UT-SID', client.XUT_SID)
                d = urllib2.urlopen(req)
                                
                searchXML = dict(json.loads(d.read()))
                auctionInfo = searchXML.get('auctionInfo')
        
                for contract in auctionInfo:
                        tradeID = contract.get('tradeId')
                        itemID = contract.get('itemData').get('id')
                        if client.buyItem(tradeID, 200):
                                print 'Bought Contract for 200 coins'
                                if client.moveCard(str(itemID), 'trade'):
                                        client.postTrade(str(itemID), str(250), str(0), str(3600))
                                        print 'Contract posted For 250 Coins'
        tradePileCards = client.getTradePileId()
        for x in range(0, client.getTradePileLegnth()):
                client.postTrade(str((tradePileCards[0])[x]), str((tradePileCards[2])[x]), str(0), str(3600))
                
def doMain():
        config = ConfigParser.ConfigParser()
        config.read("accounts.ini")
        for section in config.sections():
                email = config.get(section,'email')
                password = config.get(section,'password')
                the_hash = config.get(section,'hash')
                authdata = config.get(section,'authdata')
                authdata = eval(authdata)
                client = FifaClient(email,password,the_hash,authdata)
                print('Total Coins = ' + str(client.getCoins()))
                print('Total Items In TradePile = ' + str(client.getTradePileLegnth()))

if __name__ == "__main__":
        doMain()
