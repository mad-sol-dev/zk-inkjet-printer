# Count functions by size
from ghidra.program.model.address import AddressSet

program = currentProgram()
functionManager = program.getFunctionManager()
addrFactory = program.getAddressFactory()
defaultSpace = addrFactory.getDefaultAddressSpace()

# Define FLASH range
startAddr = defaultSpace.getAddress(0x00200000)
endAddr = defaultSpace.getAddress(0x0047522B)
flashRange = AddressSet(startAddr, endAddr)

# Count by size buckets
size_buckets = {
    "1-4 bytes": 0,
    "5-16 bytes": 0,
    "17-64 bytes": 0,
    "65-256 bytes": 0,
    "257+ bytes": 0
}

total = 0
functionIter = functionManager.getFunctions(flashRange, True)
for func in functionIter:
    size = func.getBody().getNumAddresses()
    total += 1
    
    if size <= 4:
        size_buckets["1-4 bytes"] += 1
    elif size <= 16:
        size_buckets["5-16 bytes"] += 1
    elif size <= 64:
        size_buckets["17-64 bytes"] += 1
    elif size <= 256:
        size_buckets["65-256 bytes"] += 1
    else:
        size_buckets["257+ bytes"] += 1

print("Function Size Distribution:")
print("---------------------------")
for bucket, count in sorted(size_buckets.items()):
    pct = (count * 100.0 / total) if total > 0 else 0
    print("{:15} : {:6} ({:5.1f}%)".format(bucket, count, pct))
print("---------------------------")
print("Total: {}".format(total))
