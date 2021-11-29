import threading
import socket

lock = threading.Lock()
global shutdown
shutdown = True

class channel:
    def __init__(self, id, value, changed):
        
        self.id = id
        self.value = value
        self.changed = changed
    
    def newval(self, d):
        lock.acquire()
        self.value = d
        self.changed = True
        lock.release()
    
    def update(self):
        lock.acquire()
        self.changed = False
        lock.release()


def finder(data):
    d = data[5:]
    for x in range(chncrt):
        if(chn[x].id == d):
            print("Inside If Finder")
            break
    return x

def subscribe(x, conn):

    print("In Subscribe")
    while shutdown:
        if(chn[x].changed == True):
            conn.send(str.encode(chn[x].value + " " + chn[x].id))
            print("Sending Data")
            chn[x].update()


def node(conn):

    s = []
    scount = 0
    try:
        conn.send(str.encode("You are connected to VulpesMQTT \nTo Subcribe to a channel type \"subs/<channel-id>\"\nTo Publish to a channel type \"pubs/<channel-id>\"\nTo get the list of channels type \"channel/ls\"\n"))
        while shutdown:

                data = conn.recv(1024)
                d = data.decode('utf-8')
                if(d != ""):
                    if("subs" in d):
                        t = finder(d)
                        s.append(threading.Thread(target=subscribe, args=(t, conn,)))
                        s[scount].start()
                        scount += 1
                    elif("pubs" in d):
                        p = finder(d[5:])
                    elif("channel" in d):
                        print("ls")
                    else:
                        print("Recieved Data")
                        print("Changing value")
                        chn[p].newval(d)

                else:
                    print("Closing Connection")
                    conn.close()

    except OSError:
        print("Error Occured")

    except UnicodeDecodeError:
        conn.send(str.encode("Dont send ^\ "))
        conn.send(str.encode("Closing Connection"))
        conn.close()


def create():
    global chn
    chn = []
    global chncrt
    chncrt = 0
    while shutdown:
        print("To create a channel type \"create\"")
        crt = input()
        if(crt == "create"):
            print("Type of channel you want to create\n1. Switch (actually boolean) \n2. String")
            typ = input()
            if(typ == "Switch"):
                id = input("Give a name to your channel : ")
                value = False
                changed = False
                chn.append(channel(id, value, changed))
                
            if(typ == "String"):
                id = input("Give a name to your channel : ")
                value = ""
                changed = False
                chn.append(channel(id, value, changed))
                
            print("Channel created : \nName : " + chn[chncrt].id)
            chncrt = chncrt + 1


server = socket.socket()
server.bind(('',2002))
server.listen(5)

t = []
tcount = 0
chnthread = threading.Thread(target=create)
chnthread.start() 



while True:
    
    try:
        conn, addr = server.accept()
        print("Got connection from " + addr[0] + ':' + str(addr[1]))
        t.append(threading.Thread(target=node, args=(conn, )))
        t[tcount].start()
        tcount = tcount + 1
        print("No. of Thread created : " + str(tcount))
    except Exception as e:
        print(e)
        server.close()
   # except KeyboardInterrupt:
    #    print("Closing All Threads Please Wait....")
     #   shutdown = False
     #   for x in range(tcount):
      #      t[x].join()
