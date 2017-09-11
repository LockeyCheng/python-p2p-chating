#coding:utf-8
'''
file:server.py
date:2017/9/11 14:43
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
#optype = {'ag':'group adding','cp':'chat with individual','cg':'chat with group'}
class Connector(object):   ##存放连接
    def __init__(self,account,password,addrPort,conObj):
        self.account = account
        self.password = password
        self.addrPort = addrPort
        self.conObj = conObj

class Group(object):
    def __init__(self,groupname,groupOwner):
        self.groupId = 'group'+str(len(groupLst)+1)
        self.groupName = 'group'+groupname
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
                                print('{} has logged in system({})'.format(account,self.client_address))
                                break
                if optype == 'login' and (not userIn or not existuser):
                    ret = '1'
                    print('{} failed to logged in system({})'.format(account, self.client_address))
                else:
                    if existuser:
                        ret = '1'
                        print('{} failed to register({}),account existed!'.format(account, self.client_address))
                    else:
                        try:
                            conObj = Connector(account,password,self.client_address,self.request)
                            connLst.append(conObj)
                            print('{} has registered to system({})'.format(account,self.client_address))
                            userIn = True
                        except:
                            print('%s failed to register for exception!'%account)
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
            dataobj = data.decode('utf-8')
            dataobj = json.loads(dataobj)
            if dataobj['type'] == 'ag' and userIn:
                groupName = dataobj['groupName']
                groupObj = Group(groupName,self.request)
                groupLst.append(groupObj)
                conn.sendall('ag0'.encode('utf-8'))
                print('%s added'%groupName)
                continue

            if dataobj['type'] == 'eg' and userIn:
                groupName = dataobj['groupName']
                ret = 'eg1'
                for group in groupLst:
                    if groupName == group.groupName:
                        group.members.append(self.request)
                        print('{} added into {}'.format(self.client_address,groupName))
                        ret = 'eg0'
                        break
                conn.sendall(ret.encode('utf-8'))
                continue

            #客户端将数据发给服务器端然后由服务器转发给目标客户端
            print('connLst',connLst)
            print('grouplst',groupLst)
            if len(connLst) > 1:
                sendok = False
                if dataobj['type'] == 'cg':
                    print('group',data)
                    for obj in groupLst:
                        if obj.groupName == dataobj['to']:
                            for user in obj.members:
                                if user != self.request:
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