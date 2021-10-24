import numpy as np
import math
from matplotlib import pyplot as plt
import networkx as nx
import time 

def show_placement(r_place,netlist,gate_connects):
    plt.rcParams["figure.figsize"] = [12,10]
    G=nx.Graph()
    for n in netlist.keys():
        for i in range(len(netlist[n])):
            for j in range(i+1,len(netlist[n])):
                G.add_edges_from([(netlist[n][i],netlist[n][j])])
    pos = {}
    gates = list(gate_connects.keys())
    if(len(gates)):
        for i in range(np.size(r_place,0)):
            pos[gates[i]] = (r_place[i][0], r_place[i][1])
    else:
        for i in range(np.size(r_place,0)):
            pos[i+1] = (r_place[i][0], r_place[i][1])
    for p in pad_connects:
        for n in pad_connects[p][0]:
            for g in netlist[n]:
                G.add_edges_from([(p,g)])
        pos[p] = (pad_connects[p][1][0],pad_connects[p][1][1])
    placement_graph = nx.spring_layout(G,pos=pos,fixed=pos.keys())
    nx.draw_networkx(G,pos)
    plt.show()
    return 0

def wirelen(gate,gate_connects):
    dis = 0
    for g in range(0,len(gate_connects),2):
        dis = dis + abs(gate[0] - gate_connects[g]) + abs(gate[1]-gate_connects[g+1])
    return dis

def find_conn(g,gate_connects,netlist,pad_connects,r_place):
    g_connects = np.array([])
    for n in gate_connects[g]:
        for gates in netlist[n]:
            if(gates!=g):
                if(gates<G+1):
                    g_connects = np.append(g_connects,r_place[gates-1])
                else:
                    g_connects = np.append(g_connects,pad_connects[gates][1][:])
    return g_connects

def optimize(r_place, gate_connects, pad_connects, netlist):
    swap_gates = np.random.randint(0,np.size(r_place,0),size=(1,2))+1
    gate1_connects = find_conn(swap_gates[0,0],gate_connects,netlist,pad_connects,r_place)
    gate2_connects = find_conn(swap_gates[0,1],gate_connects,netlist,pad_connects,r_place)
    wl_old = wirelen(r_place[swap_gates[0,0]-1,:],gate1_connects) + wirelen(r_place[swap_gates[0,1]-1,:],gate2_connects)   
    wl_new = wirelen(r_place[swap_gates[0,1]-1,:],gate1_connects) + wirelen(r_place[swap_gates[0,0]-1,:],gate2_connects)
    diff = 0
    if((wl_new-wl_old)<0):
        r_place[swap_gates[0,0]-1,:] = r_place[swap_gates[0,0]-1,:] + r_place[swap_gates[0,1]-1,:]
        r_place[swap_gates[0,1]-1,:] = r_place[swap_gates[0,0]-1,:] - r_place[swap_gates[0,1]-1,:]
        r_place[swap_gates[0,0]-1,:] = r_place[swap_gates[0,0]-1,:] - r_place[swap_gates[0,1]-1,:] 
        diff = wl_new - wl_old
    return r_place,diff

def place(G,L):
    # To ensure even distribution 
    place_box = math.sqrt((L*L)/G)
    n = int(L/place_box)

    r_place = np.random.rand(G,2) * place_box
    for i in range(n):
        for j in range(n):
            r_place[i*n+j,0] = r_place[i*n+j,0] + (j*place_box)
            r_place[i*n+j,1] = r_place[i*n+j,1] + (i*place_box)
    r_place[n*n:,:] = np.random.rand(G-(n*n),2) * L
    return r_place

gln = input("Input the netlist file name: ")                                        #Gate level netlist
ckt = open(gln,"r")
ckt = ckt.read().split("\n")
ckt = [ckt[i].split(" ") for i in range(len(ckt))]

G,N = int(ckt[0][0]),int(ckt[0][1])                 #G = number of gates, N = number of nets
gate_connects = {}
for i in range(G):
    gate_connects[i+1] = []
    for j in ckt[i+1][2:]:
        if(j):
            gate_connects[i+1].append(int(j))       #gate_connects gives gate: nets connected to it

P = int(ckt[G+1][0])                                #P = number of pads
pad_connects = {}
for i in range(P):
    pad_connects[G+i+1] = [[int(ckt[G+i+2][1])],[int(ckt[G+i+2][2]),int(ckt[G+i+2][3])]]    
                                                    #pad_connects gives pad: nets connected to it, location of pad (x,y)
netlist = {}
for g in gate_connects.keys():
    for n in gate_connects[g]:
        if(n in netlist.keys()):
            netlist[n].append(g)
        else:
            netlist[n] = [g]
        for p in pad_connects.keys():
            if(pad_connects[p][0][0]==n):
                netlist[n].append(p)
for n in netlist.keys():
    netlist[n] = list(set(netlist[n]))
L = 100                                             #Size of the chip 

print("Placement process started: ")
start_time = time.time()
r_place = place(G,L)                                #Random placement as the first step (However, a general gap between the gates is maintained)

wirelength = 0
for g in gate_connects.keys():
    connections = find_conn(g,gate_connects,netlist,pad_connects,r_place)
    wirelength = wirelength + wirelen(r_place[g-1],connections)

iterations = 100
chg = 0
for i in range(iterations):
    r_place,diff = optimize(r_place,gate_connects,pad_connects,netlist)
    chg = chg + diff
    print("Iteration: "+str(i+1))

print("Placement complete in time "+str(time.time()-start_time)+" seconds")
print("Initial wirelength: "+str(wirelength))
print("Final wirelength: "+str(wirelength+chg))
show_placement(r_place,netlist,gate_connects)
