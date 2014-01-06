import os

class Zip(Target):
    def __init__(self, fname, contents):
        assert type(fname) == str
        assert type(contents) == list
        self.fname = fname
        self.contents = contents

    def gen(self, fp):
        fp.write(self.fname + ":")
        for c in self.contents:
            fp.write(" " + c)
        fp.write("\n")
        fp.write("\t@echo ZIP " + self.fname + "\n")
        fp.write("\t@zip --quiet " + self.fname)
        for c in self.contents:
            fp.write(" " + c)
        fp.write("\n\n")

        fp.write("REMOVE_FILES += " + self.fname+ "\n\n")
        return self.fname
