from idautils import *
from idc import *

auto_wait()

funcs = []

for offset in Functions():
    flags = GetFunctionFlags(offset)
    #if flags & FUNC_LIB or flags & FUNC_THUNK:
    #    funcs.append("skip")
    #    continue

    funcs.append(GetFunctionName(offset))

with open("funcs", "w") as f:
    f.write("\n".join(funcs))

Exit(0)
