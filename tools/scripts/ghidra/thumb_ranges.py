# Reports where the listing holds Thumb instructions (TMode = 1), as runs of
# consecutive Thumb instructions (a gap of more than GAP bytes starts a new run),
# plus the count of functions whose entry is Thumb. Changes nothing.
# Args: optional gap in bytes with an "s" prefix (default s256), e.g. "s256".
#
# @category ZK-Inkjet
# @runtime Jython

args = getScriptArgs()
GAP = int(args[0].lstrip("s")) if args else 256

tmode = currentProgram.getProgramContext().getRegister("TMode")
runs = []
start = last = None
n_thumb = n_arm = 0
it = currentProgram.getListing().getInstructions(True)
while it.hasNext():
    if monitor.isCancelled():
        break
    ins = it.next()
    v = ins.getValue(tmode, False)
    if v is not None and int(v) == 1:
        n_thumb += 1
        a = ins.getAddress().getOffset()
        if start is None:
            start = a
        elif a - last > GAP:
            runs.append((start, last))
            start = a
        last = a + ins.getLength()
    else:
        n_arm += 1
if start is not None:
    runs.append((start, last))

println("instructions: ARM %d, Thumb %d" % (n_arm, n_thumb))
println("Thumb runs (gap > %d bytes splits): %d" % (GAP, len(runs)))
for s, e in runs:
    println("  0x%08X-0x%08X  %d bytes  (file+0x%X-0x%X)" % (s, e, e - s, s - 0x58000, e - 0x58000))

fn_thumb = 0
fn_all = 0
for f in currentProgram.getFunctionManager().getFunctions(True):
    fn_all += 1
    ins = currentProgram.getListing().getInstructionAt(f.getEntryPoint())
    if ins is not None:
        v = ins.getValue(tmode, False)
        if v is not None and int(v) == 1:
            fn_thumb += 1
println("functions: %d, Thumb entry: %d" % (fn_all, fn_thumb))
println("done")
