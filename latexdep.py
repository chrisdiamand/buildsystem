#!/usr/bin/env python3

import argparse
import os
import re
import sys

def parseArgs():
    p = argparse.ArgumentParser(description =
        "Work out Java class depencies")
    p.add_argument("--build-dir", "-b", type = str, metavar = "DIR",
                   help = "Set the build directory", default = "")
    p.add_argument("infile", metavar = "FILENAME", type = str)
    args = p.parse_args()
    return args

# Search the source file for references to other classes in
# the same package. Return a list of fully-specified class names.
def getIncludes(lines):
    deps = []
    regexp = re.compile(r'^\s*\\include\{(\S+)\}')
    for line in lines:
        m = regexp.match(line)
        if m:
            deps.append(m.group(1))
    return deps

# Convert extensionless includes into real file names.
def findFiles(deps):
    ret = []
    for d in deps:
        if len(os.path.splitext(d)[1]) == 0:
            d = d + ".tex"
        ret.append(d)
    return ret

def getDeps(fname):
    fp = open(fname, "r")
    lines = fp.readlines()
    fp.close()

    includes = getIncludes(lines)
    includes = findFiles(includes)

    return includes

def main():
    args = parseArgs()
    deps = getDeps(args.infile)
    for i in deps:
        print(i)

if __name__ == "__main__":
    main()
