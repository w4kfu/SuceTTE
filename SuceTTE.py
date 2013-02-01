import os
import sys

TEMPLATE="page.html"
OUTDIR="out/"
CSS="style.css"
SITETITLE="Bordel"

custom_tags = []

def tag(function):
    custom_tags.append((function.__name__, function))
    return function


def ReadFile(filename):
    with open(filename, "r") as f:
        return f.read()
@tag
def SiteTitle():
	return SITETITLE

def WriteFile(path, filename, content):
    if not os.path.exists(path):
        os.mkdir(path)
    with open(os.path.join(path, filename), "w") as f:
        f.write(content)

def ReadLines(filename):
    with open(filename,"r") as f:
        return list(f)

def ParseSections(lines):
	sections = {}
	section = []

	for tag_name, tag_function in custom_tags:
		sections[tag_name] = tag_function()

	name = "__nosection__"
	for line in lines:
		if line.startswith("$$"):
			sections[name] = "".join(section).strip()
			section = []
			name = line[2:].strip()
		else:
			section.append(line)

	sections[name] = "".join(section)
	sections[name].strip()
	return sections

def ReadSections(filename):
	lines = ReadLines(filename)
	sections = ParseSections(lines)
	return sections

def MakeLink(dest, content):
	return '<a href="%s"/>%s</a>' % (dest, content)

def MakeMenuEntry(dest, content):
	menuentry = '<li class="link">' + MakeLink(dest, content) + '</li>\n'
	return menuentry

def MakeMenu(sections, menu):
	outmenu = "<ul>\n"
	for entry in menu:
		outmenu += MakeMenuEntry(os.path.join(entry, menu[entry]), entry)
	outmenu += "</ul>"
	sections["menu"] = outmenu
	return sections

def SubMenu(sections):
	return "TODO"

def MakeOutputName(filename):
	if filename.endswith(".tte"):
		basename = filename[:-4]
	else:
		basename = filename
	return basename + ".html"

def ReplaceSections(template, sections):
	for section in sections:
		tag = "{{" + section + "}}"
		template = template.replace(tag, "".join(sections[section]))
	return template

def MakeRootIndex(rootfolder, template, directory, outdir):
	rootmenu = {}
	for entry in directory:
		if os.path.isdir(os.path.join(rootfolder, entry)):
			rootmenu[entry] = "index.html"
			MakeRootIndex(os.path.join(rootfolder, entry), template, os.listdir(os.path.join(rootfolder, entry)), os.path.join(outdir, entry))
	ProcessFile(rootfolder, template, outdir, "index.tte", rootmenu)

def ProcessFile(pathfile, template, outpath, filename, menu):
	outfile = MakeOutputName(filename)
	sections = ReadSections(os.path.join(pathfile, filename))
	sections = MakeMenu(sections, menu)
	output = ReplaceSections(template, sections)
	print output
	WriteFile(outpath, outfile, output)
	#sections = 


def ProcessRootFolder(rootfolder):
	directory = []
	if os.path.isdir(rootfolder) == True:
		template = ReadFile(os.path.join(rootfolder, TEMPLATE))
		directory = os.listdir(rootfolder)
		MakeRootIndex(rootfolder, template, directory, OUTDIR)
		WriteFile(OUTDIR, CSS, ReadFile(os.path.join(rootfolder, CSS)))
		#pff = os.walk(folder)
		#for (path, folders, files) in os.walk(folder):
		#	if path == folder:
		#		menu.append(folders)
			#print "subFolders : ", folders
			#print "path : ", path
			#print "files : ", files
		#print pff
	else:
		print rootfolder, " is not a folder"

def main():
    	if len(sys.argv) == 1:
        	print "usage: SuceTTE <folder>"
    	else:    
		print "Processing ", sys.argv[1], "..."
		ProcessRootFolder(sys.argv[1])

if __name__ == '__main__':
    	main()
