#coding:utf-8
'''
file:server.py
date:2017/9/10 14:43
author:lockey
email:lockey@123.com
platform:win7.x86_64 pycharm python3
desc:p2p communication serverside
'''
import socketserver,json,time
import subprocess

connLst = []
groupLst = []
##  代号 地址和端口 连接对象

class Connector(object):   ##存放连接
    def __init__(self,account,password,addrPort,conObj):
        self.account = account
        self.password = password
        self.addrPort = addrPort
        self.conObj = conObj

class Group(object):
    def __init__(self,groupname,groupOwner):
        self.groupId = 'group'+str(len(groupLst)+1)
        self.groupName = groupname
        self.groupOwner = groupOwner
        self.createTime = time.time()
        self.members=[groupOwner]

class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        print("got connection from",self.client_address)
        userIn = False
        global connLst
        global groupLst
        while not userIn:
            conn = self.request
            data = conn.recv(1024)
            if not data:
                continue
            dataobj = json.loads(data.decode('utf-8'))

            #如果连接客户端发送过来的信息格式是一个列表且注册标识为False时进行用户注册
            ret = '0'
            if type(dataobj) == list and not userIn:
                account = dataobj[0]
                password = dataobj[1]
                optype = dataobj[2]
                existuser = False
                if len(connLst) > 0:
                    for obj in connLst:
                        if obj.account == account:
                            existuser = True
                            if obj.password == password:
                                userIn = True
                                break
                if optype == 'login' and (not userIn or not existuser):
                    ret = '1'
                    print('login111111')
                else:
                    if existuser:
                        ret = '1'
                        print('reg1111')
                    else:
                        try:
                            print(account)
                            conObj = Connector(account,password,self.client_address,self.request)
                            connLst.append(conObj)
                            print(connLst)
                            userIn = True
                        except:
                            ret = '99'
            conn.sendall(ret.encode('utf-8'))
            if ret == '0':
                break

        while True:
            conn = self.request
            data = conn.recv(1024)
            if not data:
                continue
            print(data)
            dataobj = json.loads(data.decode('utf-8'))
            if type(dataobj) == str and userIn:
                groupName = dataobj
                groupObj = Group(groupName,self.request)
                groupLst.append(groupObj)
                continue
            #客户端将数据发给服务器端然后由服务器转发给目标客户端
            print(len(connLst))
            print(connLst)
            if len(connLst) > 1 and type(dataobj) == dict:
                sendok = False
                if dataobj['type'] == 'group':
                    print('group',data)
                    for obj in groupLst:
                        if obj.groupName == dataobj['to']:
                            for user in obj.members:
                                user.sendall(data)
                else:
                    for obj in connLst:
                        if dataobj['to'] == obj.account:
                            obj.conObj.sendall(data)
                            sendok = True
                    if sendok == False:
                        print('no target valid!')
            else:
                conn.sendall('-1'.encode('utf-8'))
                continue

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('192.168.1.7',8022),MyServer)
    print('waiting for connection...')
    server.serve_forever()