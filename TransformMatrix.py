def Ivan_func(filename, maxdep,mindep):

    import numpy

    path = filename
    new_path = 'DepthDangerZone.txt'
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
    bul_mas = numpy.zeros((num_str,num_clm))
    new_mas = mas
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


    for i in range(num_str):
        for j in range(num_clm):
            open_path_1_1.write(str(mas[i][j]) + '\t')
        open_path_1_1.write('\n')
    open_path_1_1.close()

    return 0