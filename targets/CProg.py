import os
import subprocess

C_COMPILER = "clang"
CPP_COMPILER = "clang++"
DEFAULT_CFLAGS = "-Wall -pedantic -g"
DEFAULT_CCFLAGS = DEFAULT_CFLAGS

def to_c_obj(fname):
    return os.path.join(builddir, os.path.splitext(fname)[0] + ".o")

class ObjectFile(Target):
    def __init__(self, src, flags = None):
        self.src = src
        self.out = to_c_obj(src)
        self.flags = flags
        self.deps = None

    def getMakeTarget(self):
        return self.out

    def getDeps(self):
        cmd = [C_COMPILER, "-MM", "-MT", self.out, self.src]
        d = subprocess.check_output(cmd).decode("utf-8")
        assert type(d) == str
        return d.strip()

class CObject(ObjectFile):
    def gen(self, fp):
        if self.flags == None:
            self.flags = DEFAULT_CFLAGS

        fp.write("%s" % (self.getDeps()))
        fp.write(" | " + builddir + "\n")
        fp.write("\t@echo CC " + self.src + "\n")
        fp.write("\t@" + C_COMPILER + " " + self.flags)
        fp.write(" -c -o " + self.out + " " + self.src + "\n\n")

class CPPObject(ObjectFile):
    def gen(self, fp):
        if self.flags == None:
            self.flags = DEFAULT_CCFLAGS

        fp.write(self.getDeps())
        fp.write(" | " + builddir + "\n")
        fp.write("\t@echo CPP " + self.src + "\n")
        fp.write("\t@" + CPP_COMPILER + " " + self.flags)
        fp.write(" -c -o " + self.out + " " + self.src + "\n\n")

def objectFile(src, cflags = None):
    ext = os.path.splitext(src)[1].lower().strip()
    if ext == ".cpp" or ext == ".cc":
        return CPPObject(src, flags = cflags)
    return CObject(src, flags = cflags)

class CProg(Target):
    def __init__(self, name, sources, cflags = DEFAULT_CFLAGS):
        assert type(name) == str
        assert type(sources) == list

        self.name = name
        self.sources = sources
        self.cflags = cflags
        self.deps = []
        for i in sources:
            self.deps.append(objectFile(i, cflags))

        self.cpp = False
        for i in self.deps:
            if type(i) == CPPObject:
                self.cpp = True
                break

    def getMakeTarget(self):
        return self.name

    def gen(self, fp):
        objlist = " ".join([i.out for i in self.deps])
        fp.write(self.name + ": " + objlist + "\n")
        fp.write("\t@echo LINK " + objlist + "\n")
        fp.write("\t@" + C_COMPILER + " " + self.cflags + " -o $@ " + objlist)
        if self.cpp:
            fp.write(" -lstdc++")
        fp.write("\n\n")

        fp.write("\nREMOVE_FILES += " + self.name + " " + objlist + "\n\n")

if False:
    #def write_rule(fp):
    fp.write("CC = " + C_COMPILER + "\n")
    fp.write("CPP = " + CPP_COMPILER + "\n")
    fp.write("CFLAGS = " + Target.CFLAGS + "\n")
    fp.write("CCFLAGS = " + Target.CCFLAGS + "\n\n")

    fp.write(os.path.join(builddir, "%.o: %.c | " + builddir + "\n"))
    fp.write("\t@echo CC $<\n")
    fp.write("\t@$(CC) $(CFLAGS) -c -o $@ $<\n\n")

    fp.write(os.path.join(builddir, "%.o: %.cpp | " + builddir + "\n"))
    fp.write("\t@echo CPP $<\n")
    fp.write("\t@$(CPP) $(CCFLAGS) -c -o $@ $<\n\n")
