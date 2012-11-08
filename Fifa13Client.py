#Fire30

import urllib2
import json
import time

def doLogin(username,password,securityHash, authData):
    '''
    securityHash is the POST data sent entering your security question at this adress:
     http://www.ea.com/p/fut/a/card-360/l/en/s/p/ut/game/fifa13/phishing/validate
   
    authdata is the POST data from:
    http://www.ea.com/p/fut/a/card-360/l/en/s/p/ut/auth
    
    '''
    #logs in and gets EASW_KEY
    content ="email="+username+"&password="+password+"&=Sign+In"
    req = urllib2.Request("https://www.ea.com/uk/football/services/authenticate/login", content, {'Content-Type': 'application/x-www-form-urlencoded'})
    d = urllib2.urlopen(req)
    EASW_KEY = d.info().getheader('Set-Cookie') #gets EASW_KEY from the cookies
    #Gets the Key from = -> ;
    EASF_SESS = EASW_KEY.split('easf_sess_com=')[1]
    EASF_SESS = EASF_SESS.split(';')[0]
    EASF_SESS = 'easf_sess_com='+EASF_SESS
    
    EASW_KEY = EASW_KEY.split(';')[0]
    
    
    #Grabs X-UT-SID 
    authData = json.dumps(authData, separators=(',',':'))
    req = urllib2.Request("http://www.ea.com/p/fut/a/card-360/l/en_US/s/p/ut/auth")
    req.add_data(authData)
    req.add_header('Cookie',EASW_KEY + ";")
    req.add_header('Content-Type', 'application/json')
    f = urllib2.urlopen(req)
    XUT_SID = f.info().getheader('X-UT-SID')    
    
    #Submits Security question and grabs FUTPHISHING key
    req = urllib2.Request('http://www.ea.com/p/fut/a/card-360/l/en_US/s/p/ut/game/fifa13/phishing/validate', 'answer='+securityHash)
    req.add_header('X-UT-SID', XUT_SID)
    req.add_header('Cookie', EASW_KEY + ";")
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    f = urllib2.urlopen(req)
    FUTPHISHING = f.info().getheader('Set-Cookie')
    
    #splits is so that we only have the key
    
    FUTPHISHING = FUTPHISHING.split(';')[0]
    
    #returns a string with all 4 keys seperated by commas
    return EASF_SESS +',' + EASW_KEY + ',' + XUT_SID + ',' + FUTPHISHING

def playerSearch(start,count ,level,formation,position,nationality,league,team,minBid,maxBid,minBIN,maxBIN):
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
    
    
    if level != "" and level != "any":
        searchstring += "&lev="+level;
    if formation != "" and formation!= "any":
        searchstring += "&form="+formation
    if position != "" and position!= "any":
        if position == "defense" or position == "midfield" or position == "attacker":
            searchstring += "&zone="+position
        else:
            searchstring += "&pos="+position
    if nationality > 0:
        searchstring += "&nat="+str(nationality)
    if league > 0:
        searchstring += "&leag="+str(league)
    if team > 0:
        searchstring += "&team="+str(team)
    if minBid > 0:
        searchstring += "&micr="+str(minBid)
    if maxBid > 0:
        searchstring += "&macr="+str(maxBid)
    if minBIN > 0:
        searchstring += "&minb="+str(minBIN)
    if maxBIN > 0:
        searchstring += "&maxb="+str(maxBIN)
                
    searchURL = "https://utas.fut.ea.com/ut/game/fifa13/auctionhouse?type=player&start="+str(start)+"&num="+str(count) + searchstring
    
    #print(searchURL)
    #sets cookies and stuff
    req = urllib2.Request(searchURL)
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-http-method-override', 'GET')
    req.add_header('X-UT-SID', XUT_SID)
    d = urllib2.urlopen(req)
        
    searchXML =  dict(json.loads(d.read()))

    #returns json from EA  
    return searchXML

def buyItem(trade, value):
    
    bidURL = 'https://utas.fut.ea.com/ut/game/fifa13/trade/'+str(trade)+'/bid'
    value = {"bid":value}
    value = json.dumps(value, separators=(','':'))
    
    req = urllib2.Request(bidURL)
    req.add_data(value)
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-http-method-override', 'PUT')
    req.add_header('Content-Length', len(value))
    req.add_header('X-UT-SID', XUT_SID)
    d = urllib2.urlopen(req)
    
    searchXML =  dict(json.loads(d.read()))
    
    
    if searchXML.get('string') == 'Permission Denied':
        return False
    else:
        return True
    
def moveCard(itemID, pile):
    #pile is either trade or club
    searchURL = "https://utas.fut.ea.com/ut/game/fifa13/item"
    req = urllib2.Request(searchURL)
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('X-UT-SID', XUT_SID)
    req.add_header('x-http-method-override', 'PUT')
    req.add_header('Content-Type', 'application/json')
    content ={"itemData":[{"id": itemID ,pile:"trade"}]};
    content = json.dumps(content,separators=(','':'))
    req.add_data(content)
    d = urllib2.urlopen(req)
    
    xmlData = dict(json.loads(d.read()))
    
    if xmlData.get('itemData') != "":
        return True
    else:
        return False

def postTrade(itemID, startBid, buyNowPrice, duration):
    #posts a trade
    searchURL = "https://utas.fut.ea.com/ut/game/fifa13/auctionhouse"
    req = urllib2.Request(searchURL)
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('X-UT-SID', XUT_SID)
    req.add_header('x-http-method-override', 'POST')
    req.add_header('Content-Type', 'application/json')
    content ={"duration":str(duration),"itemData":{"id":str(itemID)},"buyNowPrice":str(buyNowPrice),"startingBid":str(startBid)};
    content = json.dumps(content,separators=(','':'))
    req.add_data(content)
    
    d = urllib2.urlopen(req)
    
    xmlData = dict(json.loads(d.read()))
    
    
    if xmlData.get('string') == "Bad Request":
        return False
    return True
    
def getPurchasePileId():
    #returns the list of Item ID's in your Purchased Pile
    
    cardIDList = list()
    searchURL = "https://utas.fut.ea.com/ut/game/fifa13/purchased/items"
    req = urllib2.Request(searchURL)
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('X-UT-SID', XUT_SID)
    req.add_header('x-http-method-override', 'GET')
    req.add_header('Content-Type', 'application/json')
    
    d = urllib2.urlopen(req)
    
    xmlData = dict(json.loads(d.read()))
    
    xmlData = xmlData.get('itemData')
    
    
    for card in xmlData:
        cardIDList.append(card.get('id'))
    
    return cardIDList
    
def getTradePileId():
    #returns the list of Item ID's in your TradePile
    cardIDList = list()
    searchURL = "https://utas.fut.ea.com/ut/game/fifa13/tradepile"
    req = urllib2.Request(searchURL)
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('X-UT-SID', XUT_SID)
    req.add_header('x-http-method-override', 'GET')
    req.add_header('Content-Type', 'application/json')
    
    d = urllib2.urlopen(req)
    
    xmlData = dict(json.loads(d.read()))
    xmlData =  xmlData.get('auctionInfo')
    
    for card in xmlData:
        cardIDList.append(card.get('itemData').get('id'))
    
    return cardIDList
    
def coinAmount():
    #returns number of coins left
    req = urllib2.Request('https://utas.fut.ea.com/ut/game/fifa13/user/credits')
    req.add_header('Cookie', EASW_KEY + "; " + EASF_SESS + "; " + FUTPHISHING + "; "  )
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-http-method-override', 'GET')
    req.add_header('X-UT-SID', XUT_SID)
    d = urllib2.urlopen(req)
    
    xmlData = dict(json.loads(d.read()))
    
    return xmlData.get('credits')
    


#example session
keys = doLogin('EMAIL','PASSWORD','SECURITYHASH','AUTHDATA')
keys = keys.split(',')
#set the keys
EASF_SESS = keys[0]
EASW_KEY = keys[1]
XUT_SID = keys[2]
FUTPHISHING = keys[3]

print playerSearch(0,16 ,'gold','f433','CB',0,0,0,0,0,0,0)