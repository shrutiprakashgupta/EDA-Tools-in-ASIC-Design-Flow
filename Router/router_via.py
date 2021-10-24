# Router considering via penalty
import numpy as np
import heapq

g = open("bench1.grid","r")
g = g.read().split("\n")
g = [g[i].split(" ") for i in range(len(g))]
x_size,y_size,b_penalty,v_penalty = int(g[0][0]),int(g[0][1]),int(g[0][2]),int(g[0][3])
grid = np.zeros((y_size,x_size,2),dtype=int)
for i in range(y_size):
    grid[i,:,0] = [int(g[i+1][j]) for j in range(len(g[i+1])) if(g[i+1][j])]
    grid[i,:,1] = [int(g[y_size+i+1][j]) for j in range(len(g[y_size+i+1])) if(g[y_size+i+1][j])]
grid = np.transpose(grid,(1,0,2))

print("The grid is: \n")
print(grid[:,:,0])
print(grid[:,:,1])
input()

n = open("bench1.nl","r")
n = n.read().split("\n")
n = [n[i].split(" ") for i in range(len(n))]
w = int(n[0][0])
pins = np.zeros((w,7),dtype=int)
for i in range(w):
    pins[i] = [int(n[i+1][j]) for j in range(len(n[i+1])) if(n[i+1][j])]

print("The pins (ends of wires to be routed) are: \n")
print(pins)
input()

def route(pins,grid,X,Y,b_penalty,v_penalty):
    # 1:left 2:right 3:up 4:down 5:above 6:bottom 0:null
    # pathcost layer x y
    src = (1,pins[1],pins[2],pins[3])

    # pathcost initialized to 0 for target
    trg = (0,pins[4],pins[5],pins[6])
    
    #Wavefront, initialized with src
    wavefront = []
    heapq.heappush(wavefront,src)
    curr = src

    #predecessor 
    pred = np.zeros((np.size(grid,0),np.size(grid,1),np.size(grid,2)),dtype=int)

    # Pointer to the predecessor (l,y,x) to be subtracted
    pred_ptr = {1:[0,0,1],2:[0,0,-1],3:[0,1,0],4:[0,-1,0],5:[-1,0,0],6:[1,0,0]}

    while(curr[1:]!=trg[1:]):
        if(wavefront == []):
            return 0
        else:
            curr = heapq.heappop(wavefront)
            if(curr[1:]==trg[1:]):
                path = list([])
                while(curr[1:]!=src[1:]):
                    path.insert(0,(curr[1],curr[2],curr[3]))
                    del_l,del_x,del_y = pred_ptr[pred[curr[2],curr[3],curr[1]-1]]
                    curr = (0,curr[1]-del_l,curr[2]-del_x,curr[3]-del_y)
                path.insert(0,src[1:])
                return path
            else:
                l,x,y = curr[1]-1,curr[2],curr[3]
                grid[x,y,l] = -1
                if(x < X-1):
                    if(grid[x+1,y,l]!=-1):
                        heapq.heappush(wavefront,(curr[0]+grid[x+1,y,l],l+1,x+1,y))
                        grid[x+1,y,l] = -1
                        pred[x+1,y,l] = 3
                if(y > 0):
                    if(grid[x,y-1,l]!=-1):
                        heapq.heappush(wavefront,(curr[0]+grid[x,y-1,l],l+1,x,y-1))
                        grid[x,y-1,l] = -1
                        pred[x,y-1,l] = 2
                if(x > 0):
                    if(grid[x-1,y,l]!=-1):
                        heapq.heappush(wavefront,(curr[0]+grid[x-1,y,l],l+1,x-1,y))
                        grid[x-1,y,l] = -1
                        pred[x-1,y,l] = 4
                if(y < Y-1):
                    if(grid[x,y+1,l]!=-1):
                        heapq.heappush(wavefront,(curr[0]+grid[x,y+1,l],l+1,x,y+1))
                        grid[x,y+1,l] = -1
                        pred[x,y+1,l] = 1
                if(l==0):
                    if(grid[x,y,l+1]!=-1):
                        heapq.heappush(wavefront,(curr[0]+v_penalty+grid[x,y,l+1],l+2,x,y))
                        grid[x,y,l+1] = -1
                        pred[x,y,l+1] = 6
                if(l==1):
                    if(grid[x,y,l-1]!=-1):
                        heapq.heappush(wavefront,(curr[0]+v_penalty+grid[x,y,l-1],l,x,y))
                        grid[x,y,l-1] = -1
                        pred[x,y,l-1] = 5
    return 0

routed = open("bench1","w")
routed.write(str(w)+"\n")

for i in range(w):
    w_route = route(pins[i],np.copy(grid),x_size,y_size,b_penalty,v_penalty)
    routed.write(str(i+1)+"\n")
    if(w_route==0):
        routed.write(str(0)+"\n")
    else:
        for j in range(len(w_route)-1):
            routed.write(str(w_route[j][0])+" "+str(w_route[j][1])+" "+str(w_route[j][2])+"\n")
            grid[w_route[j][1],w_route[j][2],w_route[j][0]-1] = -1
            if(w_route[j][0]!=w_route[j+1][0]):
                routed.write("3 "+str(w_route[j][1])+" "+str(w_route[j][2])+"\n")
        routed.write(str(pins[i][4])+" "+str(pins[i][5])+" "+str(pins[i][6])+"\n")
        routed.write("0 \n")
    print("Completed route "+str(i+1))
    input()
