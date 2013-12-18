class Target: # Custom rule
    def __init__(self, target, deps, rules):
        assert type(target) == str
        assert type(deps) == list
        assert type(rules) == list
        self.target = target    # Target name
        self.deps = deps        # Dependencies
        self.rules = rules      # Commands to build it

    def gen(self, fp):
        fp.write(self.target + ":")
        for d in self.deps:
            fp.write(" " + d)
        fp.write("\n")
        for r in self.rules:
            fp.write("\t" + r + "\n")
        fp.write("\n")
        fp.write("REMOVE_FILES += " + self.target + "\n\n")

        return self.target

def write_rule(fp):
    None
