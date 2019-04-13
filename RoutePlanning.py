import numpy
import scipy.optimize as opt
from enum import Enum
import Graph

class Direction(Enum):
    CONTERCW = 1
    CLOCKWISE = 2

class Arc():
    def __init__(self, X0, Y0, R, A1, A2, DIR):
        super().__init__()
        self.x0 = X0
        self.y0 = Y0
        self.r = R
        self.a1 = A1
        self.a2 = A2
        self.dir = DIR


def roundDistance(a1, a2):
    d = abs(a1 - a2)
    if d > numpy.pi:
        d = 2*numpy.pi - d
    return  d

# This function walk along the way and skew way if it cross with red zone rounds
# In such moment they call function that fix route
def clarifyRoute(route, round_array):
    num_of_clarify = 0
    previous_arc = route[0]
    arc_number = 0
    for arc in route:
        line = (previous_arc.x0+previous_arc.r*numpy.cos(previous_arc.a2), previous_arc.y0+previous_arc.r*numpy.sin(previous_arc.a2), arc.x0+arc.r*numpy.cos(arc.a2), arc.y0+arc.r*numpy.sin(arc.a2))
        for round in round_array:
            cross = False
            # Looks if this round is edge of line
            if previous_arc.x0 == round[0] and previous_arc.y0 == round[1] and previous_arc.r == round[2] or arc.x0 == round[0] and arc.y0 == round[1] and arc.r == round[2]:
                # print("{} have edge at {}. So their cross is {}.".format(line, round, cross))
                continue
            # Looks if round and route_line can cross  //by square
            if line[2]<round[0]-round[2] and line[0]<round[0]-round[2] or\
                    line[2]>round[0]+round[2] and line[0]>round[0]+round[2] or\
                    line[3]<round[1]-round[2] and line[1]<round[1]-round[2] or\
                    line[3]>round[1]+round[2] and line[1]>round[1]+round[2]:
                # print("{} and {} can't cross. So their cross is {}.".format(line, round, cross))
                continue
            # Finding the distance between route_line and center of round
            distance = abs((line[3] - line[1])*round[0] - (line[2] - line[0])*round[1] + line[2]*line[1] - line[3]*line[0])/((line[3] - line[1])**2 + (line[2] - line[0])**2)**(1/2)

            # Looks if route_line cross round or not
            if distance>=round[2]:
                # print("distance from {} to {} is {}. So their cross is {}.".format(line, round, distance, cross))
                continue
            # Looks where route_line intersect round and if this point is in interval
            solution = opt.fsolve(lambda var: [(var[0]-round[0])**2+((var[1]-round[1])**2) - round[2]**2, (var[0]-line[0])*(line[3]-line[1])-(var[1]-line[1])*(line[2]-line[0])], [0,0])

            if solution[0]>=line[0] and solution[0]>=line[2] or\
                    solution[0]<=line[0] and solution[0]<=line[2] or\
                    solution[1]>=line[1] and solution[1]>=line[3] or\
                    solution[1]<=line[1] and solution[1]<=line[3]:
                # print("{} and {} don't cross (from system) and their cross is {}.".format(line, round, cross))
                continue

            cross = True
            # print("{} and {} cross. Their cross is {}.".format(line, round, cross))

            # if round[2] < (arc.x0 - round[0])**2 + (arc.y0 - round[1])**2 or arc.r < (arc.x0 - round[0])**2 + (arc.y0 - round[1])**2:
            if (round[0] - line[0])/(line[2]-line[0])-(round[1] - line[1])/(line[3]-line[1])<0:
                start_angle = numpy.pi/2*3
            else:
                start_angle = numpy.pi/2
            new_arc = Arc(round[0], round[1], round[2], start_angle, start_angle, Direction.CLOCKWISE)

            a_begin, a_end =createCompound(previous_arc, new_arc)
            previous_arc.a2 = a_begin
            new_arc.a1 = a_end

            a_begin, a_end = createCompound(new_arc, arc)
            arc.a1 = a_end
            new_arc.a2 = a_begin

            route.insert(arc_number,new_arc)
            arc = new_arc
            num_of_clarify = num_of_clarify + 1
            break

        previous_arc = arc
        arc_number = arc_number + 1
        # previous_point = point
    return num_of_clarify

def createCompound(arc1, arc2):
    # find parameters of equivalent construction task with a single round and a point
    if arc1.r>arc2.r:
        x0_external = arc1.x0
        y0_external = arc1.y0
        r_external = arc1.r - arc2.r
        x_external, y_external = arc2.x0, arc2.y0
    else:
        x0_external = arc2.x0
        y0_external = arc2.y0
        r_external = arc2.r - arc1.r
        x_external, y_external = arc1.x0, arc1.y0
    # find angles of point of contact of a circle and an external tangent
    a1_external, a2_external = createTangent(x_external, y_external, x0_external, y0_external, r_external) # External tangent

    if arc1.r + arc2.r < numpy.sqrt((arc1.x0 - arc2.x0)**2 + (arc1.y0 - arc2.y0)**2):
        # find angle for second round of point of contact of a circle and an internal tangent. For that angle of point for first round you can do: a + 180
        a1_internal, a2_internal = createTangent(arc1.x0, arc1.y0, arc2.x0, arc2.y0, arc1.r + arc2.r)  # Internal tangent
    else:
        a1_internal, a2_internal = numpy.nan, numpy.nan
    # print("a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}".format(a1_external, a2_external, a1_internal, a2_internal))

    # Choose suitable tangent
    if roundDistance(a1_external, arc1.a2) < roundDistance(a2_external, arc1.a2):
        a_external = a1_external
    else:
        a_external = a2_external
    # print("a_ext = {}".format(a_external))
    if roundDistance((a1_internal + numpy.pi)%(numpy.pi*2), arc1.a2) < roundDistance((a2_internal + numpy.pi)%(numpy.pi*2), arc1.a2):
        a_internal = a1_internal
    else:
        a_internal = a2_internal
    # print("a_int = {}".format(a_internal))

    if roundDistance(a_internal, arc2.a1) < roundDistance(a_external, arc2.a1):
        a2 = a_internal
        a1 = (a_internal + numpy.pi)%(numpy.pi*2)
    else:
        a2 = a_external
        a1 = a_external

    return a1, a2

# find angle of point of contact of round and tangent where tangent goes through the point A(XA, YA)
def createTangent(XA, YA, X0, Y0, R):
    # P = opt.fsolve(lambda var: [(var[0]-X0)**2+((var[1]-Y0)**2) - R**2, (var[0]-XA)*(Y0-YA)-(var[1]-YA)*(X0-XA)], [XA,YA])
    # # if not (P[0]<XA and P[0]>X0 or P[0]>XA and P[0]<X0) and (P[1]<YA and P[1]>Y0 or P[1]>YA and P[1]<Y0):
    # # print(P)
    # M = opt.fsolve(lambda var: [(var[0]-X0)**2+((var[1]-Y0)**2) - ((X0-XA)**2 + (Y0-YA)**2), (var[0]-P[0])*(X0-XA)+(var[1]-P[1])*(Y0-YA)], [XA,YA])
    # # print(M)
    # H = opt.fsolve(lambda var: [(var[0]-X0)**2+((var[1]-Y0)**2) - R**2, (var[0]-M[0])*(Y0-M[1])+(var[1]-M[1])*(X0-M[0])], [M[0],M[1]])
    # tana = (H[0]-X0)/(H[1]-Y0)
    # a = numpy.arctan(tana)
    cosa = R/numpy.sqrt((X0-XA)**2 + (Y0-YA)**2)
    # print("cos a = {}".format(cosa))
    if XA-X0 == 0:
        tanb = numpy.inf
    else:
        tanb = (YA-Y0)/(XA-X0)
    # print("tan b = {}".format(tanb))
    b = numpy.arctan(tanb)
    # print(b)
    if XA-X0<0:
        b = b + numpy.pi
    if XA-X0==0 and XA-X0<0:
        b = b + numpy.pi
    # print("b = {}".format(b))
    a = numpy.arccos(cosa)
    # print("a = {}".format(a))
    return (b+a)%(numpy.pi*2), (b-a)%(numpy.pi*2)


def CreateRoute(startX, startY, endX, endY, width, height, red_zone):
    pointed_route = list()
    pointed_route.append(Arc(startX, startY, 0, 0, 0, Direction.CONTERCW))
    pointed_route.append(Arc(endX, endY, 0, 0, 0, Direction.CONTERCW))

    clarifyRoute(pointed_route, red_zone)


if __name__ == "__main__":
    # read = open("G:\Maps\Single_map.txt", "a")
    # for i in range(600):
    #     for j in range(600):
    #         read.write((str)((int)(1)))
    #         if j < 599:
    #             read.write("\t")
    #     if i < 599:
    #         read.write("\n")
    # read.close()

    # CreateRoute(0, 0, 100, 100, 100, 100, [(5,25,2),(50,20,25),(60,3,50)])
    # clarifyRoute([(0,0,10,10),(11,10,16,29),(16,30,51,30),(50,40,70,70),(73,73,86,86),(86,86,86,100), (86,100,100,100)], [(5,25,10),(50,20,25),(60,3,50),(80, 65, 8),(90,85,4.5)])
    route = [Arc(0,0,0,0,0,Direction.CONTERCW),Arc(599,550,0,0,0,Direction.CONTERCW)]
    rounds = [(85,80,6), (15, 16, 9), (50, 0, 8), (60, 62, 4), (200, 100, 85), (400, 360, 76), (500, 100, 50), (560, 540, 15), (380, 350, 6)]
    n = 1
    while n>0:
        n = clarifyRoute(route, rounds)
        # print("-----------------------------------------------")
        # for i in route:
        #     print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}".format(i.x0, i.y0, i.r, i.a1, i.a2))
        # print("-----------------------------------------------")

    Graph.full_map_conjunction()
    for i in rounds:
        Graph.circle_draw(i[0], i[1], i[2])
    i_pr = route[0]
    for i in route:
        Graph.draw_line((int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)), (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)), (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)), (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1)))
        i_pr = i
    # print(createTangent(0,0,10,10,10))
    # arc1 = Arc(0,0,5,0,numpy.pi/3*2,Direction.CLOCKWISE)
    # arc2 = Arc(10,15,15,numpy.pi/2,0,Direction.CLOCKWISE)
    # print(createCompound(arc1, arc2))
    # print(numpy.nan > 0)
    # print(numpy.nan > 100)
    # print(numpy.nan < 0)
    # print(numpy.nan < 100)
    # print(numpy.nan > numpy.nan)
    # print(numpy.nan < numpy.nan)
    # print(numpy.nan == numpy.nan)
    # print(0 > numpy.nan)
    # print(100 > numpy.nan)
    # print(0 < numpy.nan)
    # print(100 < numpy.nan)
    # print(numpy.nan + 100)
    # print(numpy.nan + 100 > 120)
    # print(numpy.nan + 100 > 0)
