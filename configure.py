#!/usr/bin/env python

import javadep
import os
import subprocess
import sys

builddir = "Build"

C_COMPILER = "clang"
CFLAGS = "-Wall -pedantic -g"
CPP_COMPILER = "clang"
CCFLAGS = CFLAGS

def to_c_obj(fname):
    return os.path.join(builddir, os.path.splitext(fname)[0] + ".o")

class CProg:
    def __init__(self, name, sources):
        assert type(name) == str
        assert type(sources) == list

        self.name = name
        self.sources = sources
        self.obj = []
        self.cpp = False
        for i in sources:
            ext = os.path.splitext(i)[1].lower().strip()
            if ext == ".cpp" or ext == ".cc":
                self.cpp = True
            self.obj.append(to_c_obj(i))

    def getDeps(self, fname):
        cmd = [C_COMPILER, "-MM", "-MT", to_c_obj(fname), fname]
        return subprocess.check_output(cmd).strip()

    def gen(self, fp):
        objlist = " ".join(self.obj)
        fp.write(self.name + ": " + objlist + "\n")
        fp.write("\t@echo LINK " + objlist + "\n")
        fp.write("\t@$(CC) $(CFLAGS) -o $@ " + objlist)
        if self.cpp:
            fp.write(" -lstdc++")
        fp.write("\n\n")

        # Get the dependencies between object files and
        # source/header files
        for i in self.sources:
            fp.write(self.getDeps(i) + "\n")

        fp.write("\nREMOVE_FILES += " + self.name + " " + objlist + "\n\n")

        return self.name

class LaTeX:
    def __init__(self, src):
        assert type(src) == str
        self.src = src
        self.out = os.path.splitext(src)[0] + ".pdf"

    @staticmethod
    def write_rule(fp):
        fp.write("%.pdf: %.tex | Build\n")
        fp.write("\t@cp $< " + builddir + "/\n")
        fp.write("\t@echo PDFLATEX $<\n")
        fp.write("\t@cd " + builddir +
                 " && ( pdflatex -halt-on-error $< > /tmp/pdflatex_log.txt" +
                 " || cat /tmp/pdflatex_log.txt )\n")
        fp.write("\t@cp " + builddir + "/$@ .\n\n")

    def gen(self, fp):
        fp.write("REMOVE_FILES += " + self.out + "\n\n")
        return self.out

class Package:
    def __init__(self, name, classes):
        assert(type(name) == str)
        assert(type(classes) == list)

        self.name = name
        self.path = name.replace(".", "/")
        self.sources = []
        self.classes = []

        for i in classes:
            self.sources.append(self.path + "/" + i + ".java")
            self.classes.append(builddir + "/" + self.path + "/" + i + ".class")

    def classList(self):
        return self.classes

    def sourceList(self):
        return self.sources

class Jar:
    def __init__(self, name, mainclass, packages):
        assert(type(name) == str)
        assert(type(mainclass) == str)
        assert(type(packages) == list)

        self.name = name;
        self.jarname = name + ".jar"
        self.mainclass = mainclass
        self.packages = packages
        self.manifest = os.path.join(builddir, "manifest_" + self.name + ".txt")

    def writeManifestRule(self, fp):
        fp.write(self.manifest + ":\n")
        fp.write("\t@echo \'Manifest-Version: 1.0\' > "
                + self.manifest + "\n")
        fp.write("\t@echo \'Main-Class: " + self.mainclass + "\' >> "
                + self.manifest + "\n")
        #fp.write("Class-Path: ...\n")
        #fp.write("\techo \'\' >> " + self.manifest + "\n")
        fp.write("\n")

    def gen(self, fp):
        classes = []
        sources = []
        gensources = []
        for i in self.packages:
            classes += i.classList()
            sources += i.sourceList()
        for i in sources:
            gensources.append(os.path.join(builddir, i))

        gensources_str = " ".join(gensources)

        # Jar target and dependencies
        fp.write(self.jarname + ": " + gensources_str + " "
                              + " ".join(classes)
                              + " " + self.manifest + "\n")
        # Print out a pretty message
        fp.write("\t@echo BUILDJAR " + self.jarname + "\n")
        # The 'jar' command to create it
        fp.write("\t@cd " + builddir + " && "
               + "jar cfm " + "../" + self.jarname
               + " ../" + self.manifest)
        # Include the source files in the jar
        for fname in sources:
            fp.write(" " + fname)
        # Include all class files from relevant packages
        for pkg in self.packages:
            fp.write(" `find -path './" + pkg.path + "/*.class'`")
        fp.write("\n\t@chmod +x " + self.jarname + "\n\n");

        self.writeManifestRule(fp)

        gsvar_name = "GENERATED_SOURCES_" + self.name.replace("-", "_")
        fp.write(gsvar_name + " = " + gensources_str + "\n\n")
        fp.write("REMOVE_FILES += " + " ".join(classes) + " "
                                    + self.jarname + " "
                                    + gsvar_name + " "
                                    + self.manifest + "\n\n")

        # Generate dependencies between class files and the
        # .java source files they require for compilation.
        for src in sources:
            deps = javadep.getDeps(src)
            if len(deps) == 0:
                continue

            classname = os.path.splitext(src)[0] + ".class"
            classname = os.path.join(builddir, classname)
            fp.write(classname + ":")
            for cl in deps:
                assert type(cl) == str
                cl = cl.replace(".", "/")
                cl = os.path.join(builddir, cl + ".java")
                fp.write(" " + cl)
            fp.write("\n")
        fp.write("\n")

        return self.jarname;

class Makefile:
    def __init__(self, jars):
        self.jars = jars

    def write_c_rule(self, fp):
        fp.write("CC = " + C_COMPILER + "\n")
        fp.write("CPP = " + CPP_COMPILER + "\n")
        fp.write("CFLAGS = " + CFLAGS + "\n")
        fp.write("CCFLAGS = " + CCFLAGS + "\n\n")

        fp.write(os.path.join(builddir, "%.o: %.c | " + builddir + "\n"))
        fp.write("\t@echo CC $<\n")
        fp.write("\t@$(CC) $(CFLAGS) -c -o $@ $<\n\n")

        fp.write(os.path.join(builddir, "%.o: %.cpp | " + builddir + "\n"))
        fp.write("\t@echo CPP $<\n")
        fp.write("\t@$(CPP) $(CCFLAGS) -c -o $@ $<\n\n")

    def gen(self, outfile):
        outfile.write("# Autogenerated by " + sys.argv[0] + " - do not edit\n\n")
        outfile.write(".PHONY: all\n")
        outfile.write("all: everything\n\n")
        jartargets = " ".join([i.gen(outfile) for i in self.jars])

        # 'everything' target, now that we know all the jar files to build
        outfile.write(".PHONY: everything\n")
        outfile.write("everything: " + jartargets + "\n\n")

        # Copy all the source files to the build directory,
        # using 'sed' to remove assertions if necessary.
        outfile.write(builddir + "/%.java: %.java\n")
        outfile.write("\t@mkdir -p $(@D)\n")
        outfile.write("ifeq ($(NDEBUG),)\n")
        outfile.write("\t@cp $< $@\n")
        outfile.write("else\n")
        outfile.write("\t@echo REMOVE_ASSERTS $<\n")
        outfile.write("\t@sed -e 's/^\s*assert.*;$$/{}/' $< > $@\n")
        outfile.write("endif\n\n")

        # Rule to actually compile .java source files. The pipe operator
        # means the directory has to exist, not be more recent.
        outfile.write(builddir + "/%.class: Build/%.java | "
                               + builddir + "\n")
        # Print a pretty message showing what we're doing
        outfile.write("\t@echo COMPILE $*.java\n");
        outfile.write("\t@javac -d " + builddir
                                    + " -sourcepath " + builddir
                                    + " -Xlint $<\n")
        # Check the output file was actually created - the filename will
        # be wrong if the package doesn't match the file path.
        outfile.write("\t@test -s $@ || { echo \"Error: $@ wasn't created.\"; "
                    + "echo \"Wrong package name?\"; exit 1; }\n")
        outfile.write("\n")

        LaTeX.write_rule(outfile)
        self.write_c_rule(outfile)

        # Make sure the build directory exists
        outfile.write(builddir + ":\n")
        outfile.write("\t@mkdir -p " + builddir + "\n\n")

        # make clean
        outfile.write(".PHONY: clean\n")
        outfile.write("clean:\n")
        outfile.write("\t@rm -Rf $(REMOVE_FILES) "
                      + builddir + "\n");

# Load the project definition from 'project.py'.
project_globals = {
    "CProg"     :   CProg,
    "LaTeX"     :   LaTeX,
    "Jar"       :   Jar,
    "Makefile"  :   Makefile,
    "Package"   :   Package }

try:
    execfile("project.py", project_globals)
except IOError as e:
    print "Error: " + e.strerror + ": '" + e.filename + "'"
    sys.exit(1)

makefile = project_globals["makefile"]

# Generate the Makefile.
outfile = open("Makefile", "w")
makefile.gen(outfile)
outfile.close()
