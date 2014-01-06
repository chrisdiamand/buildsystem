import javadep
import os

class Jar(Target):
    def __init__(self, name, mainclass, packages, cp = []):
        assert(type(name) == str)
        assert(type(mainclass) == str)
        assert(type(packages) == list)

        self.name = name;
        self.jarname = name + ".jar"
        self.mainclass = mainclass
        self.packages = packages
        self.classpath = cp
        self.manifest = os.path.join(builddir, "manifest_" + self.name + ".txt")

    def writeManifestRule(self, fp):
        fp.write(self.manifest + ":\n")
        fp.write("\t@echo \'Manifest-Version: 1.0\' > "
                + self.manifest + "\n")
        fp.write("\t@echo \'Main-Class: " + self.mainclass + "\' >> "
                + self.manifest + "\n")
        if self.classpath != []:
            fp.write("\t@echo \'Class-Path:")
            for i in self.classpath:
                assert type(i) == str
                fp.write(" " + i)
            fp.write("\' >> " + self.manifest + "\n")
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
