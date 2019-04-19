def Yura_func(filename, coordinates):
    # angles are deposited clockwise from the direction right??

    # always: CCW - CW < 180 < CW - CCW

    import numpy
    import scipy.optimize as opt
    from enum import Enum
    import Graph

    eps = 0.0001

    class Direction(Enum):
        CONTERCW = 1
        CLOCKWISE = 2

    class MainPointInBadZoneError(Exception):
        def __init__(self, text):
            self.txt = text

    class RoutePlanSoftError(Exception):
        pass

    class Arc():
        def __init__(self, X0, Y0, R, A1, A2, DIR):
            super().__init__()
            self.x0 = X0
            self.y0 = Y0
            self.r = R
            self.a1 = A1
            self.a2 = A2
            self.dir = DIR

    # find angle between two points at circle
    def roundDistance(a1, a2):
        d = abs(a1 - a2)
        if d > numpy.pi:
            d = 2*numpy.pi - d
        return  d

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
                                                       line[2] - line[0])], [round[0], round[0]])

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
                print("{}, {}, {}, {} - {}, {}, {}, {}".format(previous_arc.x0, previous_arc.y0, previous_arc.r, previous_arc.a2, arc.x0, arc.y0, arc.r, arc.a1))
                a_1, a_2, d1, d2 = createCompound(previous_arc, arc)
                previous_arc.a2 = a_1
                arc.a1 = a_2

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

    # construct compounds (angel) between two circles and find more fit
    def createCompound(arc1, arc2):

        # if arc1.x0 == 500 and arc1.y0 == 400 and arc2.x0 == 500 and arc2.y0 == 460:
        #     print("-")

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
        else:
            a1_internal, a2_internal = numpy.nan, numpy.nan
            a1_dir_int = Direction.CLOCKWISE
        # print("a1_ext = {}, a2_ext = {}, a1_int = {}, a2_int = {}".format(a1_external, a2_external, a1_internal, a2_internal))

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

    # find angle of point of contact of round and tangent where tangent goes through the point A(XA, YA)
    def createTangent(XA, YA, X0, Y0, R):
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

    # main function that create route throuth field
    def CreateRoute(startX, startY, endX, endY, width, height, red_zone):
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
            n=1
            while n>0:
                n = clarifyRoute(pointed_route, red_zone)
        except MainPointInBadZoneError as err:
            print("Error: {}".format(err))
            pointed_route[1]=pointed_route[0]
        return pointed_route


    # route = [Arc(0,0,0,0,0,Direction.CONTERCW),Arc(599,599,0,0,0,Direction.CONTERCW)]
    rounds = [(85,80,6), (15, 16, 9), (50, 0, 8), (60, 62, 4), (200, 100, 85), (400, 360, 76), (500, 100, 50), (560, 540, 15), (380, 350, 6), (200, 280, 30), (360, 450, 100), (500, 400, 60)]
    # rounds = [(90, 60, 20), (150, 150, 30), (500, 540, 50), (300, 340, 60)]
    # rounds = [(200, 0, 20), (200, 20, 20), (200, 50, 20), (200, 80, 20), (200, 100, 20), (200, 110, 20), (200, 145, 20), (200, 160, 20), (210, 180, 20), (200, 200, 20), (200, 235, 20), (195, 265, 20), (200, 300, 20)]
    # rounds = sorted(rounds, key=lambda round: round[2], reverse=True)
    print(rounds)


    x_start, y_start, x_end, y_end = int(coordinates[0]), int(coordinates[1]), int(coordinates[2]), int(coordinates[3])
    width, height = 600, 600
    route = CreateRoute(x_start,y_start,x_end,y_end,width,height,rounds)
    #
    # n = 1
    # while n>0:
    #     n = clarifyRoute(route, rounds)
        # print("-----------------------------------------------")
        # for i in route:
        #     print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}".format(i.x0, i.y0, i.r, i.a1, i.a2))
        # print("-----------------------------------------------")

    for i in route:
        print("x = {}, y = {}, r = {}, a1 = {}, a2 = {}, dir = {}".format(i.x0, i.y0, i.r, i.a1, i.a2, i.dir))

    Graph.full_map_conjunction(filename)
    for i in rounds:
        Graph.circle_draw(i[0], i[1], i[2])
    i_pr = route[0]
    for i in route:
        Graph.draw_line((int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)), (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)), (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)), (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1)))
        i_pr = i