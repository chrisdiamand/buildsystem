class Custom(Target):
    def __init__(self, target, depends, rules):
        assert type(target) == str
        assert type(depends) == list
        assert type(rules) == list
        self.target = target    # Target name
        self.depends = depends  # Dependencies
        self.deps = None
        self.rules = rules      # Commands to build it

    def getMakeTarget(self):
        return self.target

    def gen(self, fp):
        fp.write(self.target + ":")
        for d in self.depends:
            fp.write(" " + d)
        fp.write("\n")
        for r in self.rules:
            fp.write("\t" + r + "\n")
        fp.write("\n")
        fp.write("REMOVE_FILES += " + self.target + "\n\n")

        return self.target
