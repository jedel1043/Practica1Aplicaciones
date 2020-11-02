
import sys
from operations import delete_files

delete_files(sys.argv[1], sys.argv[2::])