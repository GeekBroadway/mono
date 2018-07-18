#!/usr/bin/python3

import os,re,zipfile,shutil,argparse,hashlib,json,time

parser = argparse.ArgumentParser(description="Process Minecraft mod jar and zip files into suitable zips for technic solder")
parser.add_argument('-i', action="store", default="mods/", metavar="inputDir/",
	help="Input directory containing mods")
parser.add_argument('-o', action="store", default="solderZips/", metavar="outputDir/",
	help="Output Directory for parsed solder mods")
args = parser.parse_args()
mypath = args.i
outputDir = args.o
def makeModZip(modDictionary, nameVersionDictionary):
	print("\033[93mBeggining Mod Zip Creation\033[0m")
	for mod,filepath in sorted(modDictionary.items()):
		print("Name: \033[92m"+mod+"\033[0m, filepath: \033[94m"+outputDir+mod+"/"+mod+"-"+nameVersionDictionary[mod]+"\033[0m")
		workingDir = "/tmp/autozipper/"+mod+"/mods/"
		if not os.path.exists(workingDir):
			os.makedirs(workingDir)
		shutil.copyfile(mypath+filepath, workingDir+filepath)
		shutil.make_archive(outputDir+mod+"/"+mod+"-"+nameVersionDictionary[mod], "zip", "/tmp/autozipper/"+mod)
		shutil.rmtree("/tmp/autozipper/"+mod)
def parseModDirectory(modPath):
	modFileNames = []
	modNames = []
	for file in os.listdir(modPath):
		if file.endswith(".jar"):
			modFileNames.append(file)
		elif file.endswith(".zip"):
			modFileNames.append(file)
	for modFileName in modFileNames:
		modName = re.match('(^.+?)(?=-|_| |\[)', modFileName)
		if (modName == None):
			matchNumberedName = re.match('(^.+?)(?=[0-9])', modFileName)
			modNames.append(matchNumberedName.group(0))
			continue
		modNames.append(modName.group(0))
	modDict = dict(zip(modNames, modFileNames))
	return modDict
def writeDictToFile(Dictionary, myfile):
	with open(myfile, 'w') as f:
		for key, value in Dictionary.items():
			f.write('%s:%s\n' % (key, value))
def makeConfigZip():
	if os.path.exists("config/"):
		print("\033[93mCreating Config Zip\033[0m")
		tempDir = "/tmp/autozipper/config/"
		if not os.path.exists(tempDir):
			os.makedirs(tempDir)
		shutil.copytree("config/", tempDir+"config")
		shutil.make_archive("configs", "zip", tempDir)
		shutil.rmtree(tempDir)
	else:
		print("\033[91mNo Config Directory Found, skipping config zip creation\033[0m")
def genNameVersionDictionary(modDictionary):
	nameVersionDict = {}
	for mod,filepath in sorted(modDictionary.items()):
		modVersion = re.findall('(?<=-|_| |\[)(.+)', os.path.splitext(filepath)[0])
		if (modVersion == []):
			modVersion = re.findall('(?<=[0-9])(.+)', filepath)
			nameVersionDict[mod] = modVersion[0]
			continue
		nameVersionDict[mod] = modVersion[0]
	writeDictToFile(nameVersionDict, "version-"+str(time.time())+".txt")
	return nameVersionDict
def generateMD5List():
	packagedZipNames = []
	md5Array = []
	for file in os.listdir(outputDir):
		if file.endswith(".zip"):
			packagedZipNames.append(file)
	for packagedZip in (packagedZipNames):
		md5Array.append(hashlib.md5(open(outputDir+packagedZip, 'rb').read()).hexdigest())
	md5Dict = dict(zip(packagedZipNames, md5Array))
	for filename,ziphash in sorted(md5Dict.items()):
		print("Filename: \033[92m"+filename+"\033[0m, hash: \033[94m"+ziphash+"\033[0m")

##Main Running
modDictionary = parseModDirectory(mypath)
nameVerDict = genNameVersionDictionary(modDictionary)
makeModZip(modDictionary, nameVerDict)
#Package Zips
shutil.make_archive("repo-"+str(time.time()), "zip", outputDir)
#generateMD5List()

