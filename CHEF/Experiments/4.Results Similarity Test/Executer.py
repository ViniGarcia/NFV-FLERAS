import MehOriginal
import MehIndex
import MehMulti
import MijOriginal
import MijIndex
import MijMulti

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

    def mehCompare(self, filesOriginal, filesMulti):

        print("---- MEHRAGHDAM RESULTS ----")
        for index in range(len(filesOriginal)):
            self.mehOExhaustive.cCompose(filesOriginal[index])
            eResult = self.mehOExhaustive.cFirmSuggestion()
            self.mehOGreedy.cCompose(filesOriginal[index])
            gResult = self.mehOGreedy.cFirmSuggestion()

            self.mehIExhaustive.cCompose(filesOriginal[index])
            eiResult = self.mehIExhaustive.cFirmSuggestion()
            self.mehIGreedy.cCompose(filesOriginal[index])
            giResult = self.mehIGreedy.cFirmSuggestion()

            self.mehMExhaustive.cCompose(filesMulti[index])
            emResult = self.mehMExhaustive.cFirmSuggestion()
            self.mehMGreedy.cCompose(filesMulti[index])
            gmResult = self.mehMGreedy.cFirmSuggestion()            

            print("File: " + str(filesOriginal[index]))
            if eResult == eiResult and eResult == emResult:
                print("Exhaustive: True")
            else:
                print("Exhaustive: False")
            if gResult == giResult and gResult == gmResult:
                print("Greedy: True")
            else:
                print("Greedy: False")
        print()

    def mijCompare(self, filesOriginal, filesMulti):

        print("---- MIJUMBI RESULTS ----")
        for index in range(len(filesOriginal)):
            self.mijOGreedy.pProcess(filesOriginal[index])
            gResult = self.mijOGreedy.pSuggestion()

            self.mijIGreedy.pProcess(filesOriginal[index])
            giResult = self.mijIGreedy.pSuggestion()
            
            self.mijMGreedy.pProcess(filesMulti[index])
            gmResult = self.mijMGreedy.pSuggestion()

            print("File: " + str(filesOriginal[index]))
            if gResult == giResult and gResult == gmResult:
                print("Greedy: True")
            else:
                print("Greedy: False")

    def mehRequest(self, path, base, idinit, idfinal):

        filesOriginal = []
        filesMulti = []
        for index in range(idinit, idfinal+1):
            filesOriginal.append(path + base + str(index) + ".yaml")
            filesMulti.append(path + base + "Multi" + str(index) + ".yaml")
        self.mehCompare(filesOriginal, filesMulti)

    def mijRequest(self, path, base, idinit, idfinal):

        filesOriginal = []
        filesMulti = []
        for index in range(idinit, idfinal+1):
            filesOriginal.append(path + base + str(index) + ".yaml")
            filesMulti.append(path + base + "Multi" + str(index) + ".yaml")
        self.mijCompare(filesOriginal, filesMulti)

tester = Executer()
tester.mehRequest("Test/", "mehDocument", 1, 28)
tester.mijRequest("Test/", "mijDocument", 1, 8)