import os.path

def prepareOutputFile(inputFile, inputDir, outputDir):
    outputFile = inputFile.replace(inputDir,outputDir,1)
    outputFile = os.path.splitext(outputFile)[0] + '.xml'

    outputFileDir = os.path.dirname(outputFile)
    if not os.path.exists(outputFileDir):
        os.makedirs(outputFileDir)

    return outputFile
