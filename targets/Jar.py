import javadep
import os

class Manifest(Target):
    def __init__(self, fname, mainclass, classpath):
        self.fname = fname
        self.deps = None
        self.mainclass = mainclass
        self.classpath = classpath

    def getMakeTarget(self):
        return self.fname

    def gen(self, fp):
        fp.write(self.fname + ":\n")
        fp.write("\t@echo \'Manifest-Version: 1.0\' > "
                + self.fname + "\n")
        fp.write("\t@echo \'Main-Class: " + self.mainclass + "\' >> "
                + self.fname + "\n")
        if self.classpath != []:
            fp.write("\t@echo \'Class-Path:")
            for i in self.classpath:
                assert type(i) == str
                fp.write(" " + i)
            fp.write("\' >> " + self.fname + "\n")
        #fp.write("\techo \'\' >> " + self.manifest + "\n")
        fp.write("\n")

class Jar(Target):
    def __init__(self, name, mainclass, packages, cp = []):
        assert(type(name) == str)
        assert(type(mainclass) == str)
        assert(type(packages) == list)

        self.name = name;
        self.jarname = name + ".jar"
        self.mainclass = mainclass
        self.packages = packages
        self.deps = [i for i in packages]
        self.classpath = cp

        man_path = os.path.join(builddir, "manifest_" + self.name + ".txt")
        self.manifest = Manifest(man_path, mainclass, cp)
        self.deps.append(self.manifest)

    def getMakeTarget(self):
        return self.jarname

    def gen(self, fp):
        classes = []
        sources = []

        for i in self.packages:
            classes += i.classList()
            sources += i.sourceList()

        # Jar target and dependencies
        fp.write(self.jarname + ":" + self.getMakeDeps() + "\n")

        # Print out a pretty message
        fp.write("\t@echo BUILDJAR " + self.jarname + "\n")
        # The 'jar' command to create it
        fp.write("\t@cd " + builddir + " && "
               + "jar cfm " + "../" + self.jarname
               + " ../" + self.manifest.fname)
        # Include the source files in the jar
        for fname in sources:
            fp.write(" -C .. " + fname)
        # Include all class files from relevant packages
        for pkg in self.packages:
            fp.write(" `find -path './" + pkg.path + "/*.class'`")
        fp.write("\n\t@chmod +x " + self.jarname + "\n\n");

        fp.write("REMOVE_FILES += " + " ".join(classes) + " "
                                    + self.jarname + " "
                                    + self.manifest.fname + "\n\n")
