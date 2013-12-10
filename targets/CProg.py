import subprocess

C_COMPILER = "clang"
CFLAGS = "-Wall -pedantic -g"
CPP_COMPILER = "clang"
CCFLAGS = CFLAGS

def to_c_obj(fname):
    return os.path.join(builddir, os.path.splitext(fname)[0] + ".o")

class Target: # CProg
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

def write_rule(fp):
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
