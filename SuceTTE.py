import os
import sys
import posixpath

TEMPLATE="page.html"
OUTDIR="out"
CSS="style.css"
SITETITLE="Bordel"

custom_tags = []

def MakeLink(dest, content):
	return '<a href="%s"/>%s</a>' % (dest, content)

class File(object):
	def __init__(self, inpath, outpath, name):
		self.inpath = inpath
		self.outpath = outpath
		self.name = name
		self.menu = ""
	
	def Read(self):
		with open(os.join.path(self.inpath, self.name), "r") as f:
			return f.read()
	
	def ReadLines(self):
		with open(os.join.path(self.inpath, self.name), "r") as f:
			return list(f)

	def Write(self, content):
		if not os.path.exists(self.outpath):
			os.mkdir(self.outpath)
		with open(os.join.path(self.outpath, self.name), "w") as f:
			f.write(content)

	def MakeOutputName(self, filename):
		if filename.endswith(".tte"):
			basename = filename[:-4]
		else:
			basename = filename
		return basename + ".html"

	def MakeMenu(self, folders, files):
		for entry in folders:
			self.menu += '<div class="menu">' + MakeLink("/" + entry.outpath, entry.name) + '</div>\n'
			SubMenu = ""
			if files != None:
				for fi in files:
					if entry.name in fi.outpath and fi.name != "index.tte":
						SubMenu += '<div class="sousmenu">' + MakeLink(self.MakeOutputName(fi.name), fi.name[:-4]) + '</div>\n'
			if len(SubMenu) > 0:
				self.menu += '<div id="sousmenu1" style="display:block">\n'
				self.menu += SubMenu
				self.menu += '</div>\n'

	def ProcessFile(self, template):
		outfile = self.MakeOutputName(self.name)
		sections = ReadSections(posixpath.join(self.inpath, self.name))
		sections["menu"] = self.menu
		output = ReplaceSections(template, sections)
		WriteFile(posixpath.join(OUTDIR, self.outpath), outfile, output)

class Folder:
	def __init__(self, inpath, outpath, name):
		self.inpath = inpath
	    	self.outpath = outpath
	    	self.name = name
	    	self.files = []

	    	for entry in os.listdir(self.inpath):
			if os.path.isdir(posixpath.join(self.inpath, entry)):
				continue
			elif not entry.endswith('.tte'):
                    		continue
			self.files.append(File(self.inpath,
						self.outpath,
						entry))

	## DBG Stuff
	def PrintFolder(self):
		print "Folder : ", self.name
		print "\tInpath :", self.inpath
		print "\tOutpath :", self.outpath
		self.PrintFile()
	## DBG Stuff
	def PrintFile(self):
		for entry in self.files:
			print "File : ", entry.name
			print "\tMenu : ", entry.menu

class RootFolder(Folder):
	def __init__(self, inpath, outpath, name):
		Folder.__init__(self, inpath, outpath, name)
		self.folders = []
		for entry in os.listdir(self.inpath):
			if os.path.isdir(posixpath.join(self.inpath, entry)):
				self.folders.append(Folder(posixpath.join(self.inpath, entry),
				    			posixpath.join(self.outpath, entry),
							entry))

	def PrintRoot(self):
		self.PrintFolder()
		for f in self.folders:
			f.PrintFolder()

	def Generate(self):
		template = ReadFile(posixpath.join(self.inpath, TEMPLATE))		
		for f in self.files:
			f.MakeMenu(self.folders, None)
			f.ProcessFile(template)
		for f in self.folders:
			for fi in f.files:
				fi.MakeMenu(self.folders, f.files)
				fi.ProcessFile(template)


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
    with open(posixpath.join(path, filename), "w") as f:
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

def ReplaceSections(template, sections):
	for section in sections:
		tag = "{{" + section + "}}"
		template = template.replace(tag, "".join(sections[section]))
	return template


def main():
    	if len(sys.argv) == 1:
        	print "usage: SuceTTE <folder>"
    	else:    
		print "Processing ", sys.argv[1], "..."
		rootfolder = RootFolder(sys.argv[1], "", sys.argv[1])
		rootfolder.Generate()
		rootfolder.PrintRoot()

if __name__ == '__main__':
    	main()
