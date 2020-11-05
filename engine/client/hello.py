import sys
import os

out = ""

for arg in sys.argv[1::]:
    out = out +" "+arg

print(out)