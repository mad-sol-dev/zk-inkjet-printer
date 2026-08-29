Investigate this question about the ZK-Inkjet firmware and follow your report protocol.

QUESTION: The English UI string table occupies virtual addresses 0x3F2890 to 0x3F32FC
(200 null-terminated strings, 4-byte aligned). Does any 32-bit word anywhere in
firmware/bin/ZK-INKJET-NANO-APP.bin hold the address of the start of one of those
strings? Search 4-aligned and unaligned.

A negative result here is only acceptable if your probe also demonstrates, in the same
run, that the identical method DOES find pointers to strings that are known to be
referenced. Choose such a control yourself from the binary, justify the choice, and
print its result. Without a passing control, report INCONCLUSIVE.
