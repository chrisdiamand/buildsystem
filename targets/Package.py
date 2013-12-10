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
