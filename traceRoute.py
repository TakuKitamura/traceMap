# 1.160.23.145
import subprocess as sp
import shlex
import re
import urllib.request
import urllib.parse
import json
import folium


# シェルインジェクション防止
remoteAddr = shlex.quote("www.mygov.go.ke")

traceLogPath = "/tmp/traceLog"

tcptraceroute = "sudo tcptraceroute -m 50 {0} > {1}".format(remoteAddr, traceLogPath)

exitStatus = sp.call(tcptraceroute, shell=True)

# 正常終了
if exitStatus == 0:
    with open(traceLogPath,"r") as f:
        relayRemoteAddrList = []
        for row in f:
            splitList = row.split("  ")
            if splitList[0] == "":
                splitList.pop(0)

            print(splitList)
            for relayRemoteAddr in splitList[1].strip().split(" "):
                if relayRemoteAddr != "*":
                    relayRemoteAddrList.append(relayRemoteAddr)
                    break

        print(relayRemoteAddrList)
    addressList = []
    for relayRemoteAddr in relayRemoteAddrList:
        relayRemoteAddr = shlex.quote(relayRemoteAddr)
        whois = "whois {0} | grep address: | sort | uniq | sed -e 's/address:      / /g' | tr -d '\n' > {1}".format(relayRemoteAddr, traceLogPath)
        exitStatus = sp.call(whois, shell=True)

        # 正常終了
        if exitStatus == 0:
            with open(traceLogPath,"r") as f:
                lastAddress = ""
                for row in f:
                    addressList.append(row.strip())

    addressList = sorted(set(addressList), key=addressList.index)
    addressList.reverse()
    print(addressList)

    m = folium.Map(location=[34.981899, 135.963612])
    folium.Marker([34.981899, 135.963612], popup='Here').add_to(m)

    locationList = []
    for address in addressList:

        address = urllib.parse.quote(shlex.quote(address))
        googleAPIURL = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key=AIzaSyBrIg9eLceXYlnV26dXfB_5fB5Ng84l3k0".format(address)
        response = urllib.request.urlopen(googleAPIURL).read().decode('utf8')
        obj = json.loads(response)

        if obj['status'] == 'OK':
            locationList.append({'lat': float(obj['results'][0]['geometry']['location']['lat']), 'lng': float(obj['results'][0]['geometry']['location']['lng'])})
            # folium.Marker([location['lat'], location['lng']], popup='Mt. Hood Meadows').add_to(m)
            # print(location)
        elif obj['status'] == 'ZERO_RESULTS':
            ipinfoURL = "https://ipinfo.io/{0}".format()
        else:
            print('{0}のジオエンコーディングに失敗しました。'.formta(obj))

    locationList.append({'lat': 34.981899, 'lng': 135.963612})

    for i in range(0, len(locationList)):
        folium.Marker([locationList[i]['lat'], locationList[i]['lng']], popup=str(i)).add_to(m)

        if i + 1 < len(locationList):
            p1 = [locationList[i]['lat'], locationList[i]['lng']]
            p2 = [locationList[i + 1]['lat'], locationList[i + 1]['lng']]


            folium.PolyLine(locations=[p1, p2], color='blue', weight=5.5).add_to(m)


    print(locationList)

    m.save('/Users/kitamurataku/work/traceMap/test.html')
