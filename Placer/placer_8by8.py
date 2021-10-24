# Quadratic placement method 
# Splits the whole chip area into 8 by 8 (i.e. 64) sections
# To maintain even distribution of the cells 
 
import numpy as np
from matplotlib import pyplot as plt
import networkx as nx

def show_placement(QP,netlist,pad_connects,gates=[]):
    plt.rcParams["figure.figsize"] = [12,10]
    G=nx.Graph()
    for n in netlist.keys():
        for i in range(len(netlist[n])):
            for j in range(i+1,len(netlist[n])):
                G.add_edges_from([(netlist[n][i],netlist[n][j])])
    pos = {}
    if(len(gates)):
        for i in range(np.size(QP,0)):
            pos[gates[i]] = (QP[i][0], QP[i][1])
    else:
        for i in range(np.size(QP,0)):
            pos[i+1] = (QP[i][0], QP[i][1])
    for p in pad_connects:
        for n in pad_connects[p][0]:
            for g in netlist[n]:
                G.add_edges_from([(p,g)])
        pos[p] = (pad_connects[p][1][0],pad_connects[p][1][1])
    placement_graph = nx.spring_layout(G,pos=pos,fixed=pos.keys())
    nx.draw_networkx(G,pos)
    plt.show()
    return 0


def place(G,P,gate_connects,pad_connects):
    new_name = {}
    gates = list(gate_connects.keys())
    for i in range(G):
        new_name[gates[i]] = i+1
    
    netlist = {}
    for g in gates:
        for n in gate_connects[g]:
            if(n in netlist.keys()):
                netlist[n].append(g)
            else:
                netlist[n] = [g]
    padlist = {}
    pad_nets = set()
    for p in pad_connects:
        for n in pad_connects[p][0]:
            pad_nets.add(n)
            if(n in padlist.keys()):
                padlist[n].append(p)
            else:
                padlist[n] = [p]

    A = np.zeros((G,G),dtype=float)
    bx = np.zeros((G,1),dtype=float)
    by = np.zeros((G,1),dtype=float)
    for net in netlist.keys():
        n = len(netlist[net])
        k = 0
        if(net in padlist.keys()):
            k = len(padlist[net])
        for i in range(n):
            for j in range(i+1,n):
                A[new_name[netlist[net][i]]-1,new_name[netlist[net][j]]-1] = A[new_name[netlist[net][i]]-1,new_name[netlist[net][j]]-1] - 1/(k+n-1)
                A[new_name[netlist[net][j]]-1,new_name[netlist[net][i]]-1] = A[new_name[netlist[net][j]]-1,new_name[netlist[net][i]]-1] - 1/(k+n-1)
    for g in gates:
        A[new_name[g]-1,new_name[g]-1] = -1*np.sum(A[new_name[g]-1,:])
    for n in pad_nets:
        k = len(padlist[n])
        for p in padlist[n]:
            for g in netlist[n]:
                A[new_name[g]-1,new_name[g]-1] = A[new_name[g]-1,new_name[g]-1] + 1/k
                bx[new_name[g]-1] = bx[new_name[g]-1] + pad_connects[p][1][0]/k
                by[new_name[g]-1] = by[new_name[g]-1] + pad_connects[p][1][1]/k
    QP = np.linalg.solve(A,np.concatenate((bx,by),1))
    circuit = {}
    circuit["Placement"] = np.insert(QP,2,np.transpose(np.array(gates)),axis=1)
    circuit["Netlist"] = netlist
    circuit["Padlist"] = padlist
    circuit["Gate_connects"] = gate_connects
    circuit["Pad_connects"] = pad_connects
    return circuit

def partition(circuit,part,Lx,Ly):
    new_name = {}
    gates = list(circuit["Gate_connects"].keys())
    for i in range(len(gates)):
        new_name[gates[i]] = i
    
    gates_sorted = np.argsort(circuit["Placement"][:,0])
    gates_left = np.array(gates_sorted[:int(len(gates_sorted)/2)])
    gates_right = np.array(gates_sorted[int(len(gates_sorted)/2):])    
    if(part<2):
        QP_left = circuit["Placement"][gates_left]
        gates_left = np.array([list(circuit["Gate_connects"].keys())[i] for i in gates_left])
        left_sorted = np.argsort(QP_left[:,1])
        if(part==0):        #0
            gates = np.array(gates_left[left_sorted[:int(len(gates_left)/2)]])
            pads_new = {}
            gates_new = {}
            nets_new = set()
            for g in gates:
                gates_new[g] = circuit["Gate_connects"][g]
                nets_new = nets_new.union(gates_new[g])
            for n in nets_new:
                for g in circuit["Netlist"][n]:
                    if (g not in gates):
                        if(g not in pads_new.keys()):
                            if(circuit["Placement"][new_name[g],0]<Lx):
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = Lx,Ly
                                else:
                                    x,y = circuit["Placement"][new_name[g],0],Ly
                            else:
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = Lx,circuit["Placement"][new_name[g],1]
                                else:
                                    x,y = Lx,Ly
                            pads_new[g] = [[n],[x,y]]
                        else:
                            pads_new[g][0].append(n)
                if(n in circuit["Padlist"].keys()):
                    for p in circuit["Padlist"][n]:
                        if(p in pads_new.keys()):
                            pads_new[p][0].append(n)
                        else:
                            if(circuit["Pad_connects"][p][1][0]<Lx):
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = circuit["Pad_connects"][p][1][0],circuit["Pad_connects"][p][1][1]
                                else:
                                    x,y = circuit["Pad_connects"][p][1][0],Ly
                            else:
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = Lx,circuit["Pad_connects"][p][1][1]
                                else:
                                    x,y = Lx,Ly
                            pads_new[p] = [[n],[x,y]]
            part = {}
            part["Gate"] = gates
            part["Gate_connects"] = gates_new
            part["Pad_connects"] = pads_new
            return part
        else:               #1
            gates = np.array(gates_left[left_sorted[int(len(gates_left)/2):]])
            pads_new = {}
            gates_new = {}
            nets_new = set()
            for g in gates:
                gates_new[g] = circuit["Gate_connects"][g]
                nets_new = nets_new.union(gates_new[g])
            for n in nets_new:
                for g in circuit["Netlist"][n]:
                    if(g not in gates):
                        if(g not in pads_new.keys()):
                            if(circuit["Placement"][new_name[g],0]<Lx):
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = circuit["Placement"][new_name[g],0],Ly
                                else:
                                    x,y = circuit["Placement"][new_name[g],0],circuit["Placement"][new_name[g],1]
                            else:
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = Lx,Ly
                                else:
                                    x,y = Lx,circuit["Placement"][new_name[g],1]
                            pads_new[g] = [[n],[x,y]]
                        else:
                            pads_new[g][0].append(n)
                if(n in circuit["Padlist"].keys()):
                    for p in circuit["Padlist"][n]:
                        if(p in pads_new.keys()):
                            pads_new[p][0].append(n)
                        else:
                            if(circuit["Pad_connects"][p][1][0]<Lx):
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = circuit["Pad_connects"][p][1][0],Ly
                                else:
                                    x,y = circuit["Pad_connects"][p][1][0],circuit["Pad_connects"][p][1][1]
                            else:
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = Lx,Ly
                                else:
                                    x,y = Lx,circuit["Pad_connects"][p][1][1]
                            pads_new[p] = [[n],[x,y]]
            part = {}
            part["Gate"] = gates
            part["Gate_connects"] = gates_new
            part["Pad_connects"] = pads_new
            return part
    else:
        QP_right = circuit["Placement"][gates_right]
        gates_right = np.array([list(circuit["Gate_connects"].keys())[i] for i in gates_right])
        right_sorted = np.argsort(QP_right[:,1])
        if(part==2):        #2
            gates = np.array(gates_right[right_sorted[:int(len(gates_right)/2)]])
            pads_new = {}
            gates_new = {}
            nets_new = set()
            for g in gates:
                gates_new[g] = circuit["Gate_connects"][g]
                nets_new = nets_new.union(gates_new[g])
            for n in nets_new:
                for g in circuit["Netlist"][n]:
                    if(g not in gates):
                        if(g not in pads_new.keys()):
                            if(circuit["Placement"][new_name[g],0]<Lx):
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = Lx,circuit["Placement"][new_name[g],1]
                                else:
                                    x,y = Lx,Ly
                            else:
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = circuit["Placement"][new_name[g],0],circuit["Placement"][new_name[g],1]
                                else:
                                    x,y = circuit["Placement"][new_name[g],0],Ly
                            pads_new[g] = [[n],[x,y]]
                        else:
                            pads_new[g][0].append(n)
                if(n in circuit["Padlist"].keys()):
                    for p in circuit["Padlist"][n]:
                        if(p in pads_new.keys()):
                            pads_new[p][0].append(n)
                        else:
                            if(circuit["Pad_connects"][p][1][0]<Lx):
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = Lx,circuit["Pad_connects"][p][1][1]
                                else:
                                    x,y = Lx,Ly
                            else:
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = circuit["Pad_connects"][p][1][0],circuit["Pad_connects"][p][1][1]
                                else:
                                    x,y = circuit["Pad_connects"][p][1][0],Ly
                            pads_new[p] = [[n],[x,y]]
            part = {}
            part["Gate"] = gates
            part["Gate_connects"] = gates_new
            part["Pad_connects"] = pads_new
            return part
        else:               #3
            gates = np.array(gates_right[right_sorted[int(len(gates_right)/2):]])
            pads_new = {}
            gates_new = {}
            nets_new = set()
            for g in gates:
                gates_new[g] = circuit["Gate_connects"][g]
                nets_new = nets_new.union(gates_new[g])
            for n in nets_new:
                for g in circuit["Netlist"][n]:
                    if(g not in gates):
                        if(g not in pads_new.keys()):
                            if(circuit["Placement"][new_name[g],0]<Lx):
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = Lx,Ly
                                else:
                                    x,y = Lx,circuit["Placement"][new_name[g],1]
                            else:
                                if(circuit["Placement"][new_name[g],1]<Ly):
                                    x,y = circuit["Placement"][new_name[g],0],Ly
                                else:
                                    x,y = Lx,Ly
                            pads_new[g] = [[n],[x,y]]
                        else:
                            pads_new[g][0].append(n)
                if(n in circuit["Padlist"].keys()):
                    for p in circuit["Padlist"][n]:
                        if(p in pads_new.keys()):
                            pads_new[p][0].append(n)
                        else:
                            if(circuit["Pad_connects"][p][1][0]<Lx):
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = Lx,Ly
                                else:
                                    x,y = Lx,circuit["Pad_connects"][p][1][1]
                            else:
                                if(circuit["Pad_connects"][p][1][1]<Ly):
                                    x,y = circuit["Pad_connects"][p][1][0],Ly
                                else:
                                    x,y = circuit["Pad_connects"][p][1][0],circuit["Pad_connects"][p][1][1]                            
                            pads_new[p] = [[n],[x,y]]
            part = {}
            part["Gate"] = gates
            part["Gate_connects"] = gates_new
            part["Pad_connects"] = pads_new
            return part
    return 0

gln = input("Name of the input file: ")
ckt = open(gln,"r")
ckt = ckt.read().split("\n")
ckt = [ckt[i].split(" ") for i in range(len(ckt))]
G,N = int(ckt[0][0]),int(ckt[0][1])
gate_connects = {}
for i in range(G):
    gate_connects[i+1] = []
    for j in ckt[i+1][2:]:
        if(j):
            gate_connects[i+1].append(int(j))
P = int(ckt[G+1][0])
pad_connects = {}
for i in range(P):
    pad_connects[G+i+1] = [[int(ckt[G+i+2][1])],[int(ckt[G+i+2][2]),int(ckt[G+i+2][3])]]

def place_partition_place(G,P,gate_connects,pad_connects,Lx1,Lx2,Ly1,Ly2):
    # print(str(Lx1)+" "+str(Lx2)+" "+str(Ly1)+" "+str(Ly2)+" ")
    # input()
    if(Lx2-Lx1 < 13):
        circuit = place(G,P,gate_connects,pad_connects)
        return circuit
    else:
        circuit = place(G,P,gate_connects,pad_connects)
        part0 = partition(circuit,0,(Lx1+Lx2)/2,(Ly1+Ly2)/2) 
        circuit0 = place_partition_place(len(part0["Gate"]),len(part0["Pad_connects"].keys()),part0["Gate_connects"],part0["Pad_connects"],Lx1,(Lx1+Lx2)/2,Ly1,(Ly1+Ly2)/2)
        # print("*")
        for i in range(len(circuit0["Placement"])):
            for j in range(len(circuit["Placement"])):
                if(circuit["Placement"][j,2]==circuit0["Placement"][i,2]):
                    circuit["Placement"][j] = circuit0["Placement"][i]
        part1 = partition(circuit,1,(Lx1+Lx2)/2,(Ly1+Ly2)/2)
        circuit1 = place_partition_place(len(part1["Gate"]),len(part1["Pad_connects"].keys()),part1["Gate_connects"],part1["Pad_connects"],Lx1,(Lx1+Lx2)/2,(Ly1+Ly2)/2,Ly2)
        # print("**")
        for i in range(len(circuit1["Placement"])):
            for j in range(len(circuit["Placement"])):
                if(circuit["Placement"][j,2]==circuit1["Placement"][i,2]):
                    circuit["Placement"][j] = circuit1["Placement"][i]
        part2 = partition(circuit,2,(Lx1+Lx2)/2,(Ly1+Ly2)/2)
        circuit2 = place_partition_place(len(part2["Gate"]),len(part2["Pad_connects"].keys()),part2["Gate_connects"],part2["Pad_connects"],(Lx1+Lx2)/2,Lx2,Ly1,(Ly1+Ly2)/2)
        # print("***")
        for i in range(len(circuit2["Placement"])):
            for j in range(len(circuit["Placement"])):
                if(circuit["Placement"][j,2]==circuit2["Placement"][i,2]):
                    circuit["Placement"][j] = circuit2["Placement"][i]
        part3 = partition(circuit,3,(Lx1+Lx2)/2,(Ly1+Ly2)/2)
        circuit3 = place_partition_place(len(part3["Gate"]),len(part3["Pad_connects"].keys()),part3["Gate_connects"],part3["Pad_connects"],(Lx1+Lx2)/2,Lx2,(Ly1+Ly2)/2,Ly2)
        # print("****")
        for i in range(len(circuit3["Placement"])):
            for j in range(len(circuit["Placement"])):
                if(circuit["Placement"][j,2]==circuit3["Placement"][i,2]):
                    circuit["Placement"][j] = circuit3["Placement"][i]
        return circuit
L1 = 0
L2 = 100
circuit = place_partition_place(G,P,gate_connects,pad_connects,L1,L2,L1,L2)
show_placement(circuit["Placement"],circuit["Netlist"],circuit["Pad_connects"],[])

placement = open(gln+"_","w")
QP = np.array([['{:.8f}'.format(round(circuit["Placement"][i,0],8)),'{:.8f}'.format(round(circuit["Placement"][i,1],8))] for i in range(np.size(circuit["Placement"],0))])
for i in range(np.size(QP,0)):
    placement.write(str(i+1)+" "+QP[i,0]+" "+QP[i,1]+"\n")
placement.close()