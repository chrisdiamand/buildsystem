import javadep
import os

class JClass(Target):
    # cl: a .-separated java class spec e.g. "uk.ac.cam.cd493.Something"
    # cp: a list of strings containing classpath entries
    def __init__(self, cl, cp = []):
        self.jclass = cl
        # Path to the source (.java) file
        self.srcpath = cl.replace(".", "/") + ".java"
        # Path to the generated (.class) file
        self.outpath = os.path.join(builddir,
                                    cl.replace(".", "/") + ".class")
        self.classpath = cp
        self.deps = []

    def getMakeTarget(self):
        return self.outpath

    # Get the source files it depends on and put then into a
    # space-separated list as the targets of a makefile rule.
    def srcDepList(self):
        src_deps = javadep.getDeps(self.srcpath)
        if len(src_deps) == 0:
            return ""

        ret = ""
        for d in src_deps:
            d = d.replace(".", "/") + ".java"
            ret += " " + d

        return ret

    def gen(self, fp):
        out = self.outpath
        src = self.srcpath

        # Rule to actually compile .java source files. The pipe operator
        # means the directory has to exist, not be more recent.
        fp.write(out + ": " + src)
        fp.write(self.srcDepList())
        fp.write(" | " + builddir + "\n")
        # Print a message for each compiled file
        fp.write("\t@echo JAVAC " + src + "\n")
        # Compile it
        fp.write("\t@javac -d " + builddir + " -Xlint " + src + "\n")
        # Check the output file was actually created - the filename will
        # be wrong if the package doesn't match the file path.
        fp.write("\t@test -s '" + out +
                 "' || { echo \"Error: '" + out + "' wasn't created.\"; " +
                 "echo \"Wrong package name?\"; exit 1; }\n")
        fp.write("\n")
