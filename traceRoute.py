# 1.160.23.145
import subprocess as sp
import shlex
import re

# シェルインジェクション防止
remoteAddr = shlex.quote("111.223.86.177")

traceLogPath = "/tmp/traceLog"

tcptraceroute = "sudo tcptraceroute -m 50 {0} > {1}".format(remoteAddr, traceLogPath)

exitStatus = sp.call(tcptraceroute, shell=True)

# 正常終了
if exitStatus == 0:
    with open(traceLogPath,"r") as f:
        relayRemoteAddrList = []
        for row in f:
            splitList = row.split("  ")
            if splitList[1][0] != "*":
                relayRemoteAddrList.append(splitList[1].split(" ")[0])

    addressList = []
    for relayRemoteAddr in relayRemoteAddrList:
        relayRemoteAddr = shlex.quote(relayRemoteAddr)
        whois = "whois {0} | grep address: | head -1 > {1}".format(relayRemoteAddr, traceLogPath)
        exitStatus = sp.call(whois, shell=True)

        # 正常終了
        if exitStatus == 0:
            with open(traceLogPath,"r") as f:
                lastAddress = ""
                for row in f:
                    addressList.append(re.sub(r"address: *","",row.strip()))

    addressList = sorted(set(addressList), key=addressList.index)
    addressList.reverse()
    print(addressList)
