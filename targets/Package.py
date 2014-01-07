import os

class Package(Target): # Package
    def __init__(self, name, classes, cp = []):
        assert type(name) == str
        assert type(classes) == list
        assert type(cp) == list
        for c in cp:    assert type(c) == str

        self.name = name
        self.path = name.replace(".", "/")
        self.sources = []
        self.classes = []
        self.classpath = cp
        self.deps = []

        for i in classes:
            dot = ""
            if self.name != "":
                dot = "."
            full_class = self.name + dot + i
            cl = JClass(full_class, cp = self.classpath)
            self.deps.append(cl)

            src_path = os.path.join(self.path, i + ".java")
            self.sources.append(src_path)
            out_path = os.path.join(builddir, self.path, i + ".class")
            self.classes.append(out_path)

    def gen(self, fp):
        pass

    # Return a list filenames which can be used as a make target
    # to build this package.
    def getMakeTarget(self):
        if self.deps == None:
            return ""
        # Depend on the classes in this package
        targets = [i.getMakeTarget() for i in self.deps]
        return " ".join(targets)

    def classList(self):
        return self.classes

    def sourceList(self):
        return self.sources
