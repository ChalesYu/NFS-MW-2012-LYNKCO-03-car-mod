from inc_noesis import *
from contextlib import contextmanager
import os
import sys
import binascii
import shutil
import zlib

# Multi unpack option:
unpack_to_same_folder = False   # True: the extracted files will be located in the same directory
                                # False: the extracted files will be located inside a folder named as the source BIN/BNDL file (best option)

def registerNoesisTypes():
	handle = noesis.registerTool("&Need for Speed Most Wanted 2012 Unpacker", makeNFSMWToolMethod, "Unpack a Need for Speed Most Wanted 2012 file")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	return 1

def noepyCheckType(data):
	bs = NoeBitStream(data)
	Magic = bs.readBytes(4)
	if Magic != b'bnd2':
		return 0
	return 1

def validateInput(inVal):
	if os.path.exists(inVal) is not True:
		return "'" + inVal + "' does not exist!"
	return None

def validateInput2(inVal):
	if os.path.exists(inVal) is not True:
		os.makedirs(inVal)
	return None

def makeNFSMWToolMethod(toolIndex):
	srcName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select a file to unpack.", noesis.getSelectedFile(), validateInput)
#	srcName="C:\\Need for Speed(TM) Most Wanted\\MOD\\VEH_122701_HI.BNDL"
	if srcName is None:
		return 0
	saveDir = noesis.userPrompt(noesis.NOEUSERVAL_FOLDERPATH, "Open Folder", "Select a folder to save the unpacked files.", noesis.getSelectedDirectory(), validateInput2)
#	saveDir="C:\\Need for Speed(TM) Most Wanted\\MOD\\a"
	if saveDir is None:
		return 0
	noesis.logPopup()
	if os.path.isfile(srcName):
		main(srcName, saveDir)
	else:
		for File in os.listdir(srcName):
			srcName1 = srcName + "\\" +  File
			Name, ext = os.path.splitext(os.path.basename(srcName1))
			saveDir0 = saveDir + "\\" + Name		#Separated by folder
			if unpack_to_same_folder:
				saveDir0 = saveDir						#Same folder
			if os.path.isfile(srcName1):
				if os.path.exists(saveDir0) is not True:
					os.makedirs(saveDir0)
				print("Unpacking file:", File)
				with suppress_stdout():
					main(srcName1, saveDir0)
				IDsName = saveDir0 + "\\IDs.BIN"
				if os.path.exists(IDsName):
					Name, ext = os.path.splitext(os.path.basename(srcName1))
					IDsName2 = saveDir0 + "\\IDs_" + Name + ".BIN"
					shutil.copy2(IDsName, IDsName2)
					os.remove(IDsName)
				ResourceStringTableName = saveDir0 + "\\ResourceStringTable.xml"
				if os.path.exists(ResourceStringTableName):
					Name, ext = os.path.splitext(os.path.basename(srcName1))
					ResourceStringTableName2 = saveDir0 + "\\ResourceStringTable_" + Name + ".xml"
					shutil.copy2(ResourceStringTableName, ResourceStringTableName2)
					os.remove(ResourceStringTableName)
		print("Done.")
		noesis.messagePrompt("Successfully unpacked the files.")
	return 1

def main(srcName, saveDir):
	g = open(srcName, "rb")
	id = noeStrFromBytes(g.read(4))
	g.seek(0x2, NOESEEK_REL)
	version = g.read(2)
	g.close()
	if version == b'\x01\x00':
		version = "PC"
		print("Game version:", version)
		NFSMW2012_PCMethod(srcName, saveDir)
	elif version == b'\x00\x03':
		version = "XBOX"
		print("Game version:", version)
		print("Not working yet, I need some samples")
		#NFSMW2012_XBOXMethod(srcName, saveDir)	#Script not tested
	elif version == b'\x00\x02':
		version = "PS3"
		print("Game version:", version)
		NFSMW2012_PS3Method(srcName, saveDir)
	else:
		version = "Unknown"
		print("Game version:", version)
	return 1

def NFSMW2012_PCMethod(srcName, saveDir):
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	with open(srcName, "rb") as f:
		id = noeStrFromBytes(f.read(4))
		f.seek(0xC, NOESEEK_ABS)
		NumIDs, IDsTab_start, Block1_start, Block2_start, Block3_start, Fullsize, Compression = noeUnpack("<iiiiiii", f.read(28))
		f.seek(IDsTab_start, NOESEEK_ABS)
		print("Unpacking", NumIDs, "files from archive.")
		IDsList = []
		for i in range(0, NumIDs):
			print("Unpacking file", i+1)
			f.seek(IDsTab_start + i*0x48, NOESEEK_ABS)
			name = f.read(4)
			name = binascii.hexlify(name)
			name = str(name,'ascii')
			name = name.upper()
			name = name[0]+name[1]+"_"+name[2]+name[3]+"_"+name[4]+name[5]+"_"+name[6]+name[7]
			#print(name, ":name")
			countBlock, unk1 = noeUnpack("<BB", f.read(2))
			count, unk2 = noeUnpack("<BB", f.read(2))
			decompSize1, decompSize2 = noeUnpack("<iI", f.read(8))
			f.seek(0x8, NOESEEK_REL)
			compSize1, compSize2 = noeUnpack("<ii", f.read(8))
			f.seek(0x8, NOESEEK_REL)
			position1, position2 = noeUnpack("<ii", f.read(8))
			f.seek(0x8, NOESEEK_REL)
			called_block = noeUnpack("<i", f.read(4))[0]
			type = f.read(4)
			type = binascii.hexlify(type)
			type = str(type,'ascii')
			type = type.upper()
			type = type[0]+type[1]+"_"+type[2]+type[3]+"_"+type[4]+type[5]+"_"+type[6]+type[7]
			Num_int_IDs = noeUnpack("<H", f.read(2))[0]
			#print(type, ":type")
			#ID2List = name + "_" + type
			#if ID2List in IDsList:
			#	count = 1
			#	ID2List = name + "_" + str(count) + "_" + type
			#	while ID2List in IDsList:
			#		count +=1
			#		ID2List = name + "_" + str(count) + "_" + type
			#	name += "_" + str(count)
			#	ID2List = name + "_" + type
			#IDsList.append(ID2List)
			if countBlock != 0:
				name += "_" + str(countBlock) 
				if count != 0:
					name += "_" + str(count)
			elif countBlock == 0 and count != 0:
				name += "_" + str(countBlock)
				name += "_" + str(count)
			if decompSize1 >= 0x90000000:
				decompSize1 = decompSize1 - 0x90000000
			elif decompSize1 >= 0x80000000:
				decompSize1 = decompSize1 - 0x80000000
			elif decompSize1 >= 0x70000000:
				decompSize1 = decompSize1 - 0x70000000
			elif decompSize1 >= 0x60000000:
				decompSize1 = decompSize1 - 0x60000000
			elif decompSize1 >= 0x50000000:
				decompSize1 = decompSize1 - 0x50000000
			elif decompSize1 >= 0x40000000:
				decompSize1 = decompSize1 - 0x40000000
			elif decompSize1 >= 0x30000000:
				decompSize1 = decompSize1 - 0x30000000
			elif decompSize1 >= 0x20000000:
				decompSize1 = decompSize1 - 0x20000000
			elif decompSize1 >= 0x10000000:
				decompSize1 = decompSize1 - 0x10000000
			if decompSize2 >= 0xC0000000:
				decompSize2 = decompSize2 - 0xC0000000
			elif decompSize2 >= 0x70000000:
				decompSize2 = decompSize2 - 0x70000000
			elif decompSize2 >= 0x60000000:
				decompSize2 = decompSize2 - 0x60000000
			elif decompSize2 >= 0x50000000:
				decompSize2 = decompSize2 - 0x50000000
			elif decompSize2 >= 0x40000000:
				decompSize2 = decompSize2 - 0x40000000
			elif decompSize2 >= 0x30000000:
				decompSize2 = decompSize2 - 0x30000000
			elif decompSize2 >= 0x20000000:
				decompSize2 = decompSize2 - 0x20000000
			elif decompSize2 >= 0x10000000:
				decompSize2 = decompSize2 - 0x10000000
			f.seek(Block1_start + position1, NOESEEK_ABS)
			if Compression == 0x2:
				Data = f.read(decompSize1)
			elif Compression == 0x1:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x5:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x9:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x21:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x29:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			#print("Writing file '" + name + "'.")
			dstFolder =  saveDir + "\\" + type
			dstName = dstFolder + "\\" + name + ".dat"
			if dstName is None:
				return 0
			if not os.path.exists(dstFolder):
				os.makedirs(dstFolder)
			ff = open(dstName, "wb")
			ff.write(Data)
			ff.close()
			if decompSize2 != 0x0:
				f.seek(Block2_start + position2, NOESEEK_ABS)
				if Compression == 0x2:
					Data2 = f.read(decompSize2)
				elif Compression == 0x1:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x5:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x9:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x21:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x29:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				dstFolder2 =  saveDir + "\\" + type
				if type == "05_00_00_00":
					#print("Writing file '" + name + "' (model).")
					dstName2 = dstFolder2 + "\\" + name + "_model.dat"
				elif type == "01_00_00_00":
					#print("Writing file '" + name + "' (texture).")
					dstName2 = dstFolder2 + "\\" + name + "_texture.dat"
				else:
					#print("Writing file '" + name + "' (unknown).")
					dstName2 = dstFolder2 + "\\" + name + "_unknown.dat"
				if dstName2 is None:
					return 0
				if not os.path.exists(dstFolder2):
					os.makedirs(dstFolder2)
				ff2 = open(dstName2, "wb")
				ff2.write(Data2)
				ff2.close()
		f.seek(0x0, NOESEEK_ABS)
		IDsTable = f.read(Block1_start)
		dstFolder0 =  saveDir
		dstName0 = dstFolder0 + "\\IDs.BIN"
		if dstName0 is None:
			return 0
		if not os.path.exists(dstFolder0):
			os.makedirs(dstFolder0)
		ff3 = open(dstName0, "wb")
		print("Copying IDs table to IDs.BIN")
		ff3.write(IDsTable)
		ff3.close()
	noesis.freeModule(noeMod)
	print("All file were unpacked!")
	return 1

def NFSMW2012_XBOXMethod(srcName, saveDir):
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	with open(srcName, "rb") as f:
		id = noeStrFromBytes(f.read(4))
		f.seek(0x10, NOESEEK_ABS)
		NumIDs, IDsTab_start, Block1_start, Block2_start, Block3_start, Fullsize, Compression = noeUnpack(">iiiiiii", f.read(28)) # Verificar Compression
		f.seek(IDsTab_start, NOESEEK_ABS)
		print("Unpacking", NumIDs, "files from archive.")
		IDsList = []
		for i in range(0, NumIDs):
			print("Unpacking file", i+1)
			f.seek(IDsTab_start + i*0x50, NOESEEK_ABS)
			unk, count = noeUnpack(">BB", f.read(2))
			unk, countBlock = noeUnpack(">BB", f.read(2))
			name = f.read(4)
			name = binascii.hexlify(name)
			name = str(name,'ascii')
			name = name.upper()
			name = name[0]+name[1]+"_"+name[2]+name[3]+"_"+name[4]+name[5]+"_"+name[6]+name[7]
			#print(name, ":name")
			f.seek(0x4, NOESEEK_REL)
			ID2 = f.read(4)
			ID2 = binascii.hexlify(ID2)
			ID2 = str(ID2,'ascii')
			ID2 = ID2.upper()
			ID2 = ID2[0]+ID2[1]+"_"+ID2[2]+ID2[3]+"_"+ID2[4]+ID2[5]+"_"+ID2[6]+ID2[7]
			#print(ID2, ":ID2")
			decompSize1, decompSize2 = noeUnpack(">iI", f.read(8))
			f.seek(0x8, NOESEEK_REL)
			compSize1, compSize2 = noeUnpack(">ii", f.read(8))
			f.seek(0x8, NOESEEK_REL)
			position1, position2 = noeUnpack(">ii", f.read(8))
			f.seek(0x8, NOESEEK_REL)
			called_block = noeUnpack(">i", f.read(4))[0]
			type = f.read(4)
			type = binascii.hexlify(type)
			type = str(type,'ascii')
			type = type.upper()
			type = type[0]+type[1]+"_"+type[2]+type[3]+"_"+type[4]+type[5]+"_"+type[6]+type[7]
			Num_int_IDs = noeUnpack(">H", f.read(2))[0]
			#print(type, ":type")
			#ID2List = name + "_" + type
			#if ID2List in IDsList:
			#	count = 1
			#	ID2List = name + "_" + str(count) + "_" + type
			#	while ID2List in IDsList:
			#		count +=1
			#		ID2List = name + "_" + str(count) + "_" + type
			#	name += "_" + str(count)
			#	ID2List = name + "_" + type
			#IDsList.append(ID2List)
			if countBlock != 0:
				name += "_" + str(countBlock) 
				if count != 0:
					name += "_" + str(count)
			elif countBlock == 0 and count != 0:
				name += "_" + str(countBlock)
				name += "_" + str(count)
			if decompSize1 >= 0x90000000:
				decompSize1 = decompSize1 - 0x90000000
			elif decompSize1 >= 0x80000000:
				decompSize1 = decompSize1 - 0x80000000
			elif decompSize1 >= 0x70000000:
				decompSize1 = decompSize1 - 0x70000000
			elif decompSize1 >= 0x60000000:
				decompSize1 = decompSize1 - 0x60000000
			elif decompSize1 >= 0x50000000:
				decompSize1 = decompSize1 - 0x50000000
			elif decompSize1 >= 0x40000000:
				decompSize1 = decompSize1 - 0x40000000
			elif decompSize1 >= 0x30000000:
				decompSize1 = decompSize1 - 0x30000000
			elif decompSize1 >= 0x20000000:
				decompSize1 = decompSize1 - 0x20000000
			elif decompSize1 >= 0x10000000:
				decompSize1 = decompSize1 - 0x10000000
			if decompSize2 >= 0xC0000000:
				decompSize2 = decompSize2 - 0xC0000000
			elif decompSize2 >= 0x70000000:
				decompSize2 = decompSize2 - 0x70000000
			elif decompSize2 >= 0x60000000:
				decompSize2 = decompSize2 - 0x60000000
			elif decompSize2 >= 0x50000000:
				decompSize2 = decompSize2 - 0x50000000
			elif decompSize2 >= 0x40000000:
				decompSize2 = decompSize2 - 0x40000000
			elif decompSize2 >= 0x30000000:
				decompSize2 = decompSize2 - 0x30000000
			elif decompSize2 >= 0x20000000:
				decompSize2 = decompSize2 - 0x20000000
			elif decompSize2 >= 0x10000000:
				decompSize2 = decompSize2 - 0x10000000
			f.seek(Block1_start + position1, NOESEEK_ABS)
			if Compression == 0x8: #UI\Images\321351 and LUA
				Data = f.read(decompSize1)
			elif Compression == 0x1:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x27:
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x21: #Trafficattribs
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x11: #Shaders
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x7: #PVS
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			#print("Writing file '" + name + "'.")
			dstFolder =  saveDir + "\\" + type
			dstName = dstFolder + "\\" + name + ".dat"
			if dstName is None:
				return 0
			if not os.path.exists(dstFolder):
				os.makedirs(dstFolder)
			ff = open(dstName, "wb")
			ff.write(Data)
			ff.close()
			if decompSize2 != 0x0:
				f.seek(Block2_start + position2, NOESEEK_ABS)
				if Compression == 0x8: #UI\Images\321351 and LUA
					Data2 = f.read(decompSize2)
				elif Compression == 0x1:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x27:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x21: #Trafficattribs
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x11: #Shaders
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x7: #PVS
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				dstFolder2 =  saveDir + "\\" + type
				if type == "00_00_00_05":
					#print("Writing file '" + name + "' (model).")
					dstName2 = dstFolder2 + "\\" + name + "_model.dat"
				elif type == "00_00_00_01":
					#print("Writing file '" + name + "' (texture).")
					dstName2 = dstFolder2 + "\\" + name + "_texture.dat"
				else:
					#print("Writing file '" + name + "' (unknown).")
					dstName2 = dstFolder2 + "\\" + name + "_unknown.dat"
				if dstName2 is None:
					return 0
				if not os.path.exists(dstFolder2):
					os.makedirs(dstFolder2)
				ff2 = open(dstName2, "wb")
				ff2.write(Data2)
				ff2.close()
		f.seek(0x0, NOESEEK_ABS)
		IDsTable = f.read(Block1_start)
		dstFolder0 =  saveDir
		dstName0 = dstFolder0 + "\\IDs.BIN"
		if dstName0 is None:
			return 0
		if not os.path.exists(dstFolder0):
			os.makedirs(dstFolder0)
		ff3 = open(dstName0, "wb")
		print("Copying IDs table to IDs.BIN")
		ff3.write(IDsTable)
		ff3.close()
	noesis.freeModule(noeMod)
	print("All file were unpacked!")
	return 1

def NFSMW2012_PS3Method(srcName, saveDir):
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	with open(srcName, "rb") as f:
		id = noeStrFromBytes(f.read(4))
		f.seek(0xC, NOESEEK_ABS)
		NumIDs, IDsTab_start, Block1_start, Block2_start, Block3_start, Fullsize, Compression = noeUnpack(">iiiiiii", f.read(28))
		# Fullsize means the resource string table's offset in some beta builds
		f.seek(IDsTab_start, NOESEEK_ABS)
		print("Unpacking", NumIDs, "files from archive.")
		IDsList = []
		for i in range(0, NumIDs):
			print("Unpacking file", i+1)
			f.seek(IDsTab_start + i*0x48, NOESEEK_ABS)
			unk, count = noeUnpack(">BB", f.read(2))
			unk, countBlock = noeUnpack(">BB", f.read(2))
			name = f.read(4)
			name = binascii.hexlify(name)
			name = str(name,'ascii')
			name = name.upper()
			name = name[0]+name[1]+"_"+name[2]+name[3]+"_"+name[4]+name[5]+"_"+name[6]+name[7]
			#print(name, ":name")
			decompSize1, decompSize2, decompSize3 = noeUnpack(">iII", f.read(12))
			f.seek(0x4, NOESEEK_REL)
			compSize1, compSize2, compSize3 = noeUnpack(">iii", f.read(12))
			f.seek(0x4, NOESEEK_REL)
			position1, position2, position3 = noeUnpack(">iii", f.read(12))
			f.seek(0x4, NOESEEK_REL)
			called_block = noeUnpack(">i", f.read(4))[0]
			type = f.read(4)
			type = binascii.hexlify(type)
			type = str(type,'ascii')
			type = type.upper()
			type = type[0]+type[1]+"_"+type[2]+type[3]+"_"+type[4]+type[5]+"_"+type[6]+type[7]
			#print(type, ":type")
			Num_int_IDs = noeUnpack("<H", f.read(2))[0]
			#ID2List = name + "_" + type
			#if ID2List in IDsList:
			#	count = 1
			#	ID2List = name + "_" + str(count) + "_" + type
			#	while ID2List in IDsList:
			#		count +=1
			#		ID2List = name + "_" + str(count) + "_" + type
			#	name += "_" + str(count)
			#	ID2List = name + "_" + type
			#IDsList.append(ID2List)
			if countBlock != 0:
				name += "_" + str(countBlock) 
				if count != 0:
					name += "_" + str(count)
			elif countBlock == 0 and count != 0:
				name += "_" + str(countBlock)
				name += "_" + str(count)
			if decompSize1 >= 0x90000000:
				decompSize1 = decompSize1 - 0x90000000
			elif decompSize1 >= 0x80000000:
				decompSize1 = decompSize1 - 0x80000000
			elif decompSize1 >= 0x70000000:
				decompSize1 = decompSize1 - 0x70000000
			elif decompSize1 >= 0x60000000:
				decompSize1 = decompSize1 - 0x60000000
			elif decompSize1 >= 0x50000000:
				decompSize1 = decompSize1 - 0x50000000
			elif decompSize1 >= 0x40000000:
				decompSize1 = decompSize1 - 0x40000000
			elif decompSize1 >= 0x30000000:
				decompSize1 = decompSize1 - 0x30000000
			elif decompSize1 >= 0x20000000:
				decompSize1 = decompSize1 - 0x20000000
			elif decompSize1 >= 0x10000000:
				decompSize1 = decompSize1 - 0x10000000
			if decompSize2 >= 0xC0000000:
				decompSize2 = decompSize2 - 0xC0000000
			elif decompSize2 >= 0x70000000:
				decompSize2 = decompSize2 - 0x70000000
			elif decompSize2 >= 0x60000000:
				decompSize2 = decompSize2 - 0x60000000
			elif decompSize2 >= 0x50000000:
				decompSize2 = decompSize2 - 0x50000000
			elif decompSize2 >= 0x40000000:
				decompSize2 = decompSize2 - 0x40000000
			elif decompSize2 >= 0x30000000:
				decompSize2 = decompSize2 - 0x30000000
			elif decompSize2 >= 0x20000000:
				decompSize2 = decompSize2 - 0x20000000
			elif decompSize2 >= 0x10000000:
				decompSize2 = decompSize2 - 0x10000000
			if decompSize3 >= 0xC0000000:
				decompSize3 = decompSize3 - 0xC0000000
			elif decompSize3 >= 0x70000000:
				decompSize3 = decompSize3 - 0x70000000
			elif decompSize3 >= 0x60000000:
				decompSize3 = decompSize3 - 0x60000000
			elif decompSize3 >= 0x50000000:
				decompSize3 = decompSize3 - 0x50000000
			elif decompSize3 >= 0x40000000:
				decompSize3 = decompSize3 - 0x40000000
			elif decompSize3 >= 0x30000000:
				decompSize3 = decompSize3 - 0x30000000
			elif decompSize3 >= 0x20000000:
				decompSize3 = decompSize3 - 0x20000000
			elif decompSize3 >= 0x10000000:
				decompSize3 = decompSize3 - 0x10000000
			f.seek(Block1_start + position1, NOESEEK_ABS)
			if Compression == 0x3: #PS3
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0xB: #PS3
				compData = f.read(compSize1)
				Data = DecompressData(compData, decompSize1)
			elif Compression == 0x2: #PS3
				Data = f.read(decompSize1)
			else:
				if compSize1 != decompSize1:
					compData = f.read(compSize1)
					Data = DecompressData(compData, decompSize1)
				else:
					Data = f.read(decompSize1)
			#print("Writing file '" + name + "'.")
			dstFolder =  saveDir + "\\" + type
			dstName = dstFolder + "\\" + name + ".dat"
			if dstName is None:
				return 0
			if not os.path.exists(dstFolder):
				os.makedirs(dstFolder)
			ff = open(dstName, "wb")
			ff.write(Data)
			ff.close()
			if decompSize2 != 0x0:
				f.seek(Block2_start + position2, NOESEEK_ABS)
				if Compression == 0x3:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0xB:
					compData2 = f.read(compSize2)
					Data2 = DecompressData(compData2, decompSize2)
				elif Compression == 0x2:
					Data2 = f.read(decompSize2)
				else:
					if compSize2 != decompSize2:
						compData2 = f.read(compSize2)
						Data2 = DecompressData(compData2, decompSize2)
					else:
						Data2 = f.read(decompSize2)
				dstFolder2 =  saveDir + "\\" + type
				if type == "00_00_00_05":
					#print("Writing file '" + name + "' (model).")
					dstName2 = dstFolder2 + "\\" + name + "_indices.dat"
				elif type == "00_00_00_01":
					#print("Writing file '" + name + "' (texture).")
					dstName2 = dstFolder2 + "\\" + name + "_texture_block2.dat"
				else:
					#print("Writing file '" + name + "' (unknown).")
					dstName2 = dstFolder2 + "\\" + name + "_unknown.dat"
				if dstName2 is None:
					return 0
				if not os.path.exists(dstFolder2):
					os.makedirs(dstFolder2)
				ff2 = open(dstName2, "wb")
				ff2.write(Data2)
				ff2.close()
			if decompSize3 != 0x0:
				f.seek(Block3_start + position3, NOESEEK_ABS)
				if Compression == 0x3:
					compData3 = f.read(compSize3)
					Data3 = DecompressData(compData3, decompSize3)
				elif Compression == 0xB:
					compData3 = f.read(compSize3)
					Data3 = DecompressData(compData3, decompSize3)
				elif Compression == 0x2:
					Data3 = f.read(decompSize3)
				else:
					if compSize3 != decompSize3:
						compData3 = f.read(compSize3)
						print(compSize3, " ", decompSize3)
						Data3 = DecompressData(compData3, decompSize3)
					else:
						Data3 = f.read(decompSize3)
				dstFolder3 =  saveDir + "\\" + type
				if type == "00_00_00_05":
					#print("Writing file '" + name + "' (model).")
					dstName3 = dstFolder3 + "\\" + name + "_vertices.dat"
				elif type == "00_00_00_01":
					#print("Writing file '" + name + "' (texture).")
					dstName3 = dstFolder3 + "\\" + name + "_texture.dat"
				else:
					#print("Writing file '" + name + "' (unknown).")
					dstName3 = dstFolder3 + "\\" + name + "_unknown_block3.dat"
				if dstName3 is None:
					return 0
				if not os.path.exists(dstFolder3):
					os.makedirs(dstFolder3)
				ff3 = open(dstName3, "wb")
				ff3.write(Data3)
				ff3.close()
		f.seek(0x0, NOESEEK_ABS)
		IDsTable = f.read(Block1_start)
		dstFolder0 =  saveDir
		dstName0 = dstFolder0 + "\\IDs.BIN"
		if dstName0 is None:
			return 0
		if not os.path.exists(dstFolder0):
			os.makedirs(dstFolder0)
		ff4 = open(dstName0, "wb")
		print("Copying IDs table to IDs.BIN")
		ff4.write(IDsTable)
		ff4.close()
		
		# Checking for resource string table
		FileLen = os.path.getsize(srcName)
		if Fullsize < FileLen:
			f.seek(Fullsize, 0)
			ResourceStringTable = f.read(FileLen-Fullsize)
			zeroWasRemoved = False
			while ResourceStringTable[-1] == 0:
				ResourceStringTable = ResourceStringTable[:-1]
				zeroWasRemoved = True
			if zeroWasRemoved:
				ResourceStringTable = ResourceStringTable + b'\x00'		# Ending byte
			dstName0 = dstFolder0 + "\\ResourceStringTable.xml"
			rst = open(dstName0, "wb")
			print("Copying resource string table")
			rst.write(ResourceStringTable)
			rst.close()
	noesis.freeModule(noeMod)
	print("All file were unpacked!")
	return 1

def DecompressData(compData, decompSize):
	try: Data = rapi.decompInflate(compData, decompSize)
	except:
		zobj = zlib.decompressobj()							# obj for decompressing data streams that won’t fit into memory at once.
		Data = zobj.decompress(compData, decompSize)
	return Data

@contextmanager
def suppress_stdout():
	with open(os.devnull, "w") as devnull:
		old_stdout = sys.stdout
		sys.stdout = devnull
		try:  
			yield
		finally:
			sys.stdout = old_stdout

#By DGIorio