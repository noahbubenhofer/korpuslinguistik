import argparse
import re
import json
import unicodedata

def parse_arguments():
	parser = argparse.ArgumentParser(description='converts dereko cooccurrence profile exports to json or csv')
	parser.add_argument('-f','--file',help='file to process')
	parser.add_argument('-r','--root',help='root word (if no root word ist provided, it will not be displayed)')
	parser.add_argument('-o','--out',help='out file')
	parser.add_argument('-m','--min',help='min llr')
	parser.add_argument('-t','--type',help='type of format: [index] instead of [raw] text for node id')
	parser.add_argument('-a','--format',help='format: [json] or [csv]')
	
	
	args = parser.parse_args()

	return args



def main():
	args = parse_arguments()
	
	datafile = open(args.file, encoding='utf-8', mode = "r")
	columnindex = 0
	parseddata = { "nodes": [], "links": [] }
	nodes = []
	nodesValues = {}
	actualllr = ""
	
	
	for line in datafile:
		line = line.replace(u"\xa0", u" ")
		fields = line.split(";")
		if "Kookkurrenzen" in fields:
			print("Header gefunden: ", fields)
			continue
		
		words = fields[7].split(" ")
		
		if words[0] not in nodes:
			nodes.append(words[0])
			nodesValues[words[0]] = fields[2]
		if args.root and args.root not in nodes:
			nodes.append(args.root)
			nodesValues[args.root] = fields[2]
		
		if fields[2] != "":
			actualllr = fields[2]
			
			if args.root:
				if args.type == "index":
					parseddata["links"].append({ "source": nodes.index(args.root), "target": nodes.index(words[0]), "value": fields[2]})
				else:
					parseddata["links"].append({ "source": args.root, "target": words[0], "value": fields[2]})
		
		lastword = ""
		
		for word in words:
			if word not in nodes:
				nodes.append(word)
				nodesValues[word] = actualllr
			if lastword != "":
				if args.type == "index":
					parseddata["links"].append({ "source": nodes.index(lastword), "target": nodes.index(word), "value": actualllr})
				else:
					parseddata["links"].append({ "source": lastword, "target": word, "value": actualllr})
			lastword = word
		
		if int(actualllr) < int(args.min):
			break
			
	for node in nodes:
		if args.type == "index":
			parseddata["nodes"].append({ "id": nodes.index(node), "name": node, "group": 0, "value": nodesValues[node] })
		else:
			parseddata["nodes"].append({ "id": node, "group": 0, "value": nodesValues[node] })
	parseddata["directed"] = "false"
	parseddata["multigraph"] = "false"
	parseddata["graph"] = {}
	#print(nodes)
	
	if args.format == "json":
		outfile = open(args.out, "w")
		outfile.write(json.dumps(parseddata))
	else:
		outfilelinks = open(args.out+".links.tsv", "w")
		outfilelinks.write("source\ttarget\tweight\n")
		for link in parseddata["links"]:
			outfilelinks.write(str(link["source"]) + "\t" + str(link["target"]) + "\t" + str(link["value"]) + "\n")
		
		outfilenodes = open(args.out+".nodes.tsv", "w")
		if args.type == "index":
			outfilenodes.write("id\tname\tgroup\tvalue\n")
			for node in parseddata["nodes"]:
				outfilenodes.write(str(nodes.index(node["name"])) + "\t" + str(node["name"]) + "\t" + str(node["group"]) + "\t" + str(node["value"]) + "\n")
		else:
			outfilenodes.write("id\tgroup\tvalue\n")
			for node in parseddata["nodes"]:
				outfilenodes.write(str(node["id"]) + "\t" + str(node["group"]) + "\t" + str(node["value"]) + "\n")
	
		
	
if __name__ == '__main__':
	main()