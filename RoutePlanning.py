# angles are deposited clockwise from the direction right??

# always: CCW - CW < 180 < CW - CCW

import numpy
import scipy.optimize as opt
from enum import Enum
import Graph
import copy

eps = 0.0001

is_log_on = False

class Direction(Enum):
    CONTERCW = 1
    CLOCKWISE = 2

class MainPointInBadZoneError(Exception):
    def __init__(self, text):
        self.txt = text

class RoutePlanSoftError(Exception):
    pass

class Tree():
    def __init__(self, this, left, right, parent=None):
        self.left = left
        self.right = right
        self.value = this
        self.parent = parent

    def isInTreeBefore(self, element):
        thisBranch = self
        # while not in root
        while not (thisBranch.parent == None):
            thisBranch = thisBranch.parent
            if thisBranch.isValueEqualTo(element):
                return True
        return False

    def isValueEqualTo(self, element):
        if (not len(self.value) == len(element)):
            return  False
        for i in range(len(self.value)):
            if (not self.value[i] == element[i]):
                return False
        return True

class GraphRoundVertex():
    def __init__(self, this, links):
        self.vertex = this
        self.links = links # [(vertex, distance, this angle)]

class Arc():
    def __init__(self, X0, Y0, R, A1, A2, DIR):
        super().__init__()
        self.x0 = X0
        self.y0 = Y0
        self.r = R
        self.a1 = A1
        self.a2 = A2
        self.dir = DIR

    def __eq__(self, other):
        return self.x0 == other.x0 and self.y0 == other.y0 and self.a1 == other.a1 and self.a2 == other.a2 and self.r == other.r and self.dir == other.dir

# find angle between two points at circle
def roundDistance(a1, a2):
    d = abs(a1 - a2)
    if d > numpy.pi:
        d = 2*numpy.pi - d
    return  d

def round2Str(round):
    return "{}-{}".format(int(round[0]), int(round[1]))

def str2Round(str, rounds):
    a = str.split("-")
    x = int(a[0])
    y = int(a[1])
    for i in rounds:
        if x == int(i[0]) and y == int(i[1]):
            return i
    print("Error in str2Round")
    return numpy.inf

# this function work only in clockwise direction
def isArcsCrossed(a1_1, a1_2, a2_1, a2_2): # input vars are numbers
    if a1_1 == numpy.inf or a1_2 == numpy.inf or a2_1 == numpy.inf or a2_2 == numpy.inf or a1_1 == None or a1_2 == None or a2_1 == None or a2_2 == None:
        return False
    a1_2 = (a1_2 - a1_1) % (numpy.pi * 2)
    a2_1 = (a2_1 - a1_1) % (numpy.pi * 2)
    a2_2 = (a2_2 - a1_1) % (numpy.pi * 2)
    a1_1 = 0
    if (a2_1 < a1_2):
        return True
    if (a2_2 < a1_2):
        return True
    if (a2_2 < a2_1):
        return True
    return False

def normalizeRounds(rounds):
    # list of rounds must be sorted
    # _ = list()
    n = len(rounds)
    i = 0
    while i < n-1:
        j = i + 1
        # _[i] = False
        while j < n:
            # if i == j:
            #     continue
            r = numpy.sqrt((rounds[i][0]-rounds[j][0])**2+(rounds[i][1]-rounds[j][1])**2)
            dr = abs(rounds[i][2]-rounds[j][2])
            if r<=dr:
                # _[j] = True
                # print("{}-{}".format(rounds[i],rounds[j]))
                rounds.pop(j)
                j -= 1
                n -= 1
            j += 1
        i += 1
        # if (_[i]):
        #     rounds.pop(i)
    return rounds

def distanceBetweenRoundPoits(round1, a1, round2, a2):
    x1 = round1[0] + numpy.sin(a1) * round1[2]
    y1 = round1[1] + numpy.cos(a1) * round1[2]
    x2 = round2[0] + numpy.sin(a2) * round2[2]
    y2 = round2[1] + numpy.cos(a2) * round2[2]
    d = numpy.sqrt((x1-x2)**2+(y1-y2)**2)
    return d

def lenthOfArc(r, a1, a2):
    return ((a2 - a1)%(2*numpy.pi))*r

def lookRoundsIntersections(rounds):
    global intersections
    intersections = dict()
    for i in rounds:
        intersections[round2Str(i)] = dict();
    n = len(rounds)
    for round1 in rounds:
        # intersections[round1] = dict()
        for round2 in rounds:
            r = numpy.sqrt((round1[0]-round2[0])**2+(round1[1]-round2[1])**2)
            if (r > round1[2]+round2[2] or round1==round2):
                continue
            cosa = (r**2+round1[2]**2-round2[2]**2) / 2 / r / round1[2]
            cosb = (r**2-round1[2]**2+round2[2]**2) / 2 / r / round2[2]
            if abs(cosa) < 1: a = numpy.arccos(cosa)
            else: a = 0
            if abs(cosb) < 1: b = numpy.arccos(cosb)
            else: b = 0
            if round1[0] == round2[0]:
                if round1[1] < round2[1]:
                    alpha = numpy.pi/2
                else:
                    alpha = numpy.pi/2*3
            else:
                tana = (round1[1]-round2[1])/(round1[0]-round2[0])
                alpha = numpy.arctan(tana)
                if (round1[0] > round2[0]):
                    alpha += numpy.pi
            alpha = alpha%(2*numpy.pi)
            intersections[round2Str(round1)][round2Str(round2)] = ((alpha-a)%(2*numpy.pi), (alpha+a)%(2*numpy.pi))
            intersections[round2Str(round2)][round2Str(round1)] = ((alpha+numpy.pi-b)%(2*numpy.pi), (alpha+numpy.pi+b)%(2*numpy.pi))
    for i in rounds:
        if (intersections[round2Str(i)]=={}):
            intersections.pop(round2Str(i))
            continue
        # for j in rounds:
        #     if (intersections[round2Str(i)][round2Str(j)]=={}):
        #         intersections[round2Str(i)].pop(round2Str(j))
    return intersections

# reurns string
def whereClosedByRoundsIntersection(arc):
    global intersections
    round = (arc.x0, arc.y0, arc.r)
    if (not round2Str(round) in intersections):
        return None
    if arc.dir == Direction.CONTERCW:
        a1, a2 = arc.a2, arc.a1
    else:
        a1, a2 = arc.a1, arc.a2
    for i in intersections[round2Str(round)]:
        cross_a1, cross_a2 = intersections[round2Str(round)].get(i)
        if isArcsCrossed(a1, a2, cross_a1, cross_a2):
            return i
    return None

# looks if they are crossed
def isCrossed(line, round):
    cross = False
    # Looks if round and route_line can cross  //by square
    if line[2] < round[0] - round[2] and line[0] < round[0] - round[2] or \
            line[2] > round[0] + round[2] and line[0] > round[0] + round[2] or \
            line[3] < round[1] - round[2] and line[1] < round[1] - round[2] or \
            line[3] > round[1] + round[2] and line[1] > round[1] + round[2]:
        # print("{} and {} can't cross. So their cross is {}.".format(line, round, cross))
        return False
    # Finding the distance between route_line and center of round
    distance = abs(
        (line[3] - line[1]) * round[0] - (line[2] - line[0]) * round[1] + line[2] * line[1] - line[3] * line[0]) / (
                           (line[3] - line[1]) ** 2 + (line[2] - line[0]) ** 2) ** (1 / 2)

    # Looks if route_line cross round or not
    if distance >= round[2]:
        # print("distance from {} to {} is {}. So their cross is {}.".format(line, round, distance, cross))
        return False
    # Looks where route_line intersect round and if this point is in interval
    solution = opt.fsolve(lambda var: [(var[0] - round[0]) ** 2 + ((var[1] - round[1]) ** 2) - round[2] ** 2,
                                       (var[0] - line[0]) * (line[3] - line[1]) - (var[1] - line[1]) * (
                                                   line[2] - line[0])], [round[0]+round[2], round[1]])

    if solution[0] >= line[0] and solution[0] >= line[2] or \
            solution[0] <= line[0] and solution[0] <= line[2] or \
            solution[1] >= line[1] and solution[1] >= line[3] or \
            solution[1] <= line[1] and solution[1] <= line[3]:
        # print("{} and {} don't cross (from system) and their cross is {}.".format(line, round, cross))
        return False

    # They are cross
    return True

# This function walk along the way and skew way if it cross with red zone rounds
# In such moment they call function that fix route
def clarifyRoute(route, round_array):
    num_of_clarify = 0
    previous_arc = route[0]
    arc_number = 0
    for arc in route:
        # delete extra point of route
        try:
            if arc_number>0 and arc_number<len(route)-1:
                if previous_arc.x0 == arc.x0 and previous_arc.y0 == arc.y0 and previous_arc.r == arc.r:
                    previous_arc.a2 = arc.a2
                    raise RoutePlanSoftError

                a_1, a_2, d_1, d_2 = createCompound(route[arc_number-1], route[arc_number+1])
                # print("---------------------------------------------------------------------------------")
                # print("round 1 = {}, round 2 = {}, angle 1 = {}, angle 2 = {}".format([route[arc_number-1].x0, route[arc_number-1].y0, route[arc_number-1].r], [route[arc_number+1].x0, route[arc_number+1].y0, route[arc_number+1].r], a_1*180/numpy.pi, a_2*180/numpy.pi))
                line = (route[arc_number-1].x0 + route[arc_number-1].r * numpy.cos(a_1),
                        route[arc_number-1].y0 + route[arc_number-1].r * numpy.sin(a_1), route[arc_number+1].x0 + route[arc_number+1].r * numpy.cos(a_2),
                        route[arc_number+1].y0 + route[arc_number+1].r * numpy.sin(a_2))
                if not isCrossed(line, [route[arc_number].x0, route[arc_number].y0, route[arc_number].r]):
                    route[arc_number - 1].a2 = a_1
                    route[arc_number + 1].a1 = a_2
                    # print("--")
                    # return num_of_clarify
                    raise RoutePlanSoftError
        except RoutePlanSoftError:
            route.pop(arc_number)
            num_of_clarify += 1

        if not (previous_arc.a2 == arc.a1 or previous_arc.a2 == (arc.a1 + numpy.pi)%(numpy.pi*2)):
            # print("{}, {}, {}, {} - {}, {}, {}, {}".format(previous_arc.x0, previous_arc.y0, previous_arc.r, previous_arc.a2, arc.x0, arc.y0, arc.r, arc.a1))
            a_1, a_2, d1, d2 = createCompound(previous_arc, arc)
            previous_arc.a2 = a_1
            arc.a1 = a_2

        # look if arc closed by rounds intersection
        enemy = whereClosedByRoundsIntersection(arc)
        if not (enemy == None):
            previous_arc = arc
            arc_number = arc_number + 1
            continue
        enemy = whereClosedByRoundsIntersection(previous_arc)
        if not (enemy == None):
            enemy = str2Round(enemy, round_array)
            previous_arc.a2 = previous_arc.a1
            new_arc = Arc(enemy[0], enemy[1], enemy[2], previous_arc.a1, previous_arc.a2, Direction.CLOCKWISE)

            a_begin, a_end, direction1, direction2 = createCompound(previous_arc, new_arc)
            previous_arc.a2 = a_begin
            new_arc.a1 = a_end
            new_arc.a2 = a_end
            previous_arc.dir = direction1
            new_arc.dir = direction2

            a_begin, a_end, direction1, direction2 = createCompound(new_arc, arc)
            new_arc.a2 = a_begin
            arc.a1 = a_end
            new_arc.dir = direction1
            arc.dir = direction2

            route.insert(arc_number, new_arc)
            # print("x = {}, y = {} was added".format(new_arc.x0, new_arc.y0))
            arc = new_arc
            num_of_clarify = num_of_clarify + 1
            break

        line = (previous_arc.x0+previous_arc.r*numpy.cos(previous_arc.a2), previous_arc.y0+previous_arc.r*numpy.sin(previous_arc.a2), arc.x0+arc.r*numpy.cos(arc.a1), arc.y0+arc.r*numpy.sin(arc.a1))
        for round in round_array:
            # Looks if this round is edge of line
            if previous_arc.x0 == round[0] and previous_arc.y0 == round[1] and previous_arc.r == round[2]:
                continue
            if arc.x0 == round[0] and arc.y0 == round[1] and arc.r == round[2]:
                continue
            if not isCrossed(line, round):
                continue
            # find start angle
            # if round[2] < (arc.x0 - round[0])**2 + (arc.y0 - round[1])**2 or arc.r < (arc.x0 - round[0])**2 + (arc.y0 - round[1])**2:
            if (round[0] - line[0])/(line[2]-line[0])-(round[1] - line[1])/(line[3]-line[1])<0:
                start_angle = numpy.pi/2*3
            else:
                start_angle = numpy.pi/2
            new_arc = Arc(round[0], round[1], round[2], start_angle, start_angle, Direction.CLOCKWISE)

            # construct tangent
            a_begin, a_end, direction1, direction2 = createCompound(previous_arc, new_arc)
            previous_arc.a2 = a_begin
            new_arc.a1 = a_end
            new_arc.a2 = a_end
            previous_arc.dir = direction1
            new_arc.dir = direction2

            a_begin, a_end, direction1, direction2 = createCompound(new_arc, arc)
            new_arc.a2 = a_begin
            arc.a1 = a_end
            new_arc.dir = direction1
            arc.dir = direction2

            route.insert(arc_number,new_arc)
            # print("x = {}, y = {} was added".format(new_arc.x0, new_arc.y0))
            arc = new_arc
            num_of_clarify = num_of_clarify + 1
            break

        previous_arc = arc
        arc_number = arc_number + 1
        # previous_point = point
    route[0].a1 = route[0].a2
    route[len(route)-1].a2 = route[len(route)-1].a1
    return num_of_clarify

# This function walk along the way and skew way if it cross with red zone rounds
# In such moment they call function that fix route
def clarifyRouteWithTree(route, rounds):
    num_of_clarify = 0
    previous_arc = route[0]
    arc_number = 0

    # Not work
    # route1 = route.copy()
    # route2 = route.copy()
    # route1 = list(route)
    # route2 = list(route)
    route1 = copy.deepcopy(route)
    route2 = copy.deepcopy(route)

    for arc in route:
        if arc == previous_arc and arc_number==0:
            previous_arc = arc
            arc_number = arc_number + 1
            continue
        # delete extra point of route
        try:
            if arc_number>0 and arc_number<len(route)-1:
                if previous_arc.x0 == arc.x0 and previous_arc.y0 == arc.y0 and previous_arc.r == arc.r:
                    previous_arc.a2 = arc.a2
                    raise RoutePlanSoftError

                a_1, a_2, d_1, d_2 = createCompound(route[arc_number-1], route[arc_number+1])
                # print("---------------------------------------------------------------------------------")
                # print("round 1 = {}, round 2 = {}, angle 1 = {}, angle 2 = {}".format([route[arc_number-1].x0, route[arc_number-1].y0, route[arc_number-1].r], [route[arc_number+1].x0, route[arc_number+1].y0, route[arc_number+1].r], a_1*180/numpy.pi, a_2*180/numpy.pi))
                line = (route[arc_number-1].x0 + route[arc_number-1].r * numpy.cos(a_1),
                        route[arc_number-1].y0 + route[arc_number-1].r * numpy.sin(a_1), route[arc_number+1].x0 + route[arc_number+1].r * numpy.cos(a_2),
                        route[arc_number+1].y0 + route[arc_number+1].r * numpy.sin(a_2))

                _ = 0
                round = (arc.x0, arc.y0, arc.r)
                if isCrossed(line, round):
                    _ += 1
                if (round2Str(round) in intersections):
                    for i in intersections[round2Str(round)]:
                        if isCrossed(line, str2Round(i, rounds)):
                            _ += 1
                if _ == 0:
                    route1[arc_number - 1].a2 = a_1
                    route1[arc_number + 1].a1 = a_2
                    raise RoutePlanSoftError

                # if not isCrossed(line, [route[arc_number].x0, route[arc_number].y0, route[arc_number].r]):
                #     route1[arc_number - 1].a2 = a_1
                #     route1[arc_number + 1].a1 = a_2
                #     # print("--")
                #     # return num_of_clarify
                #     raise RoutePlanSoftError
        except RoutePlanSoftError:
            route1.pop(arc_number)
            return route1, None

        if not (previous_arc.a2 - arc.a1 < eps or previous_arc.a2 - (arc.a1 + numpy.pi)%(numpy.pi*2)<eps):
            # print("{}, {}, {}, {} - {}, {}, {}, {}".format(previous_arc.x0, previous_arc.y0, previous_arc.r, previous_arc.a2, arc.x0, arc.y0, arc.r, arc.a1))
            a_1, a_2,  d1, d2 = createCompound(previous_arc, arc)
            # previous_arc.a2 = a_1
            # arc.a1 = a_2
            route1[arc_number - 1].a2 = a_1
            route1[arc_number].a1 = a_2
            return route1, None

        # TODO: check for same rounds in arc and enemy

        # look if arc closed by rounds intersection
        enemy = whereClosedByRoundsIntersection(arc)
        if not (enemy == None):
            enemy = str2Round(enemy, rounds)
            # if enemy == (route1[arc_number+1].x0, route1[arc_number+1].y0, route1[arc_number+1].r):
            #     a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(previous_arc, route1[arc_number+1])
            #     if (a_1_ext == numpy.inf): return None, None
            #     if (previous_arc.dir == route1[arc_number+1].dir):
            #         if (arc.dir == d1_ext):
            #             previous_arc.a2 = a_1_ext
            #             route1[arc_number+1].a1 = a_1_ext
            #         else:
            #             previous_arc.a2 = a_2_ext
            #             route1[arc_number+1].a1 = a_2_ext
            #     elif (not a_1_int == numpy.inf):
            #         if (arc.dir == d1_int):
            #             previous_arc.a2 = (a_1_int + numpy.pi) % (2 * numpy.pi)
            #             route1[arc_number+1].a1 = a_1_int
            #         else:
            #             previous_arc.a2 = (a_2_int + numpy.pi) % (2 * numpy.pi)
            #             route1[arc_number+1].a1 = a_2_int
            #     else:
            #         route1 = None
            #     return route1, None
            # route1[arc_number-1].a2 = route1[arc_number-1].a1
            new_arc1 = Arc(enemy[0], enemy[1], enemy[2], arc.a1, arc.a2, arc.dir)
            new_arc2 = Arc(enemy[0], enemy[1], enemy[2], arc.a1, arc.a2, arc.dir)

            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(route1[arc_number-1], new_arc1)
            if (a_1_ext == numpy.inf): return None, None
            if (route1[arc_number-1].dir == new_arc1.dir):
                if (route1[arc_number-1].dir == d1_ext):
                    new_arc1.a1 = a_1_ext
                    route1[arc_number-1].a2 = a_1_ext
                else:
                    new_arc1.a1 = a_2_ext
                    route1[arc_number-1].a2 = a_2_ext
            elif (not a_1_int == numpy.inf):
                if (route1[arc_number-1].dir == d1_int):
                    new_arc1.a1 = (a_1_int + numpy.pi) % (2 * numpy.pi)
                    route1[arc_number-1].a2 = a_1_int
                else:
                    new_arc1.a1 = (a_2_int + numpy.pi) % (2 * numpy.pi)
                    route1[arc_number-1].a2 = a_2_int
            else:
                route1 = None
                return route1, None

            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(new_arc1, route1[arc_number+1])
            if (a_1_ext == numpy.inf): return None, None
            if (new_arc1.dir == route1[arc_number+1].dir):
                if (route1[arc_number+1].dir == d1_ext):
                    new_arc1.a2 = a_1_ext
                    route1[arc_number+1].a1 = a_1_ext
                else:
                    new_arc1.a2 = a_2_ext
                    route1[arc_number+1].a1 = a_2_ext
            elif (not a_1_int == numpy.inf):
                if (route1[arc_number+1].dir == d1_int):
                    new_arc1.a2 = (a_1_int + numpy.pi) % (2 * numpy.pi)
                    route1[arc_number+1].a1 = a_1_int
                else:
                    new_arc1.a2 = (a_2_int + numpy.pi) % (2 * numpy.pi)
                    route1[arc_number+1].a1 = a_2_int
            else:
                route1 = None
            # a_begin, a_end, direction1, direction2 = createallCompound(route1[arc_number-1], new_arc1)
            # route1[arc_number-1].a2 = a_begin
            # new_arc1.a1 = a_end
            # new_arc1.a2 = a_end
            # route1[arc_number-1].dir = direction1
            # new_arc1.dir = direction2
            #
            # a_begin, a_end, direction1, direction2 = createCompound(new_arc1, route1[arc_number])
            # new_arc1.a2 = a_begin
            # route1[arc_number-1].a1 = a_end
            # new_arc1.dir = direction1
            # route1[arc_number-1].dir = direction2

            if (not route1 == None):
                route1.pop(arc_number)
                route1.insert(arc_number, new_arc1)

            # print("x = {}, y = {} was added".format(new_arc.x0, new_arc.y0))
            # arc = new_arc1
            # num_of_clarify = num_of_clarify + 1
            return route1, None
        # enemy = whereClosedByRoundsIntersection(arc)
        # if not (enemy == None):
        #     previous_arc = arc
        #     arc_number = arc_number + 1
        #     continue

        line = (previous_arc.x0+previous_arc.r*numpy.cos(previous_arc.a2), previous_arc.y0+previous_arc.r*numpy.sin(previous_arc.a2), arc.x0+arc.r*numpy.cos(arc.a1), arc.y0+arc.r*numpy.sin(arc.a1))
        for round in rounds:
            # Looks if this round is edge of line
            if previous_arc.x0 == round[0] and previous_arc.y0 == round[1] and previous_arc.r == round[2]:
                continue
            if arc.x0 == round[0] and arc.y0 == round[1] and arc.r == round[2]:
                continue
            if not isCrossed(line, round):
                continue
            # find start angle
            # if round[2] < (arc.x0 - round[0])**2 + (arc.y0 - round[1])**2 or arc.r < (arc.x0 - round[0])**2 + (arc.y0 - round[1])**2:
            if (round[0] - line[0])/(line[2]-line[0])-(round[1] - line[1])/(line[3]-line[1])<0:
                start_angle = numpy.pi/2*3
            else:
                start_angle = numpy.pi/2

            new_arc1 = Arc(round[0], round[1], round[2], start_angle, start_angle, Direction.CLOCKWISE)
            new_arc2 = Arc(round[0], round[1], round[2], start_angle, start_angle, Direction.CLOCKWISE)
            # route1 = route.copy()
            # route2 = route.copy()

            # construct tangent
            # print("-------------")
            # print("{},{},{} - {},{},{}".format(previous_arc.x0, previous_arc.y0, previous_arc.r, round[0], round[1], round[2]))
            a_1_ext, a_2_ext, a_1_int, a_2_int,  d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(previous_arc, new_arc1)
            if (a_1_ext == numpy.inf): return None, None
            # print("a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}, d1 = {}, d2 = {}, d1 = {}, d2 = {}".format(a_1_ext, a_2_ext, a_1_int, a_2_int,  d1_ext, d2_ext, d1_int, d2_int))
            if (d1_ext == previous_arc.dir):
                route1[arc_number-1].a2 = a_1_ext
                new_arc1.a1 = a_1_ext
                new_arc1.a2 = a_1_ext
                new_arc1.dir = d1_ext
                # print("route1[arc_number-1].a2 = {}, new_arc1.a1 = {}, but route1[arc_number-1].a2 = {}, new_arc1.a1 = {}".format(a_1_ext, a_1_ext, route1[arc_number-1].a2, new_arc1.a1))
            else:
                route1[arc_number-1].a2 = a_2_ext
                new_arc1.a1 = a_2_ext
                new_arc1.a2 = a_2_ext
                new_arc1.dir = d2_ext
                # print("route1[arc_number-1].a2 = {}, new_arc1.a1 = {}, but route1[arc_number-1].a2 = {}, new_arc1.a1 = {}".format(a_2_ext, a_2_ext, route1[arc_number-1].a2, new_arc1.a1))

            if (not a_1_int == numpy.inf):
                if (d2_int == previous_arc.dir): # use direction for first round of first route which equal to direction for second round for second route
                    route2[arc_number-1].a2 = (a_1_int+numpy.pi)%(numpy.pi*2)
                    new_arc2.a1 = a_1_int
                    new_arc2.a2 = a_1_int
                    new_arc2.dir = d1_int
                    # print("route2[arc_number-1].a2 = {}, new_arc2.a1 = {}, but route2[arc_number-1].a2 = {}, new_arc2.a1 = {}".format((a_1_int+numpy.pi)%(numpy.pi*2), a_1_int, route2[arc_number-1].a2, new_arc2.a1))
                else:
                    route2[arc_number-1].a2 = (a_2_int+numpy.pi)%(numpy.pi*2)
                    new_arc2.a1 = a_2_int
                    new_arc2.a2 = a_2_int
                    new_arc2.dir = d2_int
                    # print("route2[arc_number-1].a2 = {}, new_arc2.a1 = {}, but route2[arc_number-1].a2 = {}, new_arc2.a1 = {}".format((a_2_int+numpy.pi)%(numpy.pi*2), a_2_int, route2[arc_number-1].a2, new_arc2.a1))
            else:
                route2 = None

            # print("{},{},{} - {},{},{}".format(new_arc1.x0, new_arc1.y0, new_arc1.r, arc.x0, arc.y0, arc.r))
            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(new_arc1, arc)
            if (a_1_ext == numpy.inf): return None, None
            # print(
            #     "a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}, d1 = {}, d2 = {}, d1 = {}, d2 = {}".format(a_1_ext,
            #                                                                                                     a_2_ext,
            #                                                                                                     a_1_int,
            #                                                                                                     a_2_int,
            #                                                                                                     d1_ext,
            #                                                                                                     d2_ext,
            #                                                                                                     d1_int,
            #                                                                                                     d2_int))
            if (new_arc1.dir == arc.dir):
                if (arc.dir == d1_ext):
                    new_arc1.a2 = a_1_ext
                    route1[arc_number].a1 = a_1_ext
                    # print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_1_ext, a_1_ext, route1[arc_number].a1, new_arc1.a2))
                else:
                    new_arc1.a2 = a_2_ext
                    route1[arc_number].a1 = a_2_ext
                    # print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_2_ext, a_2_ext, route1[arc_number].a1, new_arc1.a2))
            elif (not a_1_int == numpy.inf):
                if (arc.dir == d1_int):
                    new_arc1.a2 = (a_1_int+numpy.pi)%(2*numpy.pi)
                    route1[arc_number].a1 = a_1_int
                    # print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_1_int, (a_1_int+numpy.pi)%(2*numpy.pi), route1[arc_number].a1, new_arc1.a2))
                else:
                    new_arc1.a2 = (a_2_int+numpy.pi)%(2*numpy.pi)
                    route1[arc_number].a1 = a_2_int
                    # print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_2_int,
                    #                                                             (a_2_int+numpy.pi)%(2*numpy.pi), route1[arc_number].a1, new_arc1.a2))
            else:
                route1 = None

            if (not route2 == None):
                if (new_arc2.dir == arc.dir):
                    if (arc.dir == d1_ext):
                        new_arc2.a2 = a_1_ext
                        route2[arc_number].a1 = a_1_ext
                        # print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_1_ext, a_1_ext, route2[arc_number].a1, new_arc2.a2))
                    else:
                        new_arc2.a2 = a_2_ext
                        route2[arc_number].a1 = a_2_ext
                        # print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_2_ext, a_2_ext, route2[arc_number].a1, new_arc2.a2))
                elif (not a_1_int == numpy.inf):
                    if (arc.dir == d1_int):
                        new_arc2.a2 = (a_1_int + numpy.pi) % (2 * numpy.pi)
                        route2[arc_number].a1 = a_1_int
                        # print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_1_int, (a_1_int + numpy.pi) % (2 * numpy.pi), route2[arc_number].a1, new_arc2.a2))
                    else:
                        new_arc2.a2 = (a_2_int + numpy.pi) % (2 * numpy.pi)
                        route2[arc_number].a1 = a_2_int
                        # print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_2_int, (a_2_int + numpy.pi) % (
                        #             2 * numpy.pi), route2[arc_number].a1, new_arc2.a2))
                else:
                    route2 = None

            if (not route1 == None):
                route1.insert(arc_number,new_arc1)
            if (not route2 == None):
                route2.insert(arc_number,new_arc2)
            # print("x = {}, y = {} was added".format(new_arc.x0, new_arc.y0))
            return route1, route2

        previous_arc = arc
        arc_number = arc_number + 1
        # previous_point = point
    # if there no changes
    # route[0].a1 = route[0].a2
    # route[len(route)-1].a2 = route[len(route)-1].a1
    return "end", "end"


# construct compounds (angel) between two circles and find more fit
def createCompound(arc1, arc2):
    a1_external, a2_external, a1_internal, a2_internal, a1_dir_ext, _, a1_dir_int, _ = createAllCompounds(arc1, arc2)

    # Choose suitable tangent
    if roundDistance(a1_external, arc1.a2) < roundDistance(a2_external, arc1.a2):
        a_external = a1_external
    else:
        a_external = a2_external
        a1_dir_ext = Direction(a1_dir_ext.value % 2 + 1)
    # print("a_ext = {}".format(a_external))
    if roundDistance((a1_internal + numpy.pi)%(numpy.pi*2), arc1.a2) < roundDistance((a2_internal + numpy.pi)%(numpy.pi*2), arc1.a2):
        a_internal = a1_internal
    else:
        a_internal = a2_internal
        a1_dir_int = Direction(a1_dir_int.value % 2 + 1)
    # print("a_int = {}".format(a_internal))

    if roundDistance(a_internal, arc2.a1) < roundDistance(a_external, arc2.a1):
        a2 = a_internal
        a1 = (a_internal + numpy.pi)%(numpy.pi*2)
        dir2 = a1_dir_int
        dir1 = Direction(dir2.value % 2 + 1)
    else:
        a2 = a_external
        a1 = a_external
        dir2 = a1_dir_ext
        dir1 = a1_dir_ext

    return a1, a2, dir1, dir2 # angle and direction for first and second rounds

# def createCompound2(arc1, arc2):
#     a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(arc1, arc2)
#


# construct compounds (angel) between two circles
# returns in format: external, external, internal, internal, dir_ext, dir_ext, dir_int, dir_int
def createAllCompounds(arc1, arc2):
    # find parameters of equivalent construction task with a single round and a point
    if arc1.r>arc2.r:
        x0_external = arc1.x0
        y0_external = arc1.y0
        r_external = arc1.r - arc2.r
        x_external, y_external = arc2.x0, arc2.y0
        dir_for = 1
    else:
        x0_external = arc2.x0
        y0_external = arc2.y0
        r_external = arc2.r - arc1.r
        x_external, y_external = arc1.x0, arc1.y0
        dir_for = 2
    # find angles of point of contact of a circle and an external tangent
    a1_external, a2_external = createTangent(x_external, y_external, x0_external, y0_external, r_external) # External tangent
    # if a1_external - a2_external < a2_external - a1_external:
    if dir_for == 1:
        a1_dir_ext = Direction.CONTERCW
    else:
        a1_dir_ext = Direction.CLOCKWISE

    if arc1.r + arc2.r < numpy.sqrt((arc1.x0 - arc2.x0)**2 + (arc1.y0 - arc2.y0)**2):
        # find angle for second round of point of contact of a circle and an internal tangent. For that angle of point for first round you can do: a + 180
        a1_internal, a2_internal = createTangent(arc1.x0, arc1.y0, arc2.x0, arc2.y0, arc1.r + arc2.r)  # Internal tangent
        a1_dir_int = Direction.CLOCKWISE
    else:
        a1_internal, a2_internal = numpy.inf, numpy.inf
        a1_dir_int = Direction.CLOCKWISE
    # print("a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}".format(a1_external, a2_external, a1_internal, a2_internal))

    return a1_external, a2_external, a1_internal, a2_internal, a1_dir_ext, Direction(a1_dir_ext.value % 2 + 1), a1_dir_int, Direction(a1_dir_int.value % 2 + 1) # angle and direction for first and second rounds


# find angle of point of contact of round and tangent where tangent goes through the point A(XA, YA)
def createTangent(XA, YA, X0, Y0, R):
    try:
        if ((X0-XA)**2 + (Y0-YA)**2) < R**2 or (X0 == XA and Y0 == YA):
            raise Exception
        # a - angle between radius to touch point and line that connect round's center and point A
        # b - angle between horizontal line and line that connect round's center and point A
        cosa = R/numpy.sqrt((X0-XA)**2 + (Y0-YA)**2)
        # print("cos a = {}".format(cosa))
        if XA-X0 == 0:
            # tanb = numpy.inf
            if YA-Y0 > 0:
                b = numpy.pi/2
            else:
                b = numpy.pi*3/2
        else:
            tanb = (YA-Y0)/(XA-X0)
            b = numpy.arctan(tanb)
        # print("tan b = {}".format(tanb))
        # b = numpy.arctan(tanb)
        # print(b)
        if XA-X0<0:
            b = b + numpy.pi
        # print("b = {}".format(b))
        a = numpy.arccos(cosa)
        # print("a = {}".format(a))
        return (b+a)%(numpy.pi*2), (b-a)%(numpy.pi*2)
    except Exception as err:
        #print("Error in createTangent: {}-{}, {}-{}".format(X0, Y0, XA, YA))
        return numpy.inf, numpy.inf

# main function that create route throuth field
def CreateRouteByTangents(startX, startY, endX, endY, width, height, red_zone):
    try:
        pointed_route = list()
        pointed_route.append(Arc(startX, startY, 0, 0, 0, Direction.CONTERCW))
        pointed_route.append(Arc(endX, endY, 0, 0, 0, Direction.CONTERCW))
        red_zone = sorted(red_zone, key=lambda round: round[2], reverse=True)
        red_zone = normalizeRounds(red_zone)
        if startX < 0 or startX > width or startY < 0 or startY > height:
            raise MainPointInBadZoneError("Start point lay outside map")
        if endX < 0 or endX > width or endY < 0 or endY > height:
            raise MainPointInBadZoneError("End point lay outside map")
        for i_circle in red_zone:
            r = numpy.sqrt((startX - i_circle[0])**2 + (startY - i_circle[1])**2)
            if r < i_circle[2]:
                raise MainPointInBadZoneError("Start point lay into interdicted zone")
            r = numpy.sqrt((endX - i_circle[0]) ** 2 + (endY - i_circle[1]) ** 2)
            if r < i_circle[2]:
                raise MainPointInBadZoneError("End point lay into interdicted zone")
        # if all right, next code will run
        # next code do normal (I hope) route
        lookRoundsIntersections(red_zone)
        n=1
        while n>0:
            n = clarifyRoute(pointed_route, red_zone)
    # if initial conditions are wrong, a message about it will be displayed
    except MainPointInBadZoneError as err:
        print("Error: {}".format(err))
        pointed_route[1]=pointed_route[0]
    return pointed_route


def CreateTangentTree(startX, startY, endX, endY, width, height, red_zone):
    try:
        global good_routes, max_depth_of_tree
        max_depth_of_tree = 1
        good_routes = list()
        pointed_route = list()
        pointed_route.append(Arc(startX, startY, 0, 0, 0, Direction.CONTERCW))
        pointed_route.append(Arc(endX, endY, 0, 0, 0, Direction.CONTERCW))
        route_tree = pointed_route
        # red_zone = sorted(red_zone, key=lambda round: round[2], reverse=True)
        if startX < 0 or startX > width or startY < 0 or startY > height:
            raise MainPointInBadZoneError("Start point lay outside map")
        if endX < 0 or endX > width or endY < 0 or endY > height:
            raise MainPointInBadZoneError("End point lay outside map")
        for i_circle in red_zone:
            r = numpy.sqrt((startX - i_circle[0])**2 + (startY - i_circle[1])**2)
            if r < i_circle[2]:
                raise MainPointInBadZoneError("Start point lay into interdicted zone")
            r = numpy.sqrt((endX - i_circle[0]) ** 2 + (endY - i_circle[1]) ** 2)
            if r < i_circle[2]:
                raise MainPointInBadZoneError("End point lay into interdicted zone")
        # if all right, next code will run
        # next code do normal (I hope) route
        global j
        j = 0
        def a(tree, parent = None, current_depth_of_tree = 1):
            global j, good_routes, max_depth_of_tree
            if current_depth_of_tree>max_depth_of_tree: max_depth_of_tree = current_depth_of_tree
            if (tree == None):
                if is_log_on: log_file.write("------\nThis is deadlock path\n------\n")
                return None
            newTree = Tree(tree, None, None, parent)
            route1, route2 = clarifyRouteWithTree(tree, red_zone)
            if newTree.isInTreeBefore(tree):
                if is_log_on: log_file.write("------\nThis is deadlock path. It was yet\n------\n")
                return newTree
            for _ in good_routes:
                if _.isValueEqualTo(tree):
                    if is_log_on: log_file.write("------\nThis is deadlock path. It was yet\n------\n")
                    return newTree
                if _.isInTreeBefore(tree):
                    if is_log_on: log_file.write("------\nThis is deadlock path. It was yet\n------\n")
                    return newTree
            # if is_log_on: printroute(tree)

            if (route1 == "end"):
                k = Tree(tree, None, None, parent)
                good_routes.append(k)
                if is_log_on:
                    log_file.write("------\nThis is good path\n------\n")
                    printroute(tree)
                    log_file.write("---------------------\n")
                    drawRouteInFile(tree, red_zone, i=j, width=width, height=height)
                j += 1
                return k
            if is_log_on:
                printroute(tree)
                log_file.write("---------------------\n")

            newTree.left = a(route1, newTree, current_depth_of_tree=current_depth_of_tree+1)
            newTree.right = a(route2, newTree, current_depth_of_tree=current_depth_of_tree+1)
            # newTree = Tree(tree, a(route1), a(route2))
            # if not (newTree.left == None or newTree.left == "end"): newTree.left.parent = newTree
            # if not (newTree.right == None or newTree.right == "end"): newTree.right.parent = newTree
            return newTree
            # return Tree(tree, a(route1), a(route2))
        route_tree = a(route_tree)

        # while (not pointed_route == None):
        #     route1, route2 = clarifyRouteWithTree(route_tree.value, red_zone)
        #     route_tree.left = route1
        #     route_tree.right = route2
    # if initial conditions are wrong, a message about it will be displayed
    except MainPointInBadZoneError as err:
        print("Error: {}".format(err))
        route_tree = None
    return route_tree

def CreateRouteByTangentTree(startX, startY, endX, endY, width, height, red_zone):
    red_zone = sorted(red_zone, key=lambda round: round[2], reverse=True)
    red_zone = normalizeRounds(red_zone)
    lookRoundsIntersections(red_zone)
    tree = CreateTangentTree(startX, startY, endX, endY, width, height, red_zone)
    if tree == None:
        tree = list()
        tree.append(Arc(startX, startY, 0, 0, 0, Direction.CONTERCW))
        tree.append(Arc(endX, endY, 0, 0, 0, Direction.CONTERCW))
        return tree
    global log_file
    # if is_log_on: log_file.close()
    global good_routes
    # TODO: choose brilliant path from all created pathes
    best_index = 1
    min_distance = numpy.inf
    for i in range(len(good_routes)):
        good_route = good_routes[i].value
        distance = 0
        pr_point = good_route[0]
        for point in good_route:
            distance += distanceBetweenRoundPoits((pr_point.x0, pr_point.y0, pr_point.r), pr_point.a2, (point.x0, point.y0, point.r), point.a1)
            if point.dir == Direction.CLOCKWISE:
                distance += lenthOfArc(point.r, point.a1, point.a2)
            else:
                distance += lenthOfArc(point.r, point.a2, point.a1)
        if distance < min_distance:
            min_distance = distance
            best_index = i

    return good_routes[best_index].value

def createGraphWithRounds(rounds):
    graph = dict()
    for round1 in rounds:
        graph.setdefault(round2Str(round1) + "CCW",
                         [round1[2], dict()])  # [ext/CCW, int/CCW] // directions for this round
        graph.setdefault(round2Str(round1) + "CWS",
                         [round1[2], dict()])  # [ext/CW, int/CW] // directions for this round
    for round1 in rounds:

        arc1 = Arc(round1[0], round1[1], round1[2], 0, 0, Direction.CLOCKWISE)
        upTriangle = False
        for round2 in rounds:
            if (round1 == round2): upTriangle = True
            if not upTriangle: continue
            arc2 = Arc(round2[0], round2[1], round2[2], 0, 0, Direction.CLOCKWISE)
            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(arc1, arc2)

            _1, _2 = round2Str(round1), round2Str(round2)
            if not a_1_ext == numpy.inf:
                x1 = round1[0] + numpy.cos(a_1_ext) * round1[2]
                y1 = round1[1] + numpy.sin(a_1_ext) * round1[2]
                x2 = round2[0] + numpy.cos(a_1_ext) * round2[2]
                y2 = round2[1] + numpy.sin(a_1_ext) * round2[2]
                line = [x1, y1, x2, y2]
                crossed = False
                for r in rounds:
                    if crossed == True: continue
                    if r == round1 or r == round2: continue
                    if isCrossed(line, r): crossed = True

                if not crossed:
                    d1 = distanceBetweenRoundPoits(round1, a_1_ext, round2, a_1_ext)
                    if d1_ext == Direction.CONTERCW:
                        graph[_1+"CCW"][1].setdefault(_2+"CCW", (d1, a_1_ext))
                        graph[_2+"CWS"][1].setdefault(_1+"CWS", (d1, a_1_ext))
                    else:
                        graph[_1+"CWS"][1].setdefault(_2+"CWS", (d1, a_1_ext))
                        graph[_2+"CCW"][1].setdefault(_1+"CCW", (d1, a_1_ext))

            if not a_2_ext == numpy.inf:
                x1 = round1[0] + numpy.cos(a_2_ext) * round1[2]
                y1 = round1[1] + numpy.sin(a_2_ext) * round1[2]
                x2 = round2[0] + numpy.cos(a_2_ext) * round2[2]
                y2 = round2[1] + numpy.sin(a_2_ext) * round2[2]
                line = [x1, y1, x2, y2]
                crossed = False
                for r in rounds:
                    if crossed == True: continue
                    if r == round1 or r == round2: continue
                    if isCrossed(line, r): crossed = True

                if not crossed:
                    d1 = distanceBetweenRoundPoits(round1, a_2_ext, round2, a_2_ext)
                    if d2_ext == Direction.CONTERCW:
                        graph[_1 + "CCW"][1].setdefault(_2 + "CCW", (d1, a_2_ext))
                        graph[_2 + "CWS"][1].setdefault(_1 + "CWS", (d1, a_2_ext))
                    else:
                        graph[_1 + "CWS"][1].setdefault(_2 + "CWS", (d1, a_2_ext))
                        graph[_2 + "CCW"][1].setdefault(_1 + "CCW", (d1, a_2_ext))

            if not a_1_int == numpy.inf:
                x1 = round1[0] + numpy.cos((a_1_int+numpy.pi)%(numpy.pi*2)) * round1[2]
                y1 = round1[1] + numpy.sin((a_1_int+numpy.pi)%(numpy.pi*2)) * round1[2]
                x2 = round2[0] + numpy.cos(a_1_int) * round2[2]
                y2 = round2[1] + numpy.sin(a_1_int) * round2[2]
                line = [x1, y1, x2, y2]
                crossed = False
                for r in rounds:
                    if crossed == True: continue
                    if r == round1 or r == round2: continue
                    if isCrossed(line, r): crossed = True

                if not crossed:
                    d1 = distanceBetweenRoundPoits(round1, (a_1_int+numpy.pi)%(numpy.pi*2), round2, a_1_int)
                    if d1_int == Direction.CLOCKWISE:
                        graph[_1 + "CCW"][1].setdefault(_2 + "CWS", (d1, (a_1_int+numpy.pi)%(numpy.pi*2)))
                        graph[_2 + "CCW"][1].setdefault(_1 + "CWS", (d1, a_1_int))
                    else:
                        graph[_1 + "CWS"][1].setdefault(_2 + "CCW", (d1, (a_1_int+numpy.pi)%(numpy.pi*2)))
                        graph[_2 + "CWS"][1].setdefault(_1 + "CCW", (d1, a_1_int))

            if not a_2_int == numpy.inf:
                x1 = round1[0] + numpy.cos((a_2_int+numpy.pi)%(numpy.pi*2)) * round1[2]
                y1 = round1[1] + numpy.sin((a_2_int+numpy.pi)%(numpy.pi*2)) * round1[2]
                x2 = round2[0] + numpy.cos(a_2_int) * round2[2]
                y2 = round2[1] + numpy.sin(a_2_int) * round2[2]
                line = [x1, y1, x2, y2]
                crossed = False
                for r in rounds:
                    if crossed == True: continue
                    if r == round1 or r == round2: continue
                    if isCrossed(line, r): crossed = True

                if not crossed:
                    d1 = distanceBetweenRoundPoits(round1, (a_2_int+numpy.pi)%(numpy.pi*2), round2, a_2_int)
                    if d2_int == Direction.CONTERCW:
                        graph[_1 + "CWS"][1].setdefault(_2 + "CCW", (d1, (a_2_int+numpy.pi)%(numpy.pi*2)))
                        graph[_2 + "CWS"][1].setdefault(_1 + "CCW", (d1, a_2_int))
                    else:
                        graph[_1 + "CCW"][1].setdefault(_2 + "CWS", (d1, (a_2_int+numpy.pi)%(numpy.pi*2)))
                        graph[_2 + "CCW"][1].setdefault(_1 + "CWS", (d1, a_2_int))

    return graph

def DijkstraAlgorithm(graph): # graph = [item0, ..., itemN-3, start, end]; N elements
    # TODO: clarify algorithm of finding best way
    vertexes = dict()
    str_rounds = list(graph.keys())
    length = len(str_rounds)
    graph.pop(str_rounds[length - 3])
    graph.pop(str_rounds[length - 1])
    _1 = str_rounds.pop(length-1)
    _2 = str_rounds.pop(length-3)
    for i in graph:
        graph.get(i)[1].pop(_1, None)
        graph.get(i)[1].pop(_2, None)
    length -= 2
    for i in str_rounds:
        vertexes.setdefault(i, [False, numpy.inf, None]) # isGone / distance / way by str rounds
    vertexes.update({str_rounds[length-2]: [False, 0, [str_rounds[length-2]]]})
    isContinue = length

    while isContinue > 1:
        isContinue = 0
        min_distance = numpy.inf
        this_vertex = None
        for circle in vertexes:
            vertex = vertexes.get(circle)
            if not vertex[0]:
                isContinue += 1
                if vertex[1] < min_distance:
                    min_distance = vertex[1]
                    this_vertex = circle

        if this_vertex == str_rounds[length-1] or this_vertex == None:
            # isContinue = 0
            this_vertex = str_rounds[length - 1]
            route = list()
            str_route = vertexes.get(this_vertex)[2]
            for current_number in range(len(str_route)):
                coord = str_route[current_number].split("-")
                coord[1] = coord[1][0:len(coord[1])-3]
                if current_number == 0:
                    a1 = 0
                else:
                    str1 = str_route[current_number-1]
                    if current_number > 1:
                        l = len(str1)
                        ending = str1[l-3:l]
                        if ending == 'CCW':
                            str1 = str1[0:l-3]+'CWS'
                        else:
                            str1 = str1[0:l-3]+'CCW'
                    str2 = str_route[current_number]
                    if current_number < len(str_route)-1:
                        l = len(str2)
                        ending = str2[l - 3:l]
                        if ending == 'CCW':
                            str2 = str2[0:l - 3] + 'CWS'
                        else:
                            str2 = str2[0:l - 3] + 'CCW'
                    a1 = graph.get(str2)[1].get(str1)[1]
                if current_number == len(str_route) - 1:
                    a2 = 0
                else:
                    a2 = graph.get(str_route[current_number])[1].get(str_route[current_number + 1])[1]
                l = len(str_route[current_number])
                if str_route[current_number][l-4:l] == "CCW":
                    d = Direction.CONTERCW
                else:
                    d = Direction.CLOCKWISE
                arc = Arc(int(coord[0]), int(coord[1]), graph.get(str_route[current_number])[0], a1, a2, d)
                route.append(arc)
            return route
            # continue # full exit from cicle

        for link in graph[this_vertex][1]:
            if vertexes.get(link)[0]: continue
            all_previous = vertexes.get(this_vertex)[2]
            if len(all_previous) < 2:
                a = 0
            else:
                previous = all_previous[len(all_previous)-2]
                a = graph.get(previous)[1].get(this_vertex)[1]
            new_distance = min_distance
            if this_vertex[len(this_vertex)-3:len(this_vertex)] == 'CWS':
                new_distance += lenthOfArc(graph.get(this_vertex)[0], a, graph.get(this_vertex)[1].get(link)[1])
            else:
                new_distance += lenthOfArc(graph.get(this_vertex)[0], graph.get(this_vertex)[1].get(link)[1], a)
            new_distance += graph.get(this_vertex)[1].get(link)[0]
            if new_distance < vertexes.get(link)[1]:
                _ = list(all_previous)
                _.append(link)
                vertexes.update({link: [False, new_distance, _]})

        vertexes.get(this_vertex)[0] = True

    print("AAAAAAAAAAAA_AAAAAAA__a-_A_A__A__Aa-_A_a__A_A_a-AAaaaaaaaaAAAAA-AAAA")
    return None

def CreateRouteByDijkstraAlgorithm(startX, startY, endX, endY, width, height, red_zone):
    red_zone = sorted(red_zone, key=lambda round: round[2], reverse=True)
    red_zone = normalizeRounds(red_zone)
    red_zone.append((startX, startY, 0))
    red_zone.append((endX, endY, 0))
    graph = createGraphWithRounds(red_zone)
    route = DijkstraAlgorithm(graph)
    return route

def printroute(route):
    log_file.write("Start route\n")
    for i in route:
        log_file.write("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}\n".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))
    log_file.write("End route\n")

def drawRouteInFile(route, rounds, width=600, height=600, i=0):
    name = "Debug_img_{}.png".format(i)
    print(name)
    Graph.createImageFile(name, width, height)
    # debug_im = Image.new('RGBA', (width, height))
    # debug_im.save("Debug_img_{}".format(i))
    # debug_im.close()
    Graph.draw_list_of_circles(rounds, image=name)
    if len(route)>0:
        lines = list()
        i_pr = route[0]
        for i in route:
            lines.append([(int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)), (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)), (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)), (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1))])
            i_pr = i
        Graph.draw_list_of_lines(lines, image=name)

def drawRouteInBigImage(route, rounds0, name, width=600, height=600, x0 = 0, y0 = 0):
    _ = 0
    rounds = rounds0.copy()
    for i in rounds:
        rounds[_] = (i[0]+x0, i[1]+y0, i[2])
        _ += 1
    Graph.draw_list_of_circles(rounds, image=name)
    if len(route) > 0:
        lines = list()
        i_pr = route[0]
        for i in route:
            lines.append([(int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)+x0),
                          (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)+y0),
                          (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)+x0), (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1)+y0)])
            i_pr = i
        Graph.draw_list_of_lines(lines, image=name)

def drawTree(depth, rounds, leaf_width=600, leaf_height=600):
    global num_line
    num_line = 0
    name = "Debug_img_tree.png"
    print(name)
    height = (leaf_height + 50) * (depth + 1)
    width = (leaf_width + 50) * (2**(depth - 1))
    Graph.createImageFile(name, width, height)
    log_file = open("log.txt", "r+")
    content_lines = log_file.readlines()
    # left top corner
    x = width/2 - leaf_width/2
    y = 25
    def a(x, y, img, content, width, height, depth_gap):
        global num_line
        good_path = False
        lines = list()
        content_line = content[num_line]
        while (not content_line == "Start route\n"):
            if content_line == "This is good path\n":
                good_path = True
            if content_line == "This is deadlock path. It was yet\n" or content_line == "This is deadlock path":
                return None
            num_line += 1
            content_line = content[num_line]
        num_line += 1
        content_line = content[num_line]
        # i_pr = Arc(0, 0, 0, 0, 0, Direction.CONTERCW)
        while (not content_line == "End route\n"):
            parts = content_line.split(" ")
            i = Arc(0, 0, 0, 0, 0, Direction.CONTERCW)
            i.x0 = float(parts[2].split(",")[0])
            i.y0 = float(parts[5].split(",")[0])
            i.r = float(parts[8].split(",")[0])
            _ = parts[11].split(",")[0]
            if (_ == "inf"):
                return None
            i.a1 = float(_)
            _ = parts[14].split(",")[0]
            if (_ == "inf"):
                return None
            i.a2 = float(_)
            lines.append(i)
            # lines.append([(int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)),
            #               (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)),
            #               (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)),
            #               (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1))])
            # i_pr = i
            num_line += 1
            content_line = content[num_line]
        drawRouteInBigImage(lines, rounds, img, x0=x, y0=y)
        if good_path:
            return None
        a((x+width/2)-depth_gap/2-width/2, y+50+height, img, content, width, height, depth_gap=depth_gap/2)
        a((x+width/2)+depth_gap/2-width/2, y+50+height, img, content, width, height, depth_gap=depth_gap/2)
        return None
    a(x, y, name, content_lines, leaf_width, leaf_height, depth_gap=width/2)
    log_file.close()

def log_on():
    global log_file, route, max_depth_of_tree, is_log_on
    log_file = open("log.txt", "w+")
    is_log_on = True

if __name__ == "__main__":
    def test_by_tree():
        global log_file, route, max_depth_of_tree
        if is_log_on: log_file = open("log.txt", "w+")
        route = CreateRouteByTangentTree(x_start, y_start, x_end, y_end, width, height, rounds)
        drawRouteInFile(route, rounds, i='n')
        if is_log_on:
            log_file.close()
            # drawTree(max_depth_of_tree, rounds)
    def test_by_tangents():
        route = CreateRouteByTangents(x_start, y_start, x_end, y_end, width, height, rounds)
        for i in route:
            print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))
        drawRouteInFile(route, rounds, i='n')
    def test_by_Dijkstra():
        route = CreateRouteByDijkstraAlgorithm(x_start, y_start, x_end, y_end, width, height, rounds)
        for i in route:
            print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))
        drawRouteInFile(route, rounds, i='n')

    Graph.set_parameters(width=600, height=600)
    # route = [Arc(0,0,0,0,0,Direction.CONTERCW),Arc(599,599,0,0,0,Direction.CONTERCW)]
    rounds = [(85,80,6), (15, 16, 9), (50, 0, 8), (60, 62, 4), (200, 100, 85), (400, 360, 76), (500, 100, 50), (560, 540, 15), (380, 350, 6), (200, 280, 30), (360, 450, 100), (500, 400, 60)]
    # rounds = [(90, 60, 20), (150, 150, 30), (500, 540, 50), (300, 340, 60)]
    # rounds = [(200, 0, 20), (200, 20, 20), (200, 50, 20), (200, 80, 20), (200, 100, 20), (200, 110, 20), (200, 145, 20), (200, 160, 20), (210, 180, 20), (200, 200, 20), (200, 235, 20), (195, 265, 20), (200, 300, 20)]
    # rounds = [(100, 100, 10), (200,200,20)]
    # rounds = list()
    # rounds = [(100,100,10), (200,200,20), (400, 350, 100)]

    # drawRoute([], rounds, 600, 600, 10)
    # Graph.createImageFile("Test_image.png", 600, 600)
    # Graph.draw_list_of_circles(rounds, "Test_image.png")

    rounds = sorted(rounds, key=lambda round: round[2], reverse=True)
    print(rounds)
    # rounds = normalizeRounds(rounds)
    # print(rounds)
    # a = lookRoundsIntersections(rounds)
    # CreateRouteByTangentTree(0, 0, 600, 600, 1000, 1000, rounds)
    # print(a)

    x_start, y_start, x_end, y_end = 0, 0, 599, 599
    width, height = 600, 600

    # log_on()
    test_by_Dijkstra()

    # a = lenthOfArc(10, 1, 0)
    # print(a)

    # route = CreateRouteByTangents(x_start,y_start,x_end,y_end,width,height,rounds)
    # route = CreateRouteByTangentTree(x_start, y_start, x_end, y_end, width, height, rounds)
    # printroute(route)
    # #
    # # n = 1
    # # while n>0:
    # #     n = clarifyRoute(route, rounds)
    #     # print("-----------------------------------------------")
    #     # for i in route:
    #     #     print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}".format(i.x0, i.y0, i.r, i.a1, i.a2))
    #     # print("-----------------------------------------------")
    #
    # for i in route:
    #     print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))
    #
    # Graph.full_map_conjunction()
    # Graph.draw_list_of_circles(rounds)
    # # for i in rounds:
    # #     Graph.circle_draw(i[0], i[1], i[2])
    # i_pr = route[0]
    # lines = list()
    # for i in route:
    #     # Graph.draw_line((int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)), (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)), (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)), (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1)))
    #     lines.append([(int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)), (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)), (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)), (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1))])
    #     i_pr = i
    # Graph.draw_list_of_lines(lines)
    # log_file.close()
