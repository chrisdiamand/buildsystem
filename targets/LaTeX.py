import os

class Target: # LaTeX
    def __init__(self, src, out = None):
        assert type(src) == str
        self.src = src
        if out == None:
            self.out = os.path.splitext(src)[0] + ".pdf"
        else:
            self.out = out

    def gen(self, fp):
        fp.write(self.out + ": " + self.src + " | Build\n")
        fp.write("\t@echo PDFLATEX $<\n")
        fp.write("\t@pdflatex -output-directory " + builddir +
                 " -halt-on-error $< > /tmp/pdflatex_log.txt" +
                 " || cat /tmp/pdflatex_log.txt\n")
        fp.write("\t@cp " + builddir + "/$(<:.tex=.pdf) " + self.out + "\n\n")

        fp.write("REMOVE_FILES += " + self.out + "\n\n")
        return self.out

def write_rule(fp):
    None
