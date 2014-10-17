import latexdep
import os

class LaTeX(Target):
    def __init__(self, src, out = None):
        assert type(src) == str
        self.src = src
        self.deps = None
        if out == None:
            self.out = os.path.splitext(src)[0] + ".pdf"
        else:
            self.out = out

    def getMakeTarget(self):
        return self.out

    # Make sure it depends on any other files loaded with \include{}.
    def srcDepList(self):
        src_deps = latexdep.getDeps(self.src)
        if len(src_deps) == 0:
            return ""
        ret = ""
        for d in src_deps:
            ret = " " + d

        return ret

    def gen(self, fp):
        fp.write(self.out + ": " + self.src)
        fp.write(self.srcDepList())
        fp.write(" | Build\n")
        fp.write("\t@echo PDFLATEX $<\n")
        fp.write("\t@pdflatex -output-directory " + builddir +
                 " -halt-on-error $< > /tmp/pdflatex_log.txt" +
                 " || cat /tmp/pdflatex_log.txt\n")
        fp.write("\t@cp " + builddir + "/$(<:.tex=.pdf) " + self.out + "\n\n")

        fp.write("REMOVE_FILES += " + self.out + "\n\n")
