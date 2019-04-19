def Ivan_func(filename, maxdep,mindep):
    import numpy
    import math
    path = filename
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

    Max_Depth = int(maxdep)
    Min_Depth = int(mindep)



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
    mas = numpy.zeros((num_str,num_clm))
    new_mas = numpy.zeros((num_str,num_clm))
    x = 0
    y = 0
    for i in new_map:
        y = 0
        for j in i.split():
             if j != ' ':
                 mas[x][y] = float(j)
                 new_mas[x][y] = float(j)
                 y+=1
        x+=1
    open_new_map.close()
    bul_mas = numpy.zeros((num_str,num_clm))
    def determinant_i (a):
        if a < 0 or a > num_str-1:
            return 0
        else:
            return 1

    def determinant_j (a):
        if a < 0 or a > num_clm-1:
            return 0
        else:
            return 1

    def check(index,jndex,ind,jnd):
        if mas[index][jndex]<mas[ind][jnd]:
            bul_mas[index][jndex]+=1

    def check_neighbors(index,jndex):
        k = 0
        if determinant_i(index-1):
            check(index,jndex,index-1,jndex)
            k+=1
        # if determinant(index-1) and determinant(jndex+1):
        #     check(index,jndex,index-1,jndex+1)
        #     k+=1
        if determinant_j(jndex+1):
            check(index,jndex,index,jndex+1)
            k+=1
        # if determinant(index+1) and determinant(jndex+1):
        #     check(index,jndex,index+1,jndex+1)
        #     k+=1
        if determinant_i(index+1):
            check(index,jndex,index+1,jndex)
            k+=1
        # if determinant(index+1) and determinant(jndex-1):
        #     check(index,jndex,index+1,jndex-1)
        #     k+=1
        if determinant_j(jndex-1):
            check(index,jndex,index,jndex-1)
            k+=1
        # if determinant(index-1) and determinant(jndex-1):
        #     check(index,jndex,index-1,jndex-1)
        #     k+=1
        return k

    def last_check(i,j):
        tbd = check_neighbors(i,j)
        if tbd==2:
            if bul_mas[i][j] == 2:
                mas[i][j]+=0.25
        if tbd==3:
            if bul_mas[i][j] == 3:
                mas[i][j]+=0.25
        if tbd==4:
            if bul_mas[i][j]>=3:
                mas[i][j]+=0.25
        return tbd

    def launch(i,j):
        flag = 1
        while (flag):
            flag = 0
            bul_mas[i][j] = 0
            tbd = mas[i][j]
            last_check(i, j)
            if tbd != mas[i][j]:
                flag = 1
                if determinant_i(i - 1):
                    launch(i - 1, j)
                if determinant_j(j + 1):
                    launch(i, j + 1)
                if determinant_i(i + 1):
                    launch(i + 1, j)
                if determinant_j(j - 1):
                    launch(i, j - 1)

    for i in range(num_str-1):
        for j in range(num_clm-1):
            launch(i,j)

    spisok_border = [];

    for i in range(num_str):
        for j in range(num_clm):
            open_path_1_1.write(str(mas[i][j]) + '\t')
        open_path_1_1.write('\n')
    open_path_1_1.close()

    def circle(i,j):
        sum_X=0
        sum_Y=0
        N=0
        spisok = [i,j]
        tohka = mas[i][j]
        while(len(spisok)>0):
            y = spisok.pop()
            x = spisok.pop()
            while(mas[x][y]==tohka):
                y-=1
            y+=1
            spisok_border.append(x)
            spisok_border.append(y)
            spanUp = 0
            spanDown = 0
            while(mas[x][y]==tohka):
                sum_X+=x
                sum_Y+=y
                N+=1
                if spanUp==0 and mas[x-1][y] == tohka:
                    spisok.append(x-1)
                    spisok.append(y)
                    spanUp=1
                else:
                    if spanUp==1 and mas[x-1][y] !=tohka:
                        spanUp = 0
                if spanDown==0 and mas[x+1][y]==tohka:
                    spisok.append(x+1)
                    spisok.append(y)
                    spanDown=1
                else:
                    if spanDown==1 and mas[x+1][y]!=tohka:
                        spanDown=0
                mas[x][y]+=tohka
                y+=1
            spisok_border.append(x)
            spisok_border.append(y-1)
        middle_x = int(sum_X/N)
        middle_y = int(sum_Y/N)
        print(sum_X,sum_Y,N)
        Radius = 0
        while(len(spisok_border)>0):
            y = spisok_border.pop()
            x = spisok_border.pop()
            Rad = math.sqrt((middle_x-x)*(middle_x-x)+(middle_y-y)*(middle_y-y))
            if Rad>Radius:
                Radius=Rad
        Radius=int(Radius)+2
        return (middle_x, middle_y, Radius)
        print(middle_x, middle_y, Radius)

    Circle_array = list()
    for i in range(num_str):
        for j in range(num_clm):
            if mas[i][j]==1 or mas[i][j]==0.75:
                Circle_array.append(circle(i,j))
