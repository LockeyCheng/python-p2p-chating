#coding:utf-8
'''
file:client.py.py
date:2017/9/10 11:01
author:lockey
email:lockey@123.com
platform:win7.x86_64 pycharm python3
desc:p2p communication clientside
'''

import socket,sys,re,json
HOST = '192.168.1.7'
PORT = 8022
ADDR =(HOST,PORT)
BUFSIZE = 1024

sock = socket.socket()
userAccount = None
def register():
    print("""
    Glad to have you a member of us!
    """)
    myre = r"^[_a-zA-Z]\w{0,}"
    accout = input('Please input your account: ')
    if not re.findall(myre, accout):
        print('Account illegal!')
        return None
    password1  = input('Please input your password: ')
    password2 = input('Please confirm your password: ')
    if not (password1 and password1 == password2):
        print('Password not illegal!')
        return None
    global userAccount
    userAccount = accout
    regInfo = [accout,password1,'register']
    datastr = json.dumps(regInfo)
    print(datastr)
    sock.send(datastr.encode('utf-8'))
    data = sock.recv(BUFSIZE)
    data = data.decode('utf-8')
    if data == '0':
        print('Success!')
        return True
    elif data == '1':
        print('Account existed!')
        return False
    else:
        print('Failed!')
        return False

def login():
    print("""
    Welcome to login in!
    """)
    myre = r"^[_a-zA-Z]\w{0,}"
    accout = input('Account: ')
    if not re.findall(myre, accout):
        print('Account illegal!')
        return None
    password = input('Password: ')
    if not password:
        print('Password illegal!')
        return None
    global userAccount
    userAccount = accout
    loginInfo = [accout, password,'login']
    datastr = json.dumps(loginInfo)
    sock.send(datastr.encode('utf-8'))
    data = sock.recv(BUFSIZE)
    if data == '0':
        print('Success!')
        return True
    else:
        print('Failed to login in(user not exist or username not match the password)!')
        return False

def addGroup():
    myre = r"^[_a-zA-Z]\w{0,}"
    groupname = input('Please input group name: ')
    if not re.findall(myre, groupname):
        print('group name illegal!')
        return None
    return groupname

def chat(target):
    while True:
        print('{} -> {}: '.format(userAccount,target))
        msg = input()
        if len(msg) > 0 and not msg in 'qQ':
            if 'group' in target:
                optype = 'group'
            else:
                optype = 'person'

            dataObj = {'type': optype, 'to': target, 'msg': msg, 'froms': userAccount}
            datastr = json.dumps(dataObj)
            sock.send(datastr.encode('utf-8'))
            data = sock.recv(BUFSIZE)
            if data.decode('utf-8') == '-1':
                print('can not connect to target!')
                continue
            dataObj = json.loads(data.decode('utf-8'))
            print('{} -> {}'.format(dataObj['froms'], dataObj['msg']))
            continue
        elif msg in 'qQ':
            break
        else:
            print('Send data illegal!')

def main():
        menu = """
        (CP): Chat with individual
        (CG): Chat with group member
        (AG): Add a group
        (H):  For help menu
        (Q):  Quit the system
        """
        try:
            sock.connect(ADDR)
            print('Connected with server')
            while True:
                loginorReg = input('(l)ogin or (r)egister a new account: ')
                if loginorReg in 'lL':
                    log = login()
                    if log:
                        break
                if loginorReg in 'rR':
                    reg = register()
                    if reg:
                        break

            print(menu)
            while True:
                operation = input('Please input your operation("h" for help): ')
                if operation in 'cPCPCpcp' or operation in 'cgCGCgcG':
                    target = input('Who or which group would you like to chat with: ')
                    chat(target)
                    continue

                if operation in 'agAGAgaG':
                    addGroup()
                    continue

                if operation in 'hH':
                    print(menu)
                    continue

                if operation in 'qQ':
                    sys.exit(1)
                else:
                    print('No such operation!')

        except Exception:
            print('error')
            sock.close()
            sys.exit()

if __name__ == '__main__':
    main()