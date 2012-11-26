#!/usr/bin/python

# This script is used to convert .yaml files to patterns and package groups.
# Copyright (C) 2011 Marko Saukko <FIRSTNAME.LASTNAME@gmail.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# This script is based on MeeGo package-group scripts
# https://meego.gitorious.org/meego-os-base/package-groups/

import yaml
import sys, os
import optparse
from lxml import etree

rpm_ns="http://linux.duke.edu/metadata/rpm"
pattern_ns="http://novell.com/package/metadata/suse/pattern"
NSMAP = {None : pattern_ns, "rpm": rpm_ns}

NSMAP_GROUP = {None : pattern_ns, "rpm": rpm_ns, "patterns": pattern_ns}

def process_yaml(stream, version, release, proot, newobsapi):
	"Process all documents in the yaml stream and return a count of number handled"
	all_docs = yaml.load_all(stream)
	count = 0
	for y in all_docs:
		count = count + 1
		# <name>
		etree.SubElement(proot, "name").text = y['Name']

		# Old OBS isn't able to handle these options.
		if newobsapi:
			# <version>
			if y.has_key('Version') or version:
				entry = etree.SubElement(proot, "version")
				ver = "0"
				if version:
					ver = version
				else:
					ver = y['Version']

				# Set to 0 by default as that is what OBS expects.
				epoch = "0"
				if y.has_key('Epoch'):
					epoch = y['Epoch']

				# As above...
				rel = "0"
				if release:
					rel = release
				if y.has_key('Release'):
					rel =  y['Release']

				entry.set('ver', "%s" % ver)
				entry.set('epoch', "%s" % epoch)
				entry.set('rel', "%s" % rel)

			# <arch>
			if y.has_key('Arch'):
				etree.SubElement(proot, "arch").text = "%s" % y['Arch']

		# <summary>
		etree.SubElement(proot, "summary").text = y['Summary']
		# <description>
		etree.SubElement(proot, "description").text = y['Description']
		# <uservisible>
		etree.SubElement(proot, "uservisible")
		# <category>
		cat = etree.SubElement(proot, "category")
		cat.text = "Base Group"
		cat.set("lang", "en")

		package_keys = ['Packages','Conflicts', 'Requires', 'Recommends', 'Suggests', 'Provides']
		for key in package_keys:
			if not y.has_key(key):
				continue

			collect = y[key]
			if key == "Packages":
				# Support obsoleted keys, this should be removed in the future
				key = "Requires"
				print "WARNING: Oboleted key 'Packages' in .yaml please change to 'Requires'."
			
			req = etree.SubElement(proot, "{%s}%s" % (rpm_ns,key.lower()))

			for p in collect:
				if type(p).__name__=='dict':
					print "ERROR: Found dict and expected string value. '%s'" % (p)
					sys.exit(1)
				entry = etree.SubElement(req, "{%s}entry" %rpm_ns)
				entry.set("name", p)

	return count

def create_patterns(patterns_dir, version, release, outputdir, newobsapi):
	for f in os.listdir(patterns_dir):
		if not f.endswith('.yaml'):
			continue
		
		output_file = "%s/%s.xml" % (outputdir,os.path.basename(f).split('.')[0])
		
		print "Working on %s" % (output_file)
		
		stream = file("%s/%s" %(patterns_dir,f), 'r')
		proot = etree.Element("pattern",  nsmap=NSMAP)
		process_yaml(stream, version, release, proot, newobsapi)

		# Indent the XML as we output to file.
		etree.ElementTree(proot).write(output_file, pretty_print=True)

def merge_patterns(patterns_dir, version, release, outputdir, newobsapi):
	xmlroot = etree.Element("patterns")
	output_file = "%s/group.xml" % (outputdir)
	count = 0
	for f in os.listdir(patterns_dir):
		if not f.endswith('.yaml'):
			continue
		print "Merging %s to %s." % (f,output_file)
		stream = file("%s/%s" %(patterns_dir,f), 'r')
		proot = etree.SubElement(xmlroot, "pattern",  nsmap=NSMAP_GROUP)
		count = count + process_yaml(stream, version, release, proot, newobsapi)

	xmlroot.set('count', "%d" %count)
	# Indent the XML as we output to file.
	etree.ElementTree(xmlroot).write(output_file, pretty_print=True)

if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option("", "--patternxml", action="store_true", dest="patternxml",
			default=False,
			help="Create separated pattern XML file for each pattern.")
	parser.add_option("", "--groupxml", action="store_true", dest="groupxml",
			default=False,
			help="Create merged group.xml from all the available patterns.")
	parser.add_option("-p", "--patterndir", type="string", dest="patterndir",
			default=None,
			help="Directory where the pattern .yaml files are located.")
	parser.add_option("-o", "--outputdir", type="string", dest="outputdir",
			default=".",
			help="Output directory where the resulting .xml files are created.")
	parser.add_option("", "--old-obs-xml-format", action="store_false", dest="newobsapi",
			default=True,
			help="The old OBS api isn't able to handle the newer xml format.")
	parser.add_option("--version", type="string", dest="version", default=None, help="Version number")
	parser.add_option("--release", type="string", dest="release", default=None, help="Release number")
	
	(options, args) = parser.parse_args()
	
	if (not options.groupxml and not options.patternxml):
		print "Error: you need to use either --patternxml or --groupxml."
		exit(1)
	
	if (not options.patterndir or not os.path.exists(options.patterndir)):
		print "Error: Pattern dir '%s' doesn't exist." % (options.patterndir)
		exit(1)
	
	if options.outputdir and not os.path.exists(options.outputdir):
		os.makedirs(options.outputdir)
	
	if options.patternxml:
		create_patterns(options.patterndir, options.version, options.release, options.outputdir, options.newobsapi)

	if options.groupxml:
		merge_patterns(options.patterndir, options.version, options.release, options.outputdir, options.newobsapi)
