from .jobshop import *

import math
import random
import time


def getNeigbors(state, mode="normal"):
    allNeighbors = []

    for i in range(len(state)-1):
        neighbor = state[:]
        if mode == "normal":
            swapIndex = i + 1
        elif mode == "random":
            swapIndex = random.randrange(len(state))
        neighbor[i], neighbor[swapIndex] = neighbor[swapIndex], neighbor[i]
        allNeighbors.append(neighbor)

    return allNeighbors


def simulatedAnnealing(jobs, T, termination, halting, mode, decrease, mytest: int):
    numberOfJobs = len(jobs)
    numberOfMachines = len(jobs[0])
    shod = []
    state = randomSchedule(numberOfJobs, numberOfMachines)

    for i in range(halting):
        T = decrease * float(T)

        for k in range(termination):
            actualCost = cost(jobs, state)

            for n in getNeigbors(state, mode):
                nCost = cost(jobs, n)
                if nCost < actualCost:
                    state = n
                    actualCost = nCost
                else:
                    probability = math.exp(-nCost/T)
                    if random.random() < probability:
                        state = n
                        actualCost = nCost
                if mytest == 1:
                    shod.append(actualCost)

    return actualCost, state, shod



def simulatedAnnealingSearch(jobs, maxTime=None, T=200, termination=10, halting=10, mode="random", decrease=0.8):
    numExperiments = 1

    solutions = []
    best = 10000000

    t0 = time.time()
    totalExperiments = 0

    j = len(jobs)
    m = len(jobs[0])
    rs = randomSchedule(j, m)

    #a, b, c = simulatedAnnealing(jobs, T=T, termination=termination, halting=halting, mode=mode,   decrease=decrease, mytest=1)
    #return c
    while True:
        try:
            start = time.time()

            for i in range(numExperiments):
                cost, schedule, f = simulatedAnnealing(jobs, T=T, termination=termination, halting=halting, mode=mode, decrease=decrease, mytest=0)

                if cost < best:
                    best = cost
                    solutions.append((cost, schedule))

            totalExperiments += numExperiments

            if maxTime and time.time() - t0 > maxTime:
                raise OutOfTime("Time is over")

            t = time.time() - start
            if t > 0:
                print("Best:", best, "({:.1f} Experiments/s, {:.1f} s)".format(
                        numExperiments/t, time.time() - t0))

            if t > 4:
                numExperiments //= 2
                numExperiments = max(numExperiments, 1)
            elif t < 1.5:
                numExperiments *= 2

        except (KeyboardInterrupt, OutOfTime) as e:
            print()
            print("================================================")
            print("Best solution:")
            print(solutions[-1][1])
            print("Found in {:} experiments in {:.1f}s".format(totalExperiments, time.time() - t0))

            return solutions[-1]


def classic2n(jobs):
    I1 = []
    I2 = []
    I12 = []
    I21 = []
    for i in range(0, len(jobs)):
        if jobs[i][0][0] == 0:
            if jobs[i][0][1] == 0: # гарантируем, что хотя бы на одной машине работа выполняется
                I2.append(jobs[i])
                I2.pop([len(I2)-1][0]) # т е убираем ненужные нули
            elif jobs[i][1][1] == 0:
                I1.append(jobs[i])
                I1.pop([len(I1)-1][1])
            else:
                I12.append(jobs[i])
        else:
            if jobs[i][0][1] == 0:  # гарантируем, что хотя бы на одной машине работа выполняется
                I1.append(jobs[i])
                I1.pop([len(I1) - 1][0])
            elif jobs[i][1][1] == 0:
                I2.append(jobs[i])
                I2.pop([len(I2) - 1][1])
            else:
                I21.append(jobs[i])

    NI12 = flow2n(I12)
    NI21 = flow2n(I21)
    L1, L2 = costNI(NI12, 0, 0)
    NL1, Nl2 = costNI(NI21, L2, L1) #NL1 - ДЛИНА НА 2 МАШИНЕ, nl2 - ДЛИНА НА ПЕРВОЙ

    R1 = costSimple(I1,Nl2)
    R2 = costSimple(I2,NL1)

    return max(R1,R2)





def costNI(I,a,b):
    sum1 = a
    sum2 = b
    for i in range(0, len(I)):
        sum1 = sum1 + I[i][0][1]
        if sum1 > sum2:
            sum2 = (sum2 - sum1) + sum2 + I[i][1][1]
        else:
            sum2 = sum2 + I[i][1][1]

    return sum1, sum2


def costSimple(I,a):
    sum = a
    for i in range(0, len(I)):
        sum = sum + I[i][0][1]
    return sum


def flow2n(I):
    s1 = []
    s2 = []
    for i in range(0, len(I)):
        if I[i][0][1] < I[i][1][1]:
            s1.append(I[i])
        else:
            s2.append(I[i])

    NI = [[]]
    k = 0
    min = s1[0][0][1]
    mk = 0
    while len(s1) != 0:
        for i in range(0, len(s1)):
            if min > s1[i][0][1]:
                min = s1[i][0][1]
                mk = i

        NI[0].append(s1[mk])
        s1.pop(mk)
        if len(s1) != 0:
            min = s1[0][0][1]

    k = 0
    max = s2[0][1][1]
    mk = 0
    while len(s2) != 0:
        for i in range(0, len(s2)):
            if max > s2[i][1][1]:
                max = s1[i][1][1]
                mk = i

        NI[0].append(s2[mk])
        s2.pop(mk)
        if len(s2) != 0:
            max = s2[0][0][1]

    return NI



