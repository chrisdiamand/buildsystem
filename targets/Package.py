class Target: # Package
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

def write_rule(fp):
    # Copy all the source files to the build directory,
    # using 'sed' to remove assertions if necessary.
    fp.write(builddir + "/%.java: %.java\n")
    fp.write("\t@mkdir -p $(@D)\n")
    fp.write("ifeq ($(NDEBUG),)\n")
    fp.write("\t@cp $< $@\n")
    fp.write("else\n")
    fp.write("\t@echo REMOVE_ASSERTS $<\n")
    fp.write("\t@sed -e 's/^\s*assert.*;$$/{}/' $< > $@\n")
    fp.write("endif\n\n")
    # Rule to actually compile .java source files. The pipe operator
    # means the directory has to exist, not be more recent.
    fp.write(builddir + "/%.class: Build/%.java | "
                           + builddir + "\n")
    # Print a pretty message showing what we're doing
    fp.write("\t@echo COMPILE $*.java\n");
    fp.write("\t@javac -d " + builddir
                                + " -sourcepath " + builddir
                                + " -Xlint $<\n")
    # Check the output file was actually created - the filename will
    # be wrong if the package doesn't match the file path.
    fp.write("\t@test -s $@ || { echo \"Error: $@ wasn't created.\"; "
                + "echo \"Wrong package name?\"; exit 1; }\n")
    fp.write("\n")
