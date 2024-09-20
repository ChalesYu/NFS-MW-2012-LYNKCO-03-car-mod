from inc_noesis import *
import os
import binascii
import math
import sys
from contextlib import contextmanager
import shutil

OutputName = "Output"
#OutputName = "VEH_122701_HI"

def registerNoesisTypes():
	handle = noesis.registerTool("&Need for Speed Most Wanted 2012 Packer", packNFSMWToolMethod, "Pack a Need for Speed Most Wanted 2012 file")
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

def packNFSMWToolMethod(toolIndex):
	IDsTable = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Open File", "Select the file IDs.BIN.", noesis.getSelectedFile(), validateInput)
#	IDsTable="C:\\Need for Speed(TM) Most Wanted\\MOD\\a\\IDs.BIN"
	if IDsTable is None:
		print("file :  : Not Exist")
		return 0
	srcPath = os.path.dirname(IDsTable)
	if srcPath is None:
		return 0
	noesis.logPopup()
	if os.path.isfile(IDsTable):
		g = open(IDsTable, "rb")
		bnd = noeStrFromBytes(g.read(4))
		if bnd == "bnd2":
			g.seek(0x2, NOESEEK_REL)
			version = g.read(2)
			g.close()
			if version == b'\x01\x00':
				version = "PC"
				print("Game version:", version)
				NFSMW_PCpack(IDsTable, srcPath)
			elif version ==  b'\x00\x03':
				version = "XBOX"
				print("Game version:", version)
				#NFSMW_XBOXpack(IDsTable, srcPath)
			elif version == b'\x00\x02':
				version = "PS3"
				print("Game version:", version)
				NFSMW_PS3pack(IDsTable, srcPath)
			else:
				version = "Unknown"
				print("Game version:", version)
		elif bnd == "bndl":
			g.seek(0x4, NOESEEK_ABS)
			version = g.read(4)
			g.close()
			if version == b'\x00\x00\x00\x05':
				version = "XBOX BETA 2006"
				print("Game version:", version)
				#NFSMW_XBOXBetapack(IDsTable, srcPath)
				print("Unsupported game version")
			else:
				version = "Unknown"
				print("Game version:", version)
		else:
			g.close()
			version = "Unknown"
			print("Game version:", version)
	elif os.path.isdir(IDsTable):
		mainFolder = IDsTable
		for folder in os.listdir(mainFolder):
			folder_dir = os.path.join(mainFolder, folder)
			if not os.path.isdir(folder_dir):
				continue
			print("Packing:", folder)
			IDsPath = os.path.join(folder_dir, 'IDs_' + folder + '.BIN')
			IDsPath2 = os.path.join(folder_dir, 'IDs.BIN')
			if os.path.exists(IDsPath):
				IDsPath = IDsPath
			elif os.path.exists(IDsPath2):
				IDsPath = IDsPath2
			if os.path.isfile(IDsPath):
				g = open(IDsPath, "rb")
				bnd = noeStrFromBytes(g.read(4))
				if bnd == "bnd2":
					g.seek(0x2, NOESEEK_REL)
					version = g.read(2)
					g.close()
					if version == b'\x01\x00':
						version = "PC"
						with suppress_stdout():
							NFSMW_PCpack(IDsPath, folder_dir)
					elif version == b'x00\x03':
						version = "XBOX"
						#NFSMW_XBOXpack(IDsPath, folder_dir)
					elif version == b'x00\x02':
						version = "PS3"
						NFSMW_PS3pack(IDsPath, folder_dir)
					else:
						version = "Unknown"
						print("Game version:", version)
				else:
					g.close()
					version = "Unknown"
					print("Game version:", version)
				OutFile = os.path.join(folder_dir, OutputName + '.BNDL')
				#RenOutFile = os.path.join(folder_dir, folder + '.BNDL')
				RenOutFile = os.path.join(mainFolder, folder + '.BNDL')
				os.rename(OutFile, RenOutFile)
		print("Finished packing.")
		noesis.messagePrompt("Successfully packed the files.")
	return 1
	
def NFSMW_PCpack(IDsTable, srcPath):
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	Block1Path = srcPath + "\\" + "Block1.BIN"
	Block2Path = srcPath + "\\" + "Block2.BIN"
	Block1 = open(Block1Path, "wb")
	Block2 = open(Block2Path, "wb")
	with open(IDsTable, "rb") as f:
		f.seek(0xC, NOESEEK_ABS)
		NumIDs, IDsTab_start, Block1_start, Block2_start, Fullsize, Fullsize2, Compression = noeUnpack("<iiiiiii", f.read(28))
		f.seek(IDsTab_start, NOESEEK_ABS)
		NumIDs_check = int((os.path.getsize(IDsTable) - IDsTab_start)/0x48)
		if NumIDs_check != NumIDs:
			print("Number of IDs (", NumIDs, ") is different from the amount of IDs in IDsTable (", NumIDs_check, ").")
			print("It will be used", NumIDs_check,".")
			NumIDs = NumIDs_check
		Offset2 = 0
		FileLen_fix = [0]*NumIDs
		FileLen_fix2 = [0]*NumIDs
		CompLen = [0]*NumIDs
		CompLen2 = [0]*NumIDs
		Position1 = [0]*(NumIDs+1)
		Position2 = [0]*(NumIDs+1)
		intIDs = [0]*(NumIDs)
		intIDs_position = [0]*(NumIDs)
		IDsList = []
		#Compression = 8	#Uncomment if you want to compress an uncompressed file, like TRK_UNITs
		for i in range(0, NumIDs):
			f.seek(IDsTab_start + i*0x48, NOESEEK_ABS)
			name = f.read(4)
			countBlock, unk1 = noeUnpack("<BB", f.read(2))
			count, unk = noeUnpack("<BB", f.read(2))
			#f.seek(-0x3, NOESEEK_REL)
			name = binascii.hexlify(name)
			name = str(name,'ascii')
			name = name.upper()
			name = name[0]+name[1]+"_"+name[2]+name[3]+"_"+name[4]+name[5]+"_"+name[6]+name[7]
			#f.seek(0x38, NOESEEK_REL)
			#f.seek(0x35, NOESEEK_REL)
			f.seek(0x34, NOESEEK_REL)
			type = f.read(4)
			type = binascii.hexlify(type)
			type = str(type,'ascii')
			type = type.upper()
			type = type[0]+type[1]+"_"+type[2]+type[3]+"_"+type[4]+type[5]+"_"+type[6]+type[7]
			#if type == "12_00_00_00":
			#	name += "_"+str(count)
			#elif count != 0:
			#	name += "_"+str(count)
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
			print("Packing file:",name)
			#type = type[6]+type[7]+type[4]+type[5]+type[2]+type[3]+type[0]+type[1]
			#type = id2type(type)
			f.seek(-0x38, NOESEEK_REL)	#REMOVER
			filePath = srcPath + "\\" + type + "\\" + name + ".dat"
			if os.path.exists(filePath):
				FileLen = os.path.getsize(filePath)
				compData = None
				file = open(filePath, "rb")
				decompData = file.read()
				if type == "06_01_00_00" or type == "GraphicsSpec":				#OKOK
					file.seek(0xC, NOESEEK_ABS)
					Position0 = noeUnpack("<i", file.read(4))[0]
					file.seek(Position0 + 0x78, NOESEEK_ABS)
					PositionEnd = noeUnpack("<i", file.read(4))[0] + 0x40
					intIDs1 = (FileLen-PositionEnd)/0x10
					intIDs[i] = intIDs1
					intIDs_position[i] = PositionEnd
				elif type == "51_00_00_00" or type == "Model":					#OKOK
					#file.seek(0x14, NOESEEK_ABS)
					#intIDs1 = (noeUnpack("<B", file.read(1)))[0]
					#intIDs[i] = intIDs1
					#intIDs_position[i] = FileLen - intIDs[i]*0x10
					file.seek(0x0, NOESEEK_ABS)
					Pointer = noeUnpack("<i", file.read(4))[0]
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = noeUnpack("<i", file.read(4))[0]
					count = 1
					while check != Pointer:
						file.seek(-0x14, NOESEEK_REL)
						check = noeUnpack("<i", file.read(4))[0]
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "05_00_00_00" or type == "Renderable":				#OKOK
					file.seek(0x12, NOESEEK_ABS)
					NumMeshes = noeUnpack("<H", file.read(2))[0]
					intPosition0 = noeUnpack("<i", file.read(4))[0]
					file.seek(intPosition0, NOESEEK_ABS)
					intPosition1 = noeUnpack("<i", file.read(4))[0]
					MaterialPointer = intPosition1 + 0x20
					file.seek(intPosition1+NumMeshes*0x60, NOESEEK_ABS)
					for j in range(0, FileLen-(intPosition1+NumMeshes*0x60)):
						file.seek(0x8, NOESEEK_REL)
						MatPointer = noeUnpack("<i", file.read(4))[0]
						if MatPointer == MaterialPointer:
							intIDs_position[i] = file.tell()-0xC
							intIDs[i] = (FileLen-intIDs_position[i])/0x10
							break
						file.seek(0x4, NOESEEK_REL)
				elif type == "02_00_00_00" or type == "Material":				#OKOK
					file.seek(0x6, NOESEEK_ABS)
					intIDs_position[i] = noeUnpack("<H", file.read(2))[0]
					intIDs[i] = (FileLen - intIDs_position[i])/0x10
				elif type == "15_00_00_00" or type == "GenesysObject":			#OKOK
					#file.seek(0x2C, NOESEEK_ABS)
					#intOffset = noeUnpack("<i", file.read(4))[0]
					#intIDs_position[i] = intOffset
					#intIDs[i] = (FileLen - intIDs_position[i])/0x10
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x00\x00\x00\x80':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "B0_00_00_00" or type == "AnimationList":			#OKOK
					file.seek(0x4, NOESEEK_ABS)
					intOffset = noeUnpack("<i", file.read(4))[0]
					division1 = (intOffset/0x10)
					division2 = math.ceil(intOffset/0x10)
					padComp = int((division2 - division1)*0x10)
					intOffset += padComp
					if intOffset < FileLen:
						intIDs[i] = (FileLen - intOffset)/0x10
						intIDs_position[i] = intOffset
				elif type == "0F_02_00_00" or type == "GroundcoverCollection":	#OKOK
					file.seek(0x3C, NOESEEK_ABS)
					intOffset = noeUnpack("<i", file.read(4))[0]
					division1 = (intOffset/0x10)
					division2 = math.ceil(intOffset/0x10)
					padComp = int((division2 - division1)*0x10)
					intOffset += padComp
					if intOffset < FileLen and intOffset > 0:
						file.seek(intOffset+0x8, NOESEEK_ABS)
						check = file.read(4)
						while check != b'\x40\x00\x00\x80':
							file.seek(0xC, NOESEEK_REL)
							check = file.read(4)
						intIDs_position[i] = file.tell()-0xC
						intIDs[i] = (FileLen-intIDs_position[i])/0x10
				elif type == "04_00_00_00":	# PC Shader stuff					#OK
					intIDs[i] = 2
					intIDs_position[i] = 0x10
				elif type == "04_02_00_00" or type == "DynamicInstanceList":	#OKOK
					file.seek(0x8, NOESEEK_ABS)
					intIDs1 = noeUnpack("<i", file.read(4))[0]
					intIDs[i] = intIDs1
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "05_02_00_00" or type == "WorldObject":			#OKOK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x04\x00\x00\x00':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "06_02_00_00" or type == "ZoneHeader":				#OKOK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x04\x00\x00\x80':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "07_02_00_00" or type == "VehicleSound":			#OKOK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x10\x00\x00\x80':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "13_02_00_00" or type == "LightInstanceList":		#OKOK
					file.seek(0x8, NOESEEK_ABS)
					intIDs1 = noeUnpack("<i", file.read(4))[0]
					intIDs[i] = intIDs1
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "14_00_00_00" or type == "GenesysType":			#OKOK
					file.seek(0, NOESEEK_ABS)
					unkbyte0 = noeUnpack("<B", file.read(1))[0]
					unkbyte1 = noeUnpack("<B", file.read(1))[0]
					unkbyte2 = noeUnpack("<B", file.read(1))[0]
					if unkbyte1 == 0x6:
						pointer = b'\x24\x00\x00\x00'
					else:
						pointer = b'\x04\x00\x00\x00'
					if unkbyte2 > 0:
						file.seek(0x20, NOESEEK_ABS)
						unkint = noeUnpack("<i", file.read(4))[0]
						file.seek(0x8, NOESEEK_ABS)
						unkint2 = noeUnpack("<i", file.read(4))[0]
						if unkint > 0 or unkint2 != 0:
							file.seek(FileLen - 0x8, NOESEEK_ABS)
							check = file.read(4)
							count = 1
							while check != pointer:
								file.seek(-0x14, NOESEEK_REL)
								check = file.read(4)
								count = count + 1
								if file.tell() < unkint:						# EDITED 09 Oct 2019
									break
							if file.tell() > unkint:
								intIDs[i] = count
								intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "15_02_00_00" or type == "CompoundObject":			#OKOK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x04\x00\x00\x00':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "16_02_00_00" or type == "CompoundInstanceList":	#OKOK
					#file.seek(0x8, NOESEEK_ABS)
					#intIDs1 = noeUnpack("<i", file.read(4))[0]
					#intIDs[i] = intIDs1
					#intIDs_position[i] = FileLen - intIDs[i]*0x10
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x50\x00\x00\x80':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "17_02_00_00" or type == "PropObject":				#OKOK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x04\x00\x00\x00':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "18_02_00_00" or type == "PropInstanceList":		#OKOK
					file.seek(0x8, NOESEEK_ABS)
					intIDs1 = noeUnpack("<i", file.read(4))[0]
					intIDs[i] = intIDs1
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "50_00_00_00" or type == "InstanceList":			#OKOK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x10\x00\x00\x00':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "53_00_00_00" or type == "Shader":					#OK
					file.seek(0x12, NOESEEK_ABS)
					intOffset = noeUnpack("<H", file.read(2))[0]
					intIDs_position[i] = intOffset
					intIDs[i] = (FileLen - intIDs_position[i])/0x10
				file.close()
				if Compression == 0x1 or Compression == 0x5 or Compression == 0x9 or Compression == 0x21 or Compression == 0x29:
					compData = rapi.compressDeflate(decompData)
				elif Compression == 0x2:
					compData = decompData
				if compData is None:
					noesis.doException("Failed to compress a file while generating the archive.")
				division1 = (len(compData)/0x10)
				division2 = math.ceil(len(compData)/0x10)
				padComp = int((division2 - division1)*0x10)
				if padComp != 0:
					padCompLen = padComp
				else:
					padCompLen = 0
				padCompLen = 0
				Block1.write(compData)
				Block1.write(bytearray([0])*padCompLen)
				FileLen_fix[i] = FileLen + 0x40000000
				
				CompLen[i] = len(compData)
				Position1[i+1] = Position1[i] + len(compData) + padCompLen
			else:
				text = "WARNING: File " + name + " (type " + type + ") not found."
				print("WARNING: File", name, "(type", type,") not found.")
				noesis.doException(text)
			if type == "05_00_00_00" or type == "Renderable" or type == "VFXMeshCollection":
				filePath2 = srcPath + "\\" + type + "\\" + name + "_model.dat"
				if os.path.exists(filePath2):
					FileLen2 = os.path.getsize(filePath2)
					compData2 = None
					file2 = open(filePath2, "rb")
					decompData2 = file2.read()
					file2.close()
					if Compression == 0x1 or Compression == 0x5 or Compression == 0x9 or Compression == 0x21 or Compression == 0x29:
						compData2 = rapi.compressDeflate(decompData2)
					elif Compression == 0x2:
						compData2 = decompData2
					if compData2 is None:
						noesis.doException("Failed to compress a file while generating the archive.")
					division1 = (len(compData2)/0x80)
					division2 = math.ceil(len(compData2)/0x80)
					padComp = int((division2 - division1)*0x80)
					if padComp != 0:
						padCompLen2 = padComp
					else:
						padCompLen2 = 0
					padCompLen2 = 0
					Block2.write(compData2)
					Block2.write(bytearray([0])*padCompLen2)
					FileLen_fix2[i] = FileLen2 + 0x40000000
					CompLen2[i] = len(compData2)
					Position2[i] = Offset2
					Offset2 = Offset2 + len(compData2) + padCompLen2
			elif type == "01_00_00_00" or type == "Raster":
				filePath2 = srcPath + "\\" + type + "\\" + name + "_texture.dat"
				if os.path.exists(filePath2):
					FileLen2 = os.path.getsize(filePath2)
					compData2 = None
					file2 = open(filePath2, "rb")
					decompData2 = file2.read()
					file2.close()
					if Compression == 0x1 or Compression == 0x5 or Compression == 0x9 or Compression == 0x21 or Compression == 0x29:
						compData2 = rapi.compressDeflate(decompData2)
					elif Compression == 0x2:
						compData2 = decompData2
					if compData2 is None:
						noesis.doException("Failed to compress a file while generating the archive.")
					division1 = (len(compData2)/0x80)
					division2 = math.ceil(len(compData2)/0x80)
					padComp = int((division2 - division1)*0x80)
					if padComp != 0:
						padCompLen2 = padComp
					else:
						padCompLen2 = 0
					padCompLen2 = 0
					Block2.write(compData2)
					Block2.write(bytearray([0])*padCompLen2)
					FileLen_fix2[i] = FileLen2 + 0x40000000
					CompLen2[i] = len(compData2)
					Position2[i] = Offset2
					Offset2 = Offset2 + len(compData2) + padCompLen2
			elif type == "08_00_00_00" or type == "ShaderProgramBuffer":
				filePath2 = srcPath + "\\" + type + "\\" + name + "_unknown.dat"
				if os.path.exists(filePath2):
					FileLen2 = os.path.getsize(filePath2)
					compData2 = None
					file2 = open(filePath2, "rb")
					decompData2 = file2.read()
					file2.close()
					if Compression == 0x1 or Compression == 0x5 or Compression == 0x9 or Compression == 0x21 or Compression == 0x29:
						compData2 = rapi.compressDeflate(decompData2)
					elif Compression == 0x2:
						compData2 = decompData2
					if compData2 is None:
						noesis.doException("Failed to compress a file while generating the archive.")
					division1 = (len(compData2)/0x80)
					division2 = math.ceil(len(compData2)/0x80)
					padComp = int((division2 - division1)*0x80)
					if padComp != 0:
						padCompLen2 = padComp
					else:
						padCompLen2 = 0
					padCompLen2 = 0
					Block2.write(compData2)
					Block2.write(bytearray([0])*padCompLen2)
					FileLen_fix2[i] = FileLen2 + 0x40000000
					CompLen2[i] = len(compData2)
					Position2[i] = Offset2
					Offset2 = Offset2 + len(compData2) + padCompLen2
	with open(IDsTable, "r+b") as g:
		Block1_position = os.path.getsize(IDsTable)
		Block2_position = Block1_position + Position1[NumIDs]
		division1 = (Block2_position/0x80)
		division2 = math.ceil(Block2_position/0x80)
		padComp = int((division2 - division1)*0x80)
		if padComp != 0:
			padCompLen3 = padComp
		else:
			padCompLen3 = 0
		padCompLen3 = 0
		Block2_position = Block2_position + padCompLen3
		Block3_position = Block2_position + Offset2
		TotalFilesize = Block3_position
		g.seek(0x8, NOESEEK_ABS)
		g.write(noePack("<i", TotalFilesize))
		g.write(noePack("<i", NumIDs))
		g.seek(0x14, NOESEEK_ABS)
		g.write(noePack("<i", Block1_position))
		g.write(noePack("<i", Block2_position))
		g.write(noePack("<i", Block3_position))
		g.write(noePack("<i", TotalFilesize))
		g.write(noePack("<i", Compression))
		#g.write(noePack("<i", 0))
		for i in range(0, NumIDs):
			g.seek(IDsTab_start + i*0x48, NOESEEK_ABS)
			g.seek(0x8, NOESEEK_REL)
			g.write(noePack("<i", FileLen_fix[i]))
			g.write(noePack("<i", FileLen_fix2[i]))
			g.seek(0x8, NOESEEK_REL)
			#g.write(noePack("<i", 0))
			g#.write(noePack("<i", 0))
			g.write(noePack("<i", CompLen[i]))
			g.write(noePack("<i", CompLen2[i]))
			g.seek(0x8, NOESEEK_REL)
			#g.write(noePack("<i", 0))
			#g.write(noePack("<i", 0))
			g.write(noePack("<i", Position1[i]))
			g.write(noePack("<i", Position2[i]))
			g.seek(0x8, NOESEEK_REL)
			#g.write(noePack("<i", 0))
			#g.write(noePack("<i", 0))
			g.write(noePack("<i", intIDs_position[i]))
			g.seek(0x4, NOESEEK_REL)
			g.write(noePack("<H", int(intIDs[i])))
			#g.seek(0x4, NOESEEK_REL)
			#g.write(noePack("<i", 0))
	Block1.close()
	Block2.close()
	IDsTable2 = open(IDsTable, "rb")
	Block1 = open(Block1Path, "rb")
	Block2 = open(Block2Path, "rb")
	OutputFilePath = srcPath + "\\" + OutputName + ".BNDL"
	OutputFile = open(OutputFilePath, "wb")
	OutputFile.write(IDsTable2.read())
	OutputFile.write(Block1.read())
	OutputFile.write(bytearray([0])*padCompLen3)
	OutputFile.write(Block2.read())
	OutputFile.close()
	IDsTable2.close()
	Block1.close()
	Block2.close()
	os.remove(Block1Path)
	os.remove(Block2Path)
	noesis.freeModule(noeMod)
	print("Generated archive!")
	return 1

def NFSMW_PS3pack(IDsTable, srcPath):
	noeMod = noesis.instantiateModule()
	noesis.setModuleRAPI(noeMod)
	Block1Path = srcPath + "\\" + "Block1.BIN"
	Block2Path = srcPath + "\\" + "Block2.BIN"
	Block3Path = srcPath + "\\" + "Block3.BIN"
	Block4Path = srcPath + "\\" + "Block4.BIN"
	Block1 = open(Block1Path, "wb")
	Block2 = open(Block2Path, "wb")
	Block3 = open(Block3Path, "wb")
	Block4 = open(Block4Path, "wb")
	with open(IDsTable, "rb") as f:
		f.seek(0x8, 0)
		ResourceStringTable_start, NumIDs, IDsTab_start, Block1_start, Block2_start, Block3_start, Block4_start, Compression = noeUnpack(">iiiiiiii", f.read(32))
		f.seek(IDsTab_start, 0)
		NumIDs_check = int((os.path.getsize(IDsTable) - IDsTab_start)/0x48)
		if NumIDs_check != NumIDs:
			print("Number of IDs (", NumIDs, ") is different from the amount of IDs in IDsTable (", NumIDs_check, ").")
			print("It will be used", NumIDs_check,".")
			NumIDs = NumIDs_check
		Offset2 = 0
		Offset3 = 0
		Offset4 = 0
		FileLen_fix = [0]*NumIDs
		FileLen_fix2 = [0]*NumIDs
		FileLen_fix3 = [0]*NumIDs
		FileLen_fix4 = [0]*NumIDs
		CompLen = [0]*NumIDs
		CompLen2 = [0]*NumIDs
		CompLen3 = [0]*NumIDs
		CompLen4 = [0]*NumIDs
		Position1 = [0]*(NumIDs+1)
		Position2 = [0]*(NumIDs+1)
		Position3 = [0]*(NumIDs+1)
		Position4 = [0]*(NumIDs+1)
		intIDs = [0]*(NumIDs)
		intIDs_position = [0]*(NumIDs)
		IDsList = []
		#Compression = 8	#Uncomment if you want to compress an uncompressed file, like TRK_UNITs
		for i in range(0, NumIDs):
			f.seek(IDsTab_start + i*0x48, 0)
			unk, count = noeUnpack(">BB", f.read(2))
			unk, countBlock = noeUnpack(">BB", f.read(2))
			name = f.read(4)
			name = binascii.hexlify(name)
			name = str(name,'ascii')
			name = name.upper()
			name = name[0]+name[1]+"_"+name[2]+name[3]+"_"+name[4]+name[5]+"_"+name[6]+name[7]
			f.seek(0x34, NOESEEK_REL)
			type = f.read(4)
			type = binascii.hexlify(type)
			type = str(type,'ascii')
			type = type.upper()
			type = type[0]+type[1]+"_"+type[2]+type[3]+"_"+type[4]+type[5]+"_"+type[6]+type[7]
			if countBlock != 0:
				name += "_" + str(countBlock) 
				if count != 0:
					name += "_" + str(count)
			elif countBlock == 0 and count != 0:
				name += "_" + str(countBlock)
				name += "_" + str(count)
			print("Packing file:",name)
			f.seek(-0x38, NOESEEK_REL)	#REMOVER
			filePath = srcPath + "\\" + type + "\\" + name + ".dat"
			if os.path.exists(filePath):
				FileLen = os.path.getsize(filePath)
				compData = None
				file = open(filePath, "rb")
				decompData = file.read()
				if type == "00_00_00_14" or type == "GenesysType":						#OK
					file.seek(0, NOESEEK_ABS)
					unkbyte0 = noeUnpack(">B", file.read(1))[0]
					unkbyte1 = noeUnpack(">B", file.read(1))[0]
					unkbyte2 = noeUnpack(">H", file.read(2))[0]
					if unkbyte1 == 0x6:
						pointer = b'\x00\x00\x00\x24'
					else:
						pointer = b'\x00\x00\x00\x04'
					if unkbyte2 > 0:
						file.seek(0x20, NOESEEK_ABS)
						unkint = noeUnpack(">i", file.read(4))[0]
						file.seek(0x8, NOESEEK_ABS)
						unkint2 = noeUnpack(">i", file.read(4))[0]
						if unkint > 0 or unkint2 != 0:
							file.seek(FileLen - 0x8, NOESEEK_ABS)
							check = file.read(4)
							count = 1
							while check != pointer:
								file.seek(-0x14, NOESEEK_REL)
								check = file.read(4)
								count = count + 1
								if file.tell() < unkint:
									break
							if file.tell() > unkint:
								intIDs[i] = count
								intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "00_00_00_15" or type == "GenesysObject":						#OK
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x80\x00\x00\x00':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "00_00_01_06" or type == "GraphicsSpec":
					file.seek(0xC, NOESEEK_ABS)
					Position0 = noeUnpack(">i", file.read(4))[0]
					file.seek(Position0 + 0x78, NOESEEK_ABS)
					PositionEnd = noeUnpack(">i", file.read(4))[0] + 0x40
					if PositionEnd == 0 or PositionEnd > FileLen or PositionEnd < 0:
						file.seek(Position0, NOESEEK_ABS)
						PositionEnd = noeUnpack(">i", file.read(4))[0] + 0x40
						file.seek(PositionEnd + 0x4, NOESEEK_ABS)
						check = file.read(4)
						while check != b'\x00\x00\x00\x00':
							file.seek(0xC, NOESEEK_REL)
							check = file.read(4)
						file.seek(-0x8, NOESEEK_REL)
						PositionEnd = file.tell()
					intIDs1 = (FileLen-PositionEnd)/0x10
					intIDs[i] = intIDs1
					intIDs_position[i] = PositionEnd
				elif type == "00_00_00_51" or type == "Model":
					file.seek(0x0, NOESEEK_ABS)
					Pointer = noeUnpack(">i", file.read(4))[0]
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = noeUnpack(">i", file.read(4))[0]
					count = 1
					while check != Pointer:
						file.seek(-0x14, NOESEEK_REL)
						check = noeUnpack(">i", file.read(4))[0]
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "00_00_00_05" or type == "Renderable":
					file.seek(0x12, NOESEEK_ABS)
					NumMeshes = noeUnpack(">H", file.read(2))[0]
					intPosition0 = noeUnpack(">i", file.read(4))[0]
					file.seek(intPosition0, NOESEEK_ABS)
					intPosition1 = noeUnpack(">i", file.read(4))[0]
					MaterialPointer = intPosition1 + 0x1C
					file.seek(intPosition1+NumMeshes*0x60, NOESEEK_ABS)
					for j in range(0, FileLen-(intPosition1+NumMeshes*0x60)):
						file.seek(0x8, NOESEEK_REL)
						MatPointer = noeUnpack(">i", file.read(4))[0]
						if MatPointer == MaterialPointer:
							intIDs_position[i] = file.tell()-0xC
							intIDs[i] = (FileLen-intIDs_position[i])/0x10
							break
						file.seek(0x4, NOESEEK_REL)
				elif type == "00_00_00_02" or type == "Material":
					file.seek(0x6, NOESEEK_ABS)
					intIDs_position[i] = noeUnpack(">H", file.read(2))[0]
					intIDs[i] = (FileLen - intIDs_position[i])/0x10
				elif type == "00_00_00_B0" or type == "AnimationList":
					file.seek(0x4, NOESEEK_ABS)
					intOffset = noeUnpack(">i", file.read(4))[0]
					division1 = (intOffset/0x10)
					division2 = math.ceil(intOffset/0x10)
					padComp = int((division2 - division1)*0x10)
					intOffset += padComp
					if intOffset < FileLen:
						intIDs[i] = (FileLen - intOffset)/0x10
						intIDs_position[i] = intOffset
				elif type == "00_00_02_07" or type == "VehicleSound":
					file.seek(FileLen - 0x8, NOESEEK_ABS)
					check = file.read(4)
					count = 1
					while check != b'\x80\x00\x00\x10':
						file.seek(-0x14, NOESEEK_REL)
						check = file.read(4)
						count = count + 1
					intIDs[i] = count
					intIDs_position[i] = FileLen - intIDs[i]*0x10
				elif type == "00_00_02_0F" or type == "GroundcoverCollection":
					file.seek(0x3C, NOESEEK_ABS)
					intOffset = noeUnpack(">i", file.read(4))[0]
					division1 = (intOffset/0x10)
					division2 = math.ceil(intOffset/0x10)
					padComp = int((division2 - division1)*0x10)
					intOffset += padComp
					if intOffset < FileLen and intOffset > 0:
						file.seek(intOffset+0x8, NOESEEK_ABS)
						check = file.read(4)
						while check != b'\x80\x00\x00\x40':
							file.seek(0xC, NOESEEK_REL)
							check = file.read(4)
						intIDs_position[i] = file.tell()-0xC
						intIDs[i] = (FileLen-intIDs_position[i])/0x10
				
				
				#if Compression == 0x1 or Compression == 0x5 or Compression == 0x9 or Compression == 0x21 or Compression == 0x29:
				if Compression == 0x3 or Compression == 0x7 or Compression == 0xB or Compression == 0x23 or Compression == 0x2B:
					compData = rapi.compressDeflate(decompData)
				elif Compression == 0x2:
					compData = decompData
				if compData is None:
					noesis.doException("Failed to compress a file while generating the archive.")
				division1 = (len(compData)/0x10)
				division2 = math.ceil(len(compData)/0x10)
				padComp = int((division2 - division1)*0x10)
				if padComp != 0:
					padCompLen = padComp
				else:
					padCompLen = 0
				padCompLen = 0
				Block1.write(compData)
				Block1.write(bytearray([0])*padCompLen)
				FileLen_fix[i] = FileLen + 0x40000000
				
				CompLen[i] = len(compData)
				Position1[i+1] = Position1[i] + len(compData) + padCompLen
			else:
				text = "WARNING: File " + name + " (type " + type + ") not found."
				print("WARNING: File", name, "(type", type,") not found.")
				noesis.doException(text)
	
	
	with open(IDsTable, "r+b") as g:
		Block1_position = os.path.getsize(IDsTable)
		
		Block2_position = Block1_position + Position1[NumIDs]
		#division1 = (Block2_position/0x80)
		#division2 = math.ceil(Block2_position/0x80)
		#padComp = int((division2 - division1)*0x80)
		#if padComp != 0:
		#	padCompLen2 = padComp
		#else:
		#	padCompLen2 = 0
		padCompLen2 = 0
		Block2_position = Block2_position + padCompLen2
		
		Block3_position = Block2_position + Position2[NumIDs]
		#division1 = (Block3_position/0x80)
		#division2 = math.ceil(Block3_position/0x80)
		#padComp = int((division2 - division1)*0x80)
		#if padComp != 0:
		#	padCompLen3 = padComp
		#else:
		#	padCompLen3 = 0
		padCompLen3 = 0
		Block3_position = Block3_position + padCompLen3
		
		Block4_position = Block3_position + Position3[NumIDs]
		#division1 = (Block4_position/0x80)
		#division2 = math.ceil(Block4_position/0x80)
		#padComp = int((division2 - division1)*0x80)
		#if padComp != 0:
		#	padCompLen4 = padComp
		#else:
		#	padCompLen4 = 0
		padCompLen4 = 0
		Block4_position = Block4_position + padCompLen4
		
		ResourceStringTable_position = Block4_position + Position4[NumIDs]
		#division1 = (ResourceStringTable_position/0x80)
		#division2 = math.ceil(ResourceStringTable_position/0x80)
		#padComp = int((division2 - division1)*0x80)
		#if padComp != 0:
		#	padCompLen5 = padComp
		#else:
		#	padCompLen5 = 0
		padCompLen5 = 0
		ResourceStringTable_position = ResourceStringTable_position + padCompLen5
		
		g.seek(0x8, NOESEEK_ABS)
		g.write(noePack(">i", ResourceStringTable_position))
		g.write(noePack(">i", NumIDs))
		g.seek(0x14, NOESEEK_ABS)
		g.write(noePack(">i", Block1_position))
		g.write(noePack(">i", Block2_position))
		g.write(noePack(">i", Block3_position))
		g.write(noePack(">i", Block4_position))
		g.write(noePack(">i", Compression))
		#g.write(noePack(">i", 0))
		for i in range(0, NumIDs):
			g.seek(IDsTab_start + i*0x48, NOESEEK_ABS)
			g.seek(0x8, NOESEEK_REL)
			g.write(noePack(">i", FileLen_fix[i]))
			g.write(noePack(">i", FileLen_fix2[i]))
			g.write(noePack(">i", FileLen_fix3[i]))
			g.write(noePack(">i", FileLen_fix4[i]))
			g.write(noePack(">i", CompLen[i]))
			g.write(noePack(">i", CompLen2[i]))
			g.write(noePack(">i", CompLen3[i]))
			g.write(noePack(">i", CompLen4[i]))
			g.write(noePack(">i", Position1[i]))
			g.write(noePack(">i", Position2[i]))
			g.write(noePack(">i", Position3[i]))
			g.write(noePack(">i", Position4[i]))
			g.write(noePack(">i", intIDs_position[i]))
			g.seek(0x4, NOESEEK_REL)					# Resource type
			g.write(noePack(">H", int(intIDs[i])))
			#g.seek(0x4, NOESEEK_REL)
			#g.write(noePack(">i", 0))
	Block1.close()
	Block2.close()
	Block3.close()
	Block4.close()
	IDsTable2 = open(IDsTable, "rb")
	Block1 = open(Block1Path, "rb")
	Block2 = open(Block2Path, "rb")
	Block3 = open(Block3Path, "rb")
	Block4 = open(Block4Path, "rb")
	OutputFilePath = srcPath + "\\" + OutputName + ".BNDL"
	OutputFile = open(OutputFilePath, "wb")
	OutputFile.write(IDsTable2.read())
	OutputFile.write(Block1.read())
	OutputFile.write(bytearray([0])*padCompLen2)
	OutputFile.write(Block2.read())
	OutputFile.write(bytearray([0])*padCompLen3)
	OutputFile.write(Block3.read())
	OutputFile.write(bytearray([0])*padCompLen4)
	OutputFile.write(Block4.read())
	OutputFile.write(bytearray([0])*padCompLen5)
	# ResourceStringTable
	ResourceStringTablePath = srcPath + "\\ResourceStringTable.xml"					# Path 1
	Name, ext = os.path.splitext(os.path.basename(IDsTable))
	ResourceStringTablePath2 = srcPath + "\\ResourceStringTable_" + Name[4:] + ".xml"	# Path 2
	if os.path.isfile(ResourceStringTablePath):
		ResourceStringTable = open(ResourceStringTablePath, "rb")
		OutputFile.write(ResourceStringTable.read())
		ResourceStringTable.close()
	elif os.path.isfile(ResourceStringTablePath2):
		ResourceStringTable = open(ResourceStringTablePath2, "rb")
		OutputFile.write(ResourceStringTable.read())
		ResourceStringTable.close()
	OutputFile.close()
	IDsTable2.close()
	Block1.close()
	Block2.close()
	Block3.close()
	Block4.close()
	os.remove(Block1Path)
	os.remove(Block2Path)
	os.remove(Block3Path)
	os.remove(Block4Path)
	noesis.freeModule(noeMod)
	print("Generated archive!")
	return 1

def id2type(type):
	list = {'00000000':'Raster',
		'00000001':'Material',
		'00000003':'TextFile',
		'0000000A':'VertexDesc',
		'0000000B':'0B (console only)',
		'0000000C':'Renderable',
		'0000000D':'0D (console only)',
		'0000000E':'TextureState',
		'0000000F':'MaterialState',
		'00000012':'ShaderProgramBuffer',
		'00000014':'ShaderParameter',
		'00000016':'Debug',
		'00000017':'KdTree',
		'00000019':'Snr',
		'0000001B':'AttribSysSchema',
		'0000001C':'AttribSysVault',
		'0000001E':'AptDataHeaderType',
		'0000001F':'GuiPopup',
		'00000021':'Font',
		'00000022':'LuaCode',
		'00000023':'InstanceList',
		'00000024':'CollisionMeshData (2006 build)',
		'00000025':'IdList',
		'00000027':'Language',
		'00000028':'SatNavTile',
		'00000029':'SatNavTileDirectory',
		'0000002A':'Model',
		'0000002B':'ColourCube',
		'0000002C':'HudMessage',
		'0000002D':'HudMessageList',
		'0000002E':'HudMessageSequence',
		'0000002F':'HudMessageSequenceDictionary',
		'00000030':'WorldPainter2D',
		'00000031':'PFXHookBundle',
		'00000032':'Shader',
		'00000041':'ICETakeDictionary',
		'00000042':'VideoData',
		'00000043':'PolygonSoupList',
		'00000045':'CommsToolListDefinition',
		'00000046':'CommsToolList',
		'00000051':'AnimationCollection',
		'0000A000':'Registry',
		'0000A020':'GenericRwacWaveContent',
		'0000A021':'GinsuWaveContent',
		'0000A022':'AemsBank',
		'0000A023':'Csis',
		'0000A024':'Nicotine',
		'0000A025':'Splicer',
		'0000A028':'GenericRwacReverbIRContent',
		'0000A029':'SnapshotData',
		'0000B000':'ZoneList',
		'00010000':'LoopModel',
		'00010001':'AISections',
		'00010002':'TrafficData',
		'00010003':'Trigger',
		'00010004':'DeformationModel (2006 build)',
		'00010005':'VehicleList',
		'00010006':'GraphicsSpec',
		'00010008':'ParticleDescriptionCollection',
		'00010009':'WheelList',
		'0001000A':'WheelGraphicsSpec',
		'0001000B':'TextureNameMap',
		'0001000C':'ICEList (2006 build)',
		'0001000D':'ICEData (2006 build)',
		'0001000E':'Progression',
		'0001000F':'PropPhysics',
		'00010010':'PropGraphicsList',
		'00010011':'PropInstanceData',
		'00010012':'EnvironmentKeyframe',
		'00010013':'EnvironmentTimeLine',
		'00010014':'EnvironmentDictionary',
		'00010015':'GraphicsStub',
		'00010016':'StaticSoundMap',
		'00010018':'StreetData',
		'00010019':'VFXMeshCollection',
		'0001001A':'MassiveLookupTable',
		'0001001B':'VFXPropCollection',
		'0001001C':'StreamedDeformationSpec',
		'0001001D':'ParticleDescription',
		'0001001E':'PlayerCarColours',
		'0001001F':'ChallengeList',
		'00010020':'FlaptFile',
		'00010021':'ProfileUpgrade',
		'00010023':'VehicleAnimation',
		'00010024':'BodypartRemapping',
		'00010025':'LUAList',
		'00010026':'LUAScript'}
	for ResourceID, ResourceType in list.items():
		if ResourceID == type:
			type = ResourceType
	return (type)

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