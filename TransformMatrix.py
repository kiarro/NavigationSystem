import numpy

path = 'map.txt'
new_path = 'map1.txt'
path_1_1 = 'map_1_1.txt'
open_map = open(path, 'r')
open_new_map = open(new_path, 'w+')
open_path_1_1 = open(path_1_1,'w')
map = open_map.readlines()
open_new_map.truncate()
open_path_1_1.truncate()
new_map = open_new_map.readlines()

num_str = 0
num_clm = 0

Max_Depth = 500
Min_Depth = 100



def Warnings(Current_Depth):
    W = (Max_Depth - Current_Depth) / (Max_Depth - Min_Depth)
    if W > 1:
        W = 1
    if W < 0:
        W = 0
    return W


def Klass(tbd):
    if tbd == 0:
        return 0
    if tbd > 0 and tbd <= 0.25:
        return 0.25
    if tbd > 0.25 and tbd <= 0.50:
        return 0.5
    if tbd > 0.50 and tbd <= 0.75:
        return 0.75
    if tbd > 0.75 and tbd <= 1.00:
        return 1

num_str = len(map)
for i in map:
    kol = 0
    for j in i.split():
        if j.isnumeric():
            Current_Depth = int(j)
            tbd = Warnings(Current_Depth)
            open_new_map.write(str(Klass(tbd)) + '\t')
            kol+=1
    open_new_map.write('\n')
    if (kol>num_clm):
        num_clm = kol
open_map.close()
open_new_map.close()

open_new_map = open(new_path,"r")
new_map = open_new_map.readlines()
mas = numpy.zeros((num_str+1,num_clm))
x = 0
y = 0
for i in new_map:
    y = 0
    for j in i.split():
         if j != ' ':
             mas[x][y] = float(j)
             # print(j)
             y+=1
    x+=1
open_new_map.close()
# for i in range(num_str):
#     for j in range(num_clm):
def Rekyrs(index,jndex):
    if index == num_str-1 and jndex == 0:
        if mas[num_str-1][0] < mas[num_str-1][1] and mas[num_str-1][0]<mas[num_str-2][0]:
            mas[num_str-1][0]+=0.25
    if index == num_str-1 and jndex !=0:
        if mas[num_str-1][jndex]<mas[num_str][jndex-1] and mas[num_str-1][jndex]<mas[num_str][jndex+1]:
            mas[num_str-1][jndex]+=0.25
    if index == 0 and jndex == num_clm-1:
        if mas[0][num_clm-1] < mas[0][jndex - 2] and mas[0][num_clm-1] < mas[1][num_clm-1]:
            mas[0][num_clm-1]+=0.25
    if index != 0 and jndex == num_clm-1:
        if mas[index][num_clm-1]<mas[index-1][num_clm-1] and mas[index][num_clm-1]<mas[index+1][num_clm-1]:
            mas[index][num_clm-1]+=0.25
    else:
        if mas[index][jndex]<mas[index+1][jndex] and mas[index][jndex] < mas[index][jndex+1]:
            mas[index][jndex]+=0.25
    if index<num_str-1:
        Rekyrs(index+1,jndex)
    if jndex<num_clm-1:
        Rekyrs(index,jndex+1)
    return 0
Rekyrs(0,0)

for i in range(num_str):
    for j in range(num_clm):
        open_path_1_1.write(str(mas[i][j]) + '\t')
    open_path_1_1.write('\n')
open_path_1_1.close()