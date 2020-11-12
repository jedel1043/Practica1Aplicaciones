import sys
from operations import download_files

download_files(sys.argv[1], sys.argv[2::])
print("finished")