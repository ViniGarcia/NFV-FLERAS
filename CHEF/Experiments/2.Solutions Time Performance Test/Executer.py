import MehOriginal
import MehIndex
import MehMulti
import MijOriginal
import MijIndex
import MijMulti

import time
import statistics

class Executer:
    mehOExhaustive = None
    mehOGreedy = None
    mijOGreedy = None

    mehIExhaustive = None
    mehIGreedy = None
    mijIGreedy = None

    mehMExhaustive = None
    mehMGreedy = None
    mijMGreedy = None

    repeats = None

    def __init__(self):

        self.mehOExhaustive = MehOriginal.Composer(1)
        self.mehOGreedy = MehOriginal.Composer(2)
        self.mijOGreedy = MijOriginal.Processor()

        self.mehIExhaustive = MehIndex.Composer(1)
        self.mehIGreedy = MehIndex.Composer(2)
        self.mijIGreedy = MijIndex.Processor()

        self.mehMExhaustive = MehMulti.Composer(1)
        self.mehMGreedy = MehMulti.Composer(2)
        self.mijMGreedy = MijMulti.Processor()

        self.repeats = 30

    def mehExhaustiveTest(self, originalFile, multiFile):
        original = []
        index = []
        multi = []

        for i in range(self.repeats):
            start_time = time.time()
            self.mehOExhaustive.cCompose(originalFile)
            original.append(time.time() - start_time)

        for i in range(self.repeats):
            start_time = time.time()
            self.mehIExhaustive.cCompose(originalFile)
            index.append(time.time() - start_time)

        for i in range(self.repeats):
            start_time = time.time()
            self.mehMExhaustive.cCompose(multiFile)
            multi.append(time.time() - start_time)

        mean = statistics.mean(original)
        stdev = statistics.stdev(original)
        original.append(mean)
        original.append(stdev)

        mean = statistics.mean(index)
        stdev = statistics.stdev(index)
        index.append(mean)
        index.append(stdev)

        mean = statistics.mean(multi)
        stdev = statistics.stdev(multi)
        multi.append(mean)
        multi.append(stdev)

        return(original, index, multi)

    def mehGreedyTest(self, originalFile, multiFile):
        original = []
        index = []
        multi = []

        for i in range(self.repeats):
            start_time = time.time()
            self.mehOGreedy.cCompose(originalFile)
            original.append(time.time() - start_time)

            start_time = time.time()
            self.mehIGreedy.cCompose(originalFile)
            index.append(time.time() - start_time)

            start_time = time.time()
            self.mehMGreedy.cCompose(multiFile)
            multi.append(time.time() - start_time)

        mean = statistics.mean(original)
        stdev = statistics.stdev(original)
        original.append(mean)
        original.append(stdev)

        mean = statistics.mean(index)
        stdev = statistics.stdev(index)
        index.append(mean)
        index.append(stdev)

        mean = statistics.mean(multi)
        stdev = statistics.stdev(multi)
        multi.append(mean)
        multi.append(stdev)

        return(original, index, multi)

    def mijGreedyTest(self, originalFile, multiFile):
        original = []
        index = []
        multi = []

        for i in range(self.repeats):
            start_time = time.time()
            self.mijOGreedy.cCompose(originalFile)
            original.append(time.time() - start_time)

            start_time = time.time()
            self.mijIGreedy.cCompose(originalFile)
            index.append(time.time() - start_time)

            start_time = time.time()
            self.mijMGreedy.cCompose(multiFile)
            multi.append(time.time() - start_time)

        mean = statistics.mean(original)
        stdev = statistics.stdev(original)
        original.append(mean)
        original.append(stdev)

        mean = statistics.mean(index)
        stdev = statistics.stdev(index)
        index.append(mean)
        index.append(stdev)

        mean = statistics.mean(multi)
        stdev = statistics.stdev(multi)
        multi.append(mean)
        multi.append(stdev)

        return(original, index, multi)

    def mehExhRequest(self, path, base, idinit, idfinal):

        print("---- MEHRAGHDAM EXHAUSTIVE LOG ---- \n")
        for index in range(idinit, idfinal+1):
            originalFile = path + base + str(index) + ".yaml"
            multiFile = path + base + "Multi" + str(index) + ".yaml"
            result = self.mehExhaustiveTest(originalFile, multiFile)
            print(originalFile + " ORIGINAL -> MEAN: " + str(result[0][-2]) + "  STDEV: " + str(result[0][-1]))
            print(originalFile + " INDEX -> MEAN: " + str(result[1][-2]) + "  STDEV: " + str(result[1][-1]))
            print(multiFile + " MULTI -> MEAN: " + str(result[2][-2]) + "  STDEV: " + str(result[2][-1]) + "\n")

    def mehGreRequest(self, path, base, idinit, idfinal):

        print("---- MEHRAGHDAM GREEDY LOG ---- \n")
        for index in range(idinit, idfinal+1):
            originalFile = path + base + str(index) + ".yaml"
            multiFile = path + base + "Multi" + str(index) + ".yaml"
            result = self.mehGreedyTest(originalFile, multiFile)
            print(originalFile + " ORIGINAL -> MEAN: " + str(result[0][-2]) + "  STDEV: " + str(result[0][-1]))
            print(originalFile + " INDEX -> MEAN: " + str(result[1][-2]) + "  STDEV: " + str(result[1][-1]))
            print(multiFile + " MULTI -> MEAN: " + str(result[2][-2]) + "  STDEV: " + str(result[2][-1]) + "\n")

    def mijRequest(self, path, base, idinit, idfinal):

        print("---- MIJUMBI GREEDY LOG ---- \n")
        for index in range(idinit, idfinal+1):
            originalFile = path + base + str(index) + ".yaml"
            multiFile = path + base + "Multi" + str(index) + ".yaml"
            result = self.mehGreedyTest(originalFile, multiFile)
            print(originalFile + " ORIGINAL -> MEAN: " + str(result[0][-2]) + "  STDEV: " + str(result[0][-1]))
            print(originalFile + " INDEX -> MEAN: " + str(result[1][-2]) + "  STDEV: " + str(result[1][-1]))
            print(multiFile + " MULTI -> MEAN: " + str(result[2][-2]) + "  STDEV: " + str(result[2][-1]) + "\n")

tester = Executer()
tester.mehExhRequest("Test/", "mehDocument", 1, 7)
tester.mehGreRequest("Test/", "mehDocument", 1, 7)
tester.mijRequest("Test/", "mijDocument", 1, 7)
