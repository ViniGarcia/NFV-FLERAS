import MehMulti

import time
import statistics

class Executer:
    mehMExhaustive = None
    mehMGreedy = None

    repeats = None

    def __init__(self):

        self.mehMExhaustive = MehMulti.Composer(1)
        self.mehMGreedy = MehMulti.Composer(2)

        self.repeats = 30

    def mehExhaustiveTest(self, file):
        measuremnts = []

        for i in range(self.repeats):
            start_time = time.time()
            self.mehMExhaustive.cCompose(file)
            measuremnts.append(time.time() - start_time)

        mean = statistics.mean(measuremnts)
        stdev = statistics.stdev(measuremnts)

        return (mean, stdev)

    def mehGreedyTest(self, file):
        measuremnts = []

        for i in range(self.repeats):

            start_time = time.time()
            self.mehMGreedy.cCompose(file)
            measuremnts.append(time.time() - start_time)

        mean = statistics.mean(measuremnts)
        stdev = statistics.stdev(measuremnts)

        return(mean, stdev)


    def mehExhRequest(self, path, base, idinit, idfinal):

        print("---- MEHRAGHDAM EXHAUSTIVE LOG ---- \n")
        for index in range(idinit, idfinal+1):
            file = path + base + "Multi" + str(index) + ".yaml"
            result = self.mehExhaustiveTest(file)
            print(file + " -> TIME MEAN: " + str(result[0]) + "  STDEV: " + str(result[1]))
            print(file + " -> RESULT: " + str(self.mehMExhaustive.cSuggestion()) + ", SI: " + str(self.mehMExhaustive.cSI()) + "\n")

    def mehGreRequest(self, path, base, idinit, idfinal):

        print("---- MEHRAGHDAM GREEDY LOG ---- \n")
        for index in range(idinit, idfinal+1):
            file = path + base + "Multi" + str(index) + ".yaml"
            result = self.mehGreedyTest(file)
            print(file + " -> TIME MEAN: " + str(result[0]) + "  STDEV: " + str(result[1]))
            print(file + " -> RESULT: " + str(self.mehMGreedy.cSuggestion()) + "\n")


tester = Executer()
tester.mehExhRequest("Test/", "mehDocumentMulti", 1, 4)
tester.mehGreRequest("Test/", "mehDocumentMulti", 1, 4)