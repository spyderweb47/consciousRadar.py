#!/usr/bin/env python3

import sys
import subprocess
import os
import argparse
from functools import wraps
import errno
import os
import signal

log_location="/opt/tools/spydertool/Log-consciousRadar/"

class TimeoutError(Exception):
	pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
	def decorator(func):
		def _handle_timeout(signum, frame):
			raise TimeoutError(error_message)

		def wrapper(*args, **kwargs):
			signal.signal(signal.SIGALRM, _handle_timeout)
			signal.alarm(seconds)
			try:
				result = func(*args, **kwargs)
			finally:
				signal.alarm(0)
			return result

		return wraps(func)(wrapper)

	return decorator


#for argument
def get_args():
	parser = argparse.ArgumentParser("consciousRadar.py -f path/to/folder OR consciousRadar.py for cureent folder")
	parser.add_argument('-f','--folder-path',dest='folderlocation',help="Path of Folder",default="False")
	parser.add_argument('-p','--project-name',dest='projectname',help="Project Name",default="False")	

	args = parser.parse_args()
	return args


#input folder location
if (get_args().folderlocation == "False"):
	current_path=subprocess.check_output(f"pwd",shell=True,text=True)
	current_path=current_path.strip("\n")
	folderlocation=current_path
else:
	folderlocation=get_args().folderlocation

#project name input
if (get_args().projectname == "False"):
	project=input("Enter Project name: ")
else:
	project=get_args().projectname


#folder data extracter
folderfiles=subprocess.check_output(''' ls -p '''+folderlocation+ ''' |grep -i / |sed 's/\\///g'|xargs -i sh -c "tree -a -f -i -n|sed 's/\\.\\///g'"|sort -u''',shell=True,text=True)
filelist=folderfiles.split("\n")
filelist.remove("")


#xgf pattern list
patterns=subprocess.check_output("xgf --list",shell=True,text=True)
pattern_list=patterns.split("\n")
pattern_list.remove("")

#devnull
DNULL=open(os.devnull,"w")

def dupe(arg):
	with open(f'{log_location}{project}.log', 'a') as log:
		print(arg)
		log.write(arg)



#xgf check function for each file

@timeout(15)
def xgf_check(filename):
		
	# dupe(f"\nFilename:     {folderlocation}/{filename}")
	# #dupe(f"File Location:  {folderlocation}")
	# print(colored(f"  |","green"))


	try:
		if filename.endswith('.js'):
			for key in pattern_list:
				try:
					check_cmd=subprocess.check_output(f"cat {folderlocation}/{filename} | js-beautify | xgf {key}",shell=True,text=True,stderr=DNULL)
					if(len(check_cmd) > 1):
						dupe(f"Filename:     {folderlocation}/{filename}")
						dupe(f"  |-{key}")
						dupe(f"\n{check_cmd}")
						print("---------------------\n")
					else:
						pass
				except:
					pass

		else:
			for key in pattern_list:
				try:
					check_cmd=subprocess.check_output(f"cat {folderlocation}/{filename} | xgf {key}",shell=True,text=True,stderr=DNULL)
					if(len(check_cmd) > 1):
						dupe(f"Filename:     {folderlocation}/{filename}")
						dupe(f"  |-{key}")
						dupe(f"\n{check_cmd}")
						print("---------------------\n")
					else:
						pass
				except:
					pass
	except:
		print(f"errot {filename}")
	#unconditional only for automation
	#dupe(f"  |   File Location:  {folderlocation}")
	# print("---------------------\n")



#to save output
#main
for file in filelist:
	xgf_check(file)
