class Target: # LaTeX
    def __init__(self, src):
        assert type(src) == str
        self.src = src
        self.out = os.path.splitext(src)[0] + ".pdf"

    def gen(self, fp):
        fp.write("REMOVE_FILES += " + self.out + "\n\n")
        return self.out

def write_rule(fp):
    fp.write("%.pdf: %.tex | Build\n")
    fp.write("\t@cp $< " + builddir + "/\n")
    fp.write("\t@echo PDFLATEX $<\n")
    fp.write("\t@cd " + builddir +
             " && ( pdflatex -halt-on-error $< > /tmp/pdflatex_log.txt" +
             " || cat /tmp/pdflatex_log.txt )\n")
    fp.write("\t@cp " + builddir + "/$@ .\n\n")
