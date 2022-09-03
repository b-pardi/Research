import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'pandas'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'numpy'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'matplotlib'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'pathlib'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'openpyxl'])

# xlrd library deprecated support for xlsx files, so using older version
# alternatively could use openpyxl and put "engine='openpyxl'" arg into each read_excel call
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'xlrd==1.2.0'])