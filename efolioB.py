#!/usr/bin/python
'''========================================================================
Name        : efolioB.py
Date        : 15.05.2024
Date-of-FIX : 15.07.2024

NOTAS       :


python efolioB.py
============================================================================
'''
import os
import sys
import math
import heapq
import time
from itertools import product


def menu():
    choice = ''
    print("\n\n")
    print("1. Escolher Mapa a Correr ")
    print("2. Correr Todos os Mapas")
    print("\nQ. Quit.\n")

    while choice not in ['1', '2', 'q', 'Q']:
        choice = input("Enter your choice:[1-2](q to quit) ").lower()
    return choice


def mapchoice(prompt, comprido):
    choice = 'N/A'
    lim_min = 0

    while choice.isdigit() is False or (int(choice) not in range(lim_min+1, comprido + 1)):
        choice = input(prompt)
        if choice.isdigit() is False:
            print("NOT A NUMBER")
        elif choice.isdigit() is True:
            if int(choice) not in range(lim_min+1, comprido+1):
                print("NOT IN RANGE[", lim_min+1, "-", comprido, "]")
                choice = 'N/A'
    return int(choice) - 1


def PrintFinalZona(Zona, Custo, SolutnCenters, NrEvals, MapaId):
    linhas = " ---- " * len(Zona[0]) + " "
    TStation = "#"

    print(linhas)
    for r, row in enumerate(Zona):
        row_str = ""
        for c, val in enumerate(row):
            if (r, c) in [(center_row, center_col) for center_row, center_col in SolutnCenters]:
                symbol = TStation
            else:
                symbol = " "
            row_str += f"| {val:2} {symbol}"
        row_str += "|"
        print(row_str)
        print(linhas)

    print(f"MapaID: {MapaId}")
    print(f"Estações Colocadas: {len(SolutnCenters)}")
    for center_row, center_col in SolutnCenters:
        print(f"Centro: ({center_row}, {center_col}) ")
    print(f"Nr. Evals: {NrEvals}")
    print(f"Custo: {Custo}")
    # print("\n")


def loadZone(file_path):
    LstZonas = []
    zona = []

    with open(file_path, 'r') as file:
        zonas = file.read()

    ZonaRows = zonas.split('\n{')
    ZonaRows = [s for s in ZonaRows if "\n/" not in s]
    ZonaRows = [s for s in ZonaRows if "{" not in s]

    for zonaLinhaStr in ZonaRows:
        if zonaLinhaStr.find("\n}") != -1:
            row = zonaLinhaStr.split('},')[0]
            if row:
                currntrow = list(map(int, row.split(',')))
                zona.append(currntrow)
            LstZonas.append(zona)
            zona = []
        else:
            row = zonaLinhaStr.split('},')[0]
            if row:
                currntrow = list(map(int, row.split(',')))
                zona.append(currntrow)
    return LstZonas


# euclidean dist
# def dist(p1, p2):
#     return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# manhattan dist
# def dist(p1, p2):
#     return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# radial dist
def dist(p1, p2):
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    max_delta = max(dx, dy)
    return max_delta


def calc_zone_costs(Zona, zone_centers):
    total_fams = sum(sum(row) for row in Zona)
    costs = 0
    cells_counted = set()

    for r in range(len(Zona)):
        for c in range(len(Zona[0])):
            cell = (r, c)
            min_dist = min(dist(cell, center) for center in zone_centers)
            cell_value = Zona[cell[0]][cell[1]]
            if min_dist <= 1:
                costs += 0
            elif min_dist == 2:
                costs += 1 * cell_value
            elif min_dist == 3:
                costs += 2 * cell_value
            elif min_dist == 4:
                costs += 4 * cell_value
            elif min_dist == 5:
                costs += 8 * cell_value
            else:
                costs += 10 * cell_value

            cells_counted.add(cell)

    if total_fams != 0:
        average_cost = (costs / total_fams)
    else:
        average_cost = 0

    # return math.floor(1000*len(zone_centers) + average_cost * 100)
    return math.floor(average_cost * 100)


def ZoneInitSwipe(zona):
    cell_sums = {}
    for r in range(1, len(zona) - 1):
        for c in range(1, len(zona[0]) - 1):
            total_sum = 0
            total_sum = calc_zone_costs(zona, [(r, c)])
            cell_sums[(r, c)] = total_sum

    # Sort cells based on their sums in descending order
    #sorted_cells = sorted(cell_sums.items(), key=lambda x: x[1], reverse=True)
    sorted_cells = sorted(cell_sums.items(), key=lambda x: x[1])
    # print(sorted_cells)
    sorted_snipped = sorted_cells[:int(len(sorted_cells) * 0.48)]
    return sorted_snipped
    #return sorted_cells


def generate_combinations(centers, radius, zona):
    if not centers:
        return [[]]
    else:
        first, rest = centers[0], centers[1:]
        combinations_without_first = generate_combinations(rest, radius, zona)
        combinations = []
        row, col = first
        for dr, dc in [(0, 0), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]:
            for r in range(1, radius+1):
                new_row, new_col = row + r*dr, col + r*dc
                if (0 <= new_row - 1) and (new_row + 1 < len(zona)) and (0 <= new_col - 1) and (new_col + 1 < len(zona[0])):
                # if 0 <= new_row < len(zona) and 0 <= new_col < len(zona[0]):
                    new_center = (new_row, new_col)
                    combinations_with_first = [[new_center] + combination for combination in combinations_without_first]
                    combinations += combinations_with_first
        return combinations


def a_search(zona, max_iterations=100000):
    # Initialize an empty priority queue
    pqueue = []
    evals = 0
    cost_zone = float('inf')
    new_cost = 0
    BestCost = float('inf')
    # Start at the center of the zona
    pruned = set()
    Zone_Centers = []
    Start = ((len(zona) // 2), (len(zona[0]) // 2))
    # Start = (1, 1)
    Zone_Centers.append(Start)
    BestCenterCfg = []
    Center = []
    StationLmt = 1
    #current_zone_centers = []
    total_fams = sum(sum(row) for row in zona)

    InitCenters = ZoneInitSwipe(zona)
    for Center, SingleCellCost in InitCenters:
        # print(Center, SingleCellCost)
        heapq.heappush(pqueue, (SingleCellCost, [Center]))
        evals += 1
        pruned.add(tuple(sorted([Center])))

    # while pqueue and evals < max_iterations:
    # 1st
    while pqueue:
        # print("Greedy First")
        cost_f, current_zone_centers = heapq.heappop(pqueue)
        #evals += 1

        #pruned.add(tuple(sorted(current_zone_centers)))

        #print(current_zone_centers)
        if 1000*len(current_zone_centers)+cost_f < 1000*len(current_zone_centers)+300:
            if 1000*len(current_zone_centers)+cost_f < BestCost:
                BestCenterCfg = current_zone_centers
                BestCost = 1000*len(current_zone_centers) + cost_f
                StationLmt = len(BestCenterCfg)
                # print("Bst", BestCenterCfg, BestCost)

        #print("1", BestCenterCfg)
        #print("2", current_zone_centers, cost_f, calc_zone_costs_special(zona, BestCenterCfg))
        #print("3", current_zone_centers)
        #print("4", current_zone_centers, cost_f, calc_zone_costs_special(zona, current_zone_centers))
        #print("0Seen: ", pruned)

        # print("B&B")
        # Expand partial solution by adding additional stations
        # if cost_f > 300 and cost_f < 3 * total_fams and len(current_zone_centers) <= StationLmt + 1:
        if cost_f > 300 and len(current_zone_centers) <= StationLmt + 1:
        # if cost_f > 300 and cost_f < 3 * total_fams:
            for i in range(1, len(InitCenters) + 1):
                for j in range(len(InitCenters) - i + 1):
                    new_zone_centers = current_zone_centers.copy()
                    for item, _ in InitCenters[j:j + i]:
                        new_zone_centers.append(item)
                        if tuple(sorted(new_zone_centers)) not in pruned and len(new_zone_centers) <= StationLmt + 3:
                            #print(new_zone_centers)
                            new_cost = calc_zone_costs(zona, new_zone_centers)
                            evals += 1
                            #print(new_zone_centers, new_cost)
                            pruned.add(tuple(sorted(new_zone_centers)))
                            if new_cost < 300 and 1000*len(new_zone_centers) + new_cost < BestCost:
                                heapq.heappush(pqueue, (new_cost, new_zone_centers))
                                StationLmt = len(new_zone_centers)

    # print("Climbing the Hill")
    # 2nd
    # for a in range(len(BestCenterCfg)):
    #     for b in range(len(BestCenterCfg)):
    #         centro_row, centro_col = BestCenterCfg[b]
    #         # E, SE, S, SW, W, NW, N, NE
    #         for radiusR in range(0, 2):
    #             for radiusC in range(0, 2):
    #                 for dr, dc in [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]:
    #                     new_center_row, new_center_col = centro_row + dr * radiusR, centro_col + dc * radiusC
    #                     new_zone_centers = BestCenterCfg[:]
    #                     if (0 <= new_center_row - 1) and (new_center_row + 1 < len(zona)) and (0 <= new_center_col - 1) and (new_center_col + 1 < len(zona[0])) and (new_center_row, new_center_col):
    #                         #if tuple(sorted(new_zone_centers)) not in pruned:
    #                         new_zone_centers[b] = (new_center_row, new_center_col)
    #                         new_cost = calc_zone_costs(zona, new_zone_centers)
    #                         evals += 1
    #                         heapq.heappush(pqueue, (new_cost, new_zone_centers))
    #                         print("ANOTHER BEST: ", new_zone_centers, new_cost)

    # 2nd
    # all_combinations = generate_combinations(BestCenterCfg, 1, zona)
    # for new_zone_centers in all_combinations:
    #     new_cost = calc_zone_costs(zona, new_zone_centers)
    #     evals += 1
    #     heapq.heappush(pqueue, (new_cost, new_zone_centers))
    #     # print("ANOTHER BEST: ", new_zone_centers, new_cost)

    all_combinations = generate_combinations(BestCenterCfg, 2, zona)
    for new_zone_centers in all_combinations:
        new_cost = calc_zone_costs(zona, new_zone_centers)
        evals += 1
        heapq.heappush(pqueue, (new_cost, new_zone_centers))

    while pqueue:
        cost_f, current_zone_centers = heapq.heappop(pqueue)
        if 1000*len(current_zone_centers)+cost_f < 1000*len(current_zone_centers)+300:
            if 1000*len(current_zone_centers)+cost_f < BestCost:
                BestCenterCfg = current_zone_centers
                BestCost = 1000*len(current_zone_centers) + cost_f
                StationLmt = len(BestCenterCfg)
                # print("BstClimb", BestCenterCfg, BestCost)

                all_combinations = generate_combinations(BestCenterCfg, 1, zona)
                for new_zone_centers in all_combinations:
                    new_cost = calc_zone_costs(zona, new_zone_centers)
                    evals += 1
                    heapq.heappush(pqueue, (new_cost, new_zone_centers))
                    # print("ANOTHER BEST: ", new_zone_centers, new_cost)


    return BestCenterCfg, evals


def main():
    fnZones = "zonas.txt"
    final_evaluations = 0

    LstZones = loadZone(os.path.join(sys.path[0], fnZones))

    while True:
        choice = menu()
        if choice == '1':
            # print("\033[H\033[J", end="")  # clear screen
            choice = mapchoice("Qual o mapa ?  ", len(LstZones))
            # print(LstZones[choice], "\n")
            # print(zone_init_swipe(LstZones[choice]))
            # result = branch_and_bound(LstZones[choice])
            # result = a_star_search(LstZones[choice], 100000)
            current_time = time.localtime()
            print(f"Current time: {time.strftime('%H:%M:%S', current_time)}")
            start_time = time.time()
            result, final_evaluations = a_search(LstZones[choice], 100000)
            end_time = time.time()
            total_fams = sum(sum(row) for row in LstZones[choice])
            fams_cost = calc_zone_costs(LstZones[choice], result)
            PrintFinalZona(LstZones[choice], 1000*len(result)+fams_cost, result, final_evaluations, choice + 1)
            # fams_cost = calc_zone_costs(LstZones[choice], [(2, 2), (4, 5)])
            print("total familias: ", total_fams)
            # print("Cell Centers Explored:", result)
            # fams_cost = calc_zone_costs(LstZones[choice], [(1, 5)])
            # print("Custo: ", 1000*len(result)+fams_cost)
            # fams_cost = calc_zone_costs(LstZones[choice], [(2, 4)])
            # print("Custo: ", 1000*len(result)+fams_cost)
            # fams_cost = calc_zone_costs(LstZones[choice], [(2, 5)])
            # print("Custo: ", 1000*len(result)+fams_cost)
            # fams_cost = calc_zone_costs(LstZones[choice], [(4, 3), (6, 7)])
            # print("Custo: ", 1000*len(result)+fams_cost)
            # fams_cost = calc_zone_costs(LstZones[choice], [(5, 7), (3, 7), (2, 6)])
            # print("Custo: ", 1000*len(result)+fams_cost)
            # fams_cost = calc_zone_costs(LstZones[choice], [(len(LstZones[choice]) // 2, len(LstZones[choice][0]) // 2)])
            # print("Custo: ", 1000*len(result)+fams_cost)

            #max_bus_stops = 5  # Example limit on the maximum number of bus stops
            #result = branch_and_bound_search(LstZones[choice], max_bus_stops)

            #if result:
            #    bus_stops, total_cost, average_cost = result
            #    print("Bus Stops:", bus_stops)
            #    print("Total Cost:", total_cost)
            #    print("Average Cost:", average_cost)
            #else:
            #    print("No valid solution found.")
            execution_time = end_time - start_time
            minutes = int(execution_time // 60)
            seconds = int(execution_time % 60)
            print("Tempo exec: {} min(s) e {} seg(s) \n\n".format(minutes, seconds))

        elif choice == '2':
            # print("\033[H\033[J", end="")  # clear screen
            for i, map in enumerate(LstZones):
                #PrintFinalZona(map, 0, [((len(map) // 2), len(map[0]) // 2)], 0, i + 1)
                # print(map, "\n")
                current_time = time.localtime()
                print(f"Current time: {time.strftime('%H:%M:%S', current_time)}")
                start_time = time.time()
                result, final_evaluations = a_search(map, 100000)
                end_time = time.time()

                total_fams = sum(sum(row) for row in map)
                fams_cost = calc_zone_costs(map, result)
                PrintFinalZona(map, 1000*len(result)+fams_cost, result, final_evaluations, i + 1)
                # fams_cost = calc_zone_costs(LstZones[choice], [(2, 2), (4, 5)])
                print("total familias: ", total_fams)

                execution_time = end_time - start_time
                minutes = int(execution_time // 60)
                seconds = int(execution_time % 60)
                print("Tempo exec: {} min(s) e {} seg(s) ".format(minutes, seconds))
                print("\n\n")
                # print(zone_init_swipe(map))
        elif choice == 'q':
            # print("\033[H\033[J", end="")  # clear screen
            print("Exiting the program...")
            return
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
