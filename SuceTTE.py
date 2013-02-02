import os
import sys
import posixpath
import markdown

TEMPLATE="page.html"
OUTDIR="rstuff"
CSS="style.css"
SITETITLE="Random Stuff"
FOOTER=""
IMG=['jpg', 'jpeg', 'bmp', 'gif', 'png']

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
		with open(os.path.join(self.inpath, self.name), "rb") as f:
			return f.read()
	
	def ReadLines(self):
		with open(os.path.join(self.inpath, self.name), "rb") as f:
			return list(f)

	def Write(self, outpath, name, content):
		if not os.path.exists(outpath):
			os.mkdir(outpath)
		with open(os.path.join(outpath, name), "wb") as f:
			f.write(content)

	def MakeOutputName(self, filename):
		if filename.endswith(".tte"):
			basename = filename[:-4]
		else:
			basename = filename
		return basename + ".html"

	def MakeMenu(self, folders, files):
		for entry in folders:
			if len(entry.files) == 0:
				continue
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
		sections = self.ReadSections(posixpath.join(self.inpath, self.name))
		sections["menu"] = self.menu
		md = markdown.Markdown()
        	sections["body"] = md.convert(sections["body"])		

		output = self.ReplaceSections(template, sections)
		self.Write(posixpath.join(OUTDIR, self.outpath), self.MakeOutputName(self.name), output)

	def ParseSections(self, lines):
		sections = {}
		section = []

		for tag_name, tag_function in custom_tags:
			sections[tag_name] = tag_function()

		name = "empty"
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

	def ReadSections(self, filename):
		lines = self.ReadLines()
		sections = self.ParseSections(lines)
		return sections

	def ReplaceSections(self, template, sections):
		for section in sections:
			tag = "{{" + section + "}}"
			template = template.replace(tag, "".join(sections[section]))
		return template

class Folder:
	def __init__(self, inpath, outpath, name):
		self.inpath = inpath
	    	self.outpath = outpath
	    	self.name = name
	    	self.files = []

	    	for entry in os.listdir(self.inpath):
			if os.path.isdir(posixpath.join(self.inpath, entry)):
				continue
			if any(entry.endswith(x) for x in IMG):
				f = File(self.inpath, self.outpath, entry)
				f.Write(posixpath.join(OUTDIR, self.outpath), f.name, f.Read())
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
		self.template = File(self.inpath, None, TEMPLATE).Read()
		self.css = File(self.inpath, None, CSS)

	def PrintRoot(self):
		self.PrintFolder()
		for f in self.folders:
			f.PrintFolder()

	def Generate(self):
		if not os.path.exists(OUTDIR):
			os.mkdir(OUTDIR)
		for f in self.files:
			f.MakeMenu(self.folders, None)
			f.ProcessFile(self.template)
		for f in self.folders:
			for fi in f.files:
				fi.MakeMenu(self.folders, f.files)
				fi.ProcessFile(self.template)
		self.css.Write(OUTDIR, CSS, self.css.Read())


def tag(function):
    custom_tags.append((function.__name__, function))
    return function


@tag
def SiteTitle():
	return SITETITLE
@tag
def footer():
	return FOOTER

def main():
    	if len(sys.argv) == 1:
        	print "usage: SuceTTE <folder>"
    	else:    
		print "Processing ", sys.argv[1], "..."
		rootfolder = RootFolder(sys.argv[1], "", sys.argv[1])
		rootfolder.Generate()
		#rootfolder.PrintRoot()

if __name__ == '__main__':
    	main()
