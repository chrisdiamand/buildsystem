import os

class Package(Target): # Package
    def __init__(self, name, classes):
        assert(type(name) == str)
        assert(type(classes) == list)

        self.name = name
        self.path = name.replace(".", "/")
        self.sources = []
        self.classes = []
        self.deps = []

        for i in classes:
            if self.name != "":
                i = "." + i
            full_class = self.name + i
            cl = JClass(full_class)
            self.deps.append(cl)

            src_path = os.path.join(self.path, i + ".java")
            self.sources.append(src_path)
            out_path = os.path.join(builddir, self.path, i + ".class")
            self.classes.append(out_path)

    # Return a list filenames which can be used as a make target
    # to build this package.
    def getMakeTarget(self):
        # Depend on the classes in this package
        targets = [i.getMakeTarget() for i in self.deps]
        return " ".join(targets)

    def classList(self):
        return self.classes

    def sourceList(self):
        return self.sources
