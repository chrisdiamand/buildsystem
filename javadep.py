#!/usr/bin/env python

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

# Search the source file for the 'package' statement
def getPackage(lines):
    assert type(lines) == list
    for l in lines:
        l = l.strip()
        if l.startswith("package "):
            pkg = l.split()[1]
            # Remove the semicolon
            pkg = pkg[0:-1]
            return pkg
    return ""

# Search the source file for 'import' statements
def getImports(lines):
    assert type(lines) == list
    imports = []
    for l in lines:
        l = l.strip()
        if l.startswith("import "):
            pkg = l.split()[1]
            pkg = pkg[0:-1]
            imports.append(pkg)
    return imports

# Look through the directory the file is in for
# other java classes in the same package.
def getOtherClassesInPackage(fname):
    thisClass = os.path.basename(fname)
    [thisClass, ext] = os.path.splitext(thisClass)
    if ext.lower() != ".java":
        print "Error: Not a Java source file:", fname
        sys.exit(1)
    dirname = os.path.dirname(fname)
    classes = []
    for i in os.listdir(dirname):
        [classname, ext] = os.path.splitext(i)
        if ext == ".java" and classname != thisClass:
            classes.append(classname)
    return classes

# Search the source file for references to other classes in
# the same package. Return a list of fully-specified class names.
def getPackageDeps(lines, classes, package):
    deps = []
    regexps = []
    for cl in classes:
        regexp = re.compile(r"\b" + cl + r"\b")
        regexps.append(regexp)
    for line in lines:
        for i, cl_re in enumerate(regexps):
            if cl_re.search(line) != None:
                cl = package + "." + classes[i]
                if not cl in deps:
                    deps.append(package + "." + classes[i])
    return deps

def packageRoot(fname, package):
    assert type(fname) == str
    assert type(package) == str
    # Get the 'base' directory
    numdots = package.count(".")
    dirname = os.path.dirname(fname)
    for i in range(0, numdots + 1):
        dirname = os.path.join(dirname, "..")
    dirname = os.path.abspath(dirname)
    return dirname

def getImportDeps(fname, imports, package):
    assert type(fname) == str
    assert type(imports) == list

    deps = []
    root = packageRoot(fname, package)

    for cl in imports:
        path = cl.replace(".", "/")
        path = os.path.join(root, path + ".java")
        if os.path.exists(path):
            deps.append(cl)
    return deps

def getDeps(fname):
    fp = open(fname, "r")
    lines = fp.readlines()
    fp.close()

    package = getPackage(lines)
    imports = getImports(lines)

    otherPackageClasses = getOtherClassesInPackage(fname)
    packageDeps = getPackageDeps(lines, otherPackageClasses, package)

    importDeps = getImportDeps(fname, imports, package)
    return packageDeps + importDeps

def main():
    args = parseArgs()
    deps = getDeps(args.infile)
    for i in deps:
        i = i.replace(".", "/")
        print os.path.join(args.build_dir, i + ".java")

if __name__ == "__main__":
    main()
