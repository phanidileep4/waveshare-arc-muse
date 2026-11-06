#!/usr/bin/env python3
"""Mac host-test adapter only; never use as the ESP32 cross compiler."""
import os, sys
args=[]
for arg in sys.argv[1:]:
    if arg == '-no-pie':
        continue
    args.append('-Wl,-dead_strip' if arg == '-Wl,--gc-sections' else arg)
os.execv('/usr/bin/clang', ['clang', *args, '-Wno-error=deprecated-declarations'])
