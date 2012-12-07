import Fifa13Client
import urllib2



class Functions(object):
    
    def __init__(self,client):
        self.client = client
        
    def get59thMinuteCards(self,start,formation,maxPrice,maxBIN,lowestTime): 
        
            data = self.client.playerSearch(start,15,'gold',formation,'',0,0,0,0,maxPrice,0,maxBIN)
            
            
            if not data : timeLeft = 0
            else: timeLeft = int(data[0].timeLeft)
            while timeLeft < lowestTime or timeLeft > 3580:
                if timeLeft > 4500:
                    start -= 300
                elif timeLeft > 3800:
                    start-= 75
                elif timeLeft >3700:
                    start -= 50  
                elif timeLeft > 2500:
                    start += 200
                elif timeLeft == 0:
                    start = 9900
                    lowestTime -= 200
                else:
                    start +=500
                return self.get59thMinuteCards(start,formation,maxPrice,maxBIN,lowestTime)
            self.client.start = start-10
            return data
            
    
    
                
                                                          