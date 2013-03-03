import json
import urllib2


class Card(object):
    def __init__(self, cardDict, FifaClient):
        self.cardDict = cardDict
        self.client = FifaClient
        self.price = self.cardDict.get('buyNowPrice')
        self.timeLeft = self.cardDict.get('expires')
        self.resourceID = self.cardDict.get('itemData').get('resourceId')
        self.position = self.cardDict.get('itemData').get('preferredPosition')
        self.tradeID = self.cardDict.get('tradeId')
        self.baseId = self.getBaseId()
        self.itemID = self.cardDict.get('itemData').get('id')
        self.position = self.cardDict.get('itemData').get('preferredPosition')
        self.hasContract = self.cardDict.get('itemData').get('contract') > 0
        self.sellPrice = self.getSellPrice()
        self.rare = self.cardDict.get('itemData').get('rareflag') > 0
        self.rating = self.cardDict.get('itemData').get('rating')
        self.formation = self.cardDict.get('itemData').get('formation')
        self.discardValue = self.cardDict.get('itemData').get('discardValue')
        self.lastSalePrice = self.cardDict.get('itemData').get('lastSalePrice')
        self.getInfo()

    def __str__(self):
        return str(self.cardDict)

    def getSellPrice(self):
        sellPrice = self.price
        while self.price + (.05 * sellPrice) + 300 > sellPrice:
            sellPrice += 100
        return sellPrice

    def getBaseId(self):
        version = 0
        baseId = self.resourceID
        while baseId > 16777216:
            version += 1
            if version == 1:
                baseId -= 1342177280
            elif version == 2:
                baseId -= 50331648
            else:
                baseId -= 16777216

        return baseId

    def getAveragePrice(self, start, averagePrice, formation):
        priceData = self.client.playerSearch(start, 40, 'gold', formation, '', self.nationality, self.league, self.team, 0, 0, 0, 0)
        if priceData != "":
            for card in priceData:
                if self.resourceID == card.resourceID and self.position == card.position:
                    if int(card.cardDict.get('currentBid')) > 0:
                        averagePrice.append(int(card.cardDict.get('currentBid')))
                    else:
                        averagePrice.append(int(card.cardDict.get('startingBid')))

            if len(averagePrice) < 40 and start < 720:
                return self.getAveragePrice(start + 40, averagePrice, formation)

        averagePrice.sort(key=int)
        if len(averagePrice) < 40:
            return 0
        else:
            return averagePrice

    def getInfo(self):
        playerURL = 'http://cdn.content.easports.com/fifa/fltOnlineAssets/2013/fut/items/web/' + str(self.baseId) + '.json'
        req = urllib2.Request(playerURL)
        d = urllib2.urlopen(req)
        returnData = dict(json.loads(d.read()))
        returnData = returnData.get('Item')

        self.nationality = returnData.get('NationId')
        self.league = returnData.get('LeagueId')
        self.team = returnData.get('ClubId')
        if returnData.get('CommonName') is None:
            self.name = returnData.get('LastName').encode('utf-8')
        else:
            self.name = returnData.get('CommonName').encode('utf-8')
