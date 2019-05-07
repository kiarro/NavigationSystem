# I must look at internal angles for finding rigth using of it



# angles are deposited clockwise from the direction right??

# always: CCW - CW < 180 < CW - CCW

import numpy
import scipy.optimize as opt
from enum import Enum
import Graph
import copy

eps = 0.0001

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
    return numpy.nan

# this function work only in clockwise direction
def isArcsCrossed(a1_1, a1_2, a2_1, a2_2): # input vars are numbers
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
            a = numpy.arccos(cosa)
            b = numpy.arccos(cosb)
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
                                                   line[2] - line[0])], [line[0], line[1]])

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
            enemy = str2Round(enemy, rounds)
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
def clarifyRouteWithTree(route, round_array):
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
                if not isCrossed(line, [route[arc_number].x0, route[arc_number].y0, route[arc_number].r]):
                    route1[arc_number - 1].a2 = a_1
                    route1[arc_number + 1].a1 = a_2
                    # print("--")
                    # return num_of_clarify
                    raise RoutePlanSoftError
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
        enemy = whereClosedByRoundsIntersection(previous_arc)
        if not (enemy == None):
            enemy = str2Round(enemy, rounds)
            route1[arc_number-1].a2 = route1[arc_number-1].a1
            new_arc1 = Arc(enemy[0], enemy[1], enemy[2], route1[arc_number-1].a1, route1[arc_number-1].a2, Direction.CLOCKWISE)

            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(route1[arc_number-1], new_arc1)

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

            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(new_arc1, arc)

            if (new_arc1.dir == arc.dir):
                if (arc.dir == d1_ext):
                    new_arc1.a2 = a_1_ext
                    route1[arc_number].a1 = a_1_ext
                else:
                    new_arc1.a2 = a_2_ext
                    route1[arc_number].a1 = a_2_ext
            elif (not a_1_int == numpy.nan):
                if (arc.dir == d1_int):
                    new_arc1.a2 = (a_1_int + numpy.pi) % (2 * numpy.pi)
                    route1[arc_number].a1 = a_1_int
                else:
                    new_arc1.a2 = (a_2_int + numpy.pi) % (2 * numpy.pi)
                    route1[arc_number].a1 = a_2_int
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

            if (not route1 == None): route1.insert(arc_number, new_arc1)
            # print("x = {}, y = {} was added".format(new_arc.x0, new_arc.y0))
            arc = new_arc1
            num_of_clarify = num_of_clarify + 1
            return route1, None
        enemy = whereClosedByRoundsIntersection(arc)
        if not (enemy == None):
            previous_arc = arc
            arc_number = arc_number + 1
            continue

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

            new_arc1 = Arc(round[0], round[1], round[2], start_angle, start_angle, Direction.CLOCKWISE)
            new_arc2 = Arc(round[0], round[1], round[2], start_angle, start_angle, Direction.CLOCKWISE)
            # route1 = route.copy()
            # route2 = route.copy()

            # construct tangent
            print("-------------")
            print("{},{},{} - {},{},{}".format(previous_arc.x0, previous_arc.y0, previous_arc.r, round[0], round[1], round[2]))
            a_1_ext, a_2_ext, a_1_int, a_2_int,  d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(previous_arc, new_arc1)
            print("a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}, d1 = {}, d2 = {}, d1 = {}, d2 = {}".format(a_1_ext, a_2_ext, a_1_int, a_2_int,  d1_ext, d2_ext, d1_int, d2_int))
            if (d1_ext == previous_arc.dir):
                route1[arc_number-1].a2 = a_1_ext
                new_arc1.a1 = a_1_ext
                new_arc1.a2 = a_1_ext
                new_arc1.dir = d1_ext
                print("route1[arc_number-1].a2 = {}, new_arc1.a1 = {}, but route1[arc_number-1].a2 = {}, new_arc1.a1 = {}".format(a_1_ext, a_1_ext, route1[arc_number-1].a2, new_arc1.a1))
            else:
                route1[arc_number-1].a2 = a_2_ext
                new_arc1.a1 = a_2_ext
                new_arc1.a2 = a_2_ext
                new_arc1.dir = d2_ext
                print("route1[arc_number-1].a2 = {}, new_arc1.a1 = {}, but route1[arc_number-1].a2 = {}, new_arc1.a1 = {}".format(a_2_ext, a_2_ext, route1[arc_number-1].a2, new_arc1.a1))

            if (not a_1_int == numpy.nan):
                if (d2_int == previous_arc.dir): # use direction for first round of first route which equal to direction for second round for second route
                    route2[arc_number-1].a2 = (a_1_int+numpy.pi)%(numpy.pi*2)
                    new_arc2.a1 = a_1_int
                    new_arc2.a2 = a_1_int
                    new_arc2.dir = d1_int
                    print("route2[arc_number-1].a2 = {}, new_arc2.a1 = {}, but route2[arc_number-1].a2 = {}, new_arc2.a1 = {}".format((a_1_int+numpy.pi)%(numpy.pi*2), a_1_int, route2[arc_number-1].a2, new_arc2.a1))
                else:
                    route2[arc_number-1].a2 = (a_2_int+numpy.pi)%(numpy.pi*2)
                    new_arc2.a1 = a_2_int
                    new_arc2.a2 = a_2_int
                    new_arc2.dir = d2_int
                    print("route2[arc_number-1].a2 = {}, new_arc2.a1 = {}, but route2[arc_number-1].a2 = {}, new_arc2.a1 = {}".format((a_2_int+numpy.pi)%(numpy.pi*2), a_2_int, route2[arc_number-1].a2, new_arc2.a1))
            else:
                route2 = None

            print("{},{},{} - {},{},{}".format(new_arc1.x0, new_arc1.y0, new_arc1.r, arc.x0, arc.y0, arc.r))
            a_1_ext, a_2_ext, a_1_int, a_2_int, d1_ext, d2_ext, d1_int, d2_int = createAllCompounds(new_arc1, arc)
            print(
                "a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}, d1 = {}, d2 = {}, d1 = {}, d2 = {}".format(a_1_ext,
                                                                                                                a_2_ext,
                                                                                                                a_1_int,
                                                                                                                a_2_int,
                                                                                                                d1_ext,
                                                                                                                d2_ext,
                                                                                                                d1_int,
                                                                                                                d2_int))
            if (new_arc1.dir == arc.dir):
                if (arc.dir == d1_ext):
                    new_arc1.a2 = a_1_ext
                    route1[arc_number].a1 = a_1_ext
                    print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_1_ext, a_1_ext, route1[arc_number].a1, new_arc1.a2))
                else:
                    new_arc1.a2 = a_2_ext
                    route1[arc_number].a1 = a_2_ext
                    print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_2_ext, a_2_ext, route1[arc_number].a1, new_arc1.a2))
            elif (not a_1_int == numpy.nan):
                if (arc.dir == d1_int):
                    new_arc1.a2 = (a_1_int+numpy.pi)%(2*numpy.pi)
                    route1[arc_number].a1 = a_1_int
                    print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_1_int, (a_1_int+numpy.pi)%(2*numpy.pi), route1[arc_number].a1, new_arc1.a2))
                else:
                    new_arc1.a2 = (a_2_int+numpy.pi)%(2*numpy.pi)
                    route1[arc_number].a1 = a_2_int
                    print("route1[arc_number].a1 = {}, new_arc1.a2 = {}, but route1[arc_number].a1 = {}, new_arc1.a2 = {}".format(a_2_int,
                                                                                (a_2_int+numpy.pi)%(2*numpy.pi), route1[arc_number].a1, new_arc1.a2))
            else:
                route1 = None

            if (not route2 == None):
                if (new_arc2.dir == arc.dir):
                    if (arc.dir == d1_ext):
                        new_arc2.a2 = a_1_ext
                        route2[arc_number].a1 = a_1_ext
                        print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_1_ext, a_1_ext, route2[arc_number].a1, new_arc2.a2))
                    else:
                        new_arc2.a2 = a_2_ext
                        route2[arc_number].a1 = a_2_ext
                        print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_2_ext, a_2_ext, route2[arc_number].a1, new_arc2.a2))
                elif (not a_1_int == numpy.nan):
                    if (arc.dir == d1_int):
                        new_arc2.a2 = (a_1_int + numpy.pi) % (2 * numpy.pi)
                        route2[arc_number].a1 = a_1_int
                        print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_1_int, (a_1_int + numpy.pi) % (2 * numpy.pi), route2[arc_number].a1, new_arc2.a2))
                    else:
                        new_arc2.a2 = (a_2_int + numpy.pi) % (2 * numpy.pi)
                        route2[arc_number].a1 = a_2_int
                        print("route2[arc_number].a1 = {}, new_arc2.a2 = {}, but route2[arc_number].a1 = {}, new_arc2.a2 = {}".format(a_2_int, (a_2_int + numpy.pi) % (
                                    2 * numpy.pi), route2[arc_number].a1, new_arc2.a2))
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
    if a1_external - a2_external < a2_external - a1_external:
        a1_dir_ext = Direction.CONTERCW
    else:
        a1_dir_ext = Direction.CLOCKWISE

    if arc1.r + arc2.r < numpy.sqrt((arc1.x0 - arc2.x0)**2 + (arc1.y0 - arc2.y0)**2):
        # find angle for second round of point of contact of a circle and an internal tangent. For that angle of point for first round you can do: a + 180
        a1_internal, a2_internal = createTangent(arc1.x0, arc1.y0, arc2.x0, arc2.y0, arc1.r + arc2.r)  # Internal tangent
        if a1_internal - a2_internal < a2_internal - a1_internal:
            a1_dir_int = Direction.CONTERCW # direction for ferst angle for second round
        else:
            a1_dir_int = Direction.CLOCKWISE
        # if dir_for == 1:
        #     a1_internal, a2_internal = (a1_internal+numpy.pi)%(numpy.pi*2), (a2_internal+numpy.pi)%(numpy.pi*2)
        #     a1_dir_int = Direction(a1_dir_ext.value % 2 + 1)
    else:
        a1_internal, a2_internal = numpy.nan, numpy.nan
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
        print("Error in createTangent: {}-{}, {}-{}".format(X0, Y0, XA, YA))
        return numpy.nan, numpy.nan

# main function that create route throuth field
def CreateRouteByTangents(startX, startY, endX, endY, width, height, red_zone):
    try:
        pointed_route = list()
        pointed_route.append(Arc(startX, startY, 0, 0, 0, Direction.CONTERCW))
        pointed_route.append(Arc(endX, endY, 0, 0, 0, Direction.CONTERCW))
        red_zone = sorted(red_zone, key=lambda round: round[2], reverse=True)
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
        n=1
        while n>0:
            n = clarifyRoute(pointed_route, red_zone)
    # if initial conditions are wrong, a message about it will be displayed
    except MainPointInBadZoneError as err:
        print("Error: {}".format(err))
        pointed_route[1]=pointed_route[0]
    return pointed_route


def CreateRouteByTangentTree(startX, startY, endX, endY, width, height, red_zone):
    try:
        global good_routes
        good_routes = list()
        pointed_route = list()
        pointed_route.append(Arc(startX, startY, 0, 0, 0, Direction.CONTERCW))
        pointed_route.append(Arc(endX, endY, 0, 0, 0, Direction.CONTERCW))
        route_tree = pointed_route
        red_zone = sorted(red_zone, key=lambda round: round[2], reverse=True)
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
        def a(tree, parent = None):
            global j, good_routes
            if (tree == None):
                log_file.write("------\nThis is deadlock path\n------\n")
                return None
            newTree = Tree(tree, None, None, parent)
            route1, route2 = clarifyRouteWithTree(tree, red_zone)
            if newTree.isInTreeBefore(tree):
                log_file.write("------\nThis is deadlock path. It was yet\n------\n")
                return newTree
            for _ in good_routes:
                if _.isValueEqualTo(tree):
                    log_file.write("------\nThis is deadlock path. It was yet\n------\n")
                    return newTree
                if _.isInTreeBefore(tree):
                    log_file.write("------\nThis is deadlock path. It was yet\n------\n")
                    return newTree
            # printroute(tree)

            if (route1 == "end"):
                k = Tree(tree, None, None, parent)
                good_routes.append(k)
                log_file.write("------\nThis is good path\n------\n")
                printroute(tree)
                log_file.write("---------------------\n")
                drawRoute(tree, rounds, i=j)
                j += 1
                return k
            printroute(tree)
            log_file.write("---------------------\n")

            newTree.left = a(route1, newTree)
            newTree.right = a(route2, newTree)
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

def printroute(route):
    log_file.write("Strart route\n")
    for i in route:
        log_file.write("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}\n".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))
    log_file.write("End route\n")

def drawRoute(route, rounds, width=600, height=600, i=0):
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

if __name__ == "__main__":
    def test_with_log():
        global log_file, route
        log_file = open("log.txt", "w+")
        route = CreateRouteByTangentTree(x_start, y_start, x_end, y_end, width, height, rounds)
        log_file.close()
    def test_without_log():
        route = CreateRouteByTangents(x_start, y_start, x_end, y_end, width, height, rounds)
        for i in route:
            print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))
        drawRoute(route, rounds, i='n')

    Graph.set_parameters(width=600, height=600)
    # route = [Arc(0,0,0,0,0,Direction.CONTERCW),Arc(599,599,0,0,0,Direction.CONTERCW)]
    rounds = [(85,80,6), (15, 16, 9), (50, 0, 8), (60, 62, 4), (200, 100, 85), (400, 360, 76), (500, 100, 50), (560, 540, 15), (380, 350, 6), (200, 280, 30), (360, 450, 100), (500, 400, 60)]
    # rounds = [(90, 60, 20), (150, 150, 30), (500, 540, 50), (300, 340, 60)]
    # rounds = [(200, 0, 20), (200, 20, 20), (200, 50, 20), (200, 80, 20), (200, 100, 20), (200, 110, 20), (200, 145, 20), (200, 160, 20), (210, 180, 20), (200, 200, 20), (200, 235, 20), (195, 265, 20), (200, 300, 20)]
    # rounds = [(100, 100, 10), (200,200,20)]
    # rounds = [(100,100,10), (200,200,20), (400, 350, 100)]

    # drawRoute([], rounds, 600, 600, 10)
    # Graph.createImageFile("Test_image.png", 600, 600)
    # Graph.draw_list_of_circles(rounds, "Test_image.png")

    rounds = sorted(rounds, key=lambda round: round[2], reverse=True)
    print(rounds)
    rounds = normalizeRounds(rounds)
    # print(rounds)
    a = lookRoundsIntersections(rounds)
    # CreateRouteByTangentTree(0, 0, 600, 600, 1000, 1000, rounds)
    # print(a)

    x_start, y_start, x_end, y_end = 0, 0, 599, 599
    width, height = 600, 600

    test_with_log()
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
