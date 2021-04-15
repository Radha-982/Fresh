import subprocess
from subprocess import Popen,PIPE
#print(Popen("git config --list",shell=True,stdout=subprocess.PIPE).communicate())
import os
os.chdir("F:/GIT")
s=Popen("git clone https://github.com/Radha-982/temp.git",shell=True,stdout=subprocess.PIPE)


'''import os
os.chdir("F:/GIT/temp")'''
#print(Popen("git status",shell=True,stdout=subprocess.PIPE).communicate())
#print(Popen("git checkout -b Radha",shell=True,stdout=subprocess.PIPE).communicate())
#print(Popen("git add --a",shell=True,stdout=subprocess.PIPE).communicate())
#print(Popen("git status",shell=True,stdout=subprocess.PIPE).communicate())
'''print(Popen('git commit -m "Now its oky"',shell=True,stdout=subprocess.PIPE).communicate())
print(Popen("git remote add origin https://github.com/Radha-982/temp.git",shell=True,stdout=subprocess.PIPE).communicate())
print(Popen("git push -u origin radha",shell=True,stdout=subprocess.PIPE).communicate())'''