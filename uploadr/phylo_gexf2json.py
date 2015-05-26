
import pygraphviz as pgv
import networkx as nx

class PhyloGen:
    def __init__(self):
        self.hola = "mundo"

    def process(self , inputfile):
		G = nx.read_gexf(inputfile)
		the_limit = 2998 # i want to consider the phylograph until this year

		# [ Nodes ID dictionary: String <-> Number ]
		IDs_int2str = {}
		IDs_str2int = {}
		for n in G.nodes_iter(data=True):
		    category = n[1]["category"]
		    if category=="Document":
		        ID = n[0]
		        rawdata = ID.split("::")[1].split("_")
		        year = int(rawdata[0].split("-")[1])

		        if year<the_limit:
		            IDs_str2int[ID] = True 
		idx=0
		for k in IDs_str2int:
		    IDs_int2str[str(idx)] = k
		    IDs_str2int[k] = str(idx)
		    idx+=1
		# [ / Nodes ID dictionary: String <-> Number ]

		Year_CL = {}
		for n in G.nodes_iter(data=True):
		    category = n[1]["category"]
		    if category=="Document":
		        ID = n[0]
		        content = ""
		        if "content" in n[1]: content = n[1]["content"]
		        occ = n[1]["occurrences"]
		        weight = n[1]["weight"]
		        label = n[1]["label"]

		        customlabel = ""
		        striplabel = label.split(" ")
		        # print striplabel
		        for w in striplabel:
		            try:
		                customlabel+=w[0].upper()
		            except:
		                pass
		        # print customlabel

		        rawdata = ID.split("::")[1].split("_")
		        alabel = customlabel+" "+rawdata[1]
		        year = int(rawdata[0].split("-")[1])

		        if year<the_limit:
		            if year not in Year_CL: Year_CL[year] = {}
		            # print "wololo:", ID , IDs_str2int[ID]
		            Year_CL[year][IDs_str2int[ID]] = alabel
		            # print [ ID , year , alabel ,category , occ , weight ,  label , content ]

		AG = nx.DiGraph()

		years = Year_CL.keys()
		for y in years:
		    AG.add_node(str(y), label=y , fake=True ,shape="plaintext")

		# import pprint
		for y in Year_CL:
		    for id in Year_CL[y]:
		        label = str(y)+":"+Year_CL[y][id]
		        AG.add_node(id, shape="square" , y=y , label=label, fontsize=7)

		 # adding year-edges
		for i in range(len(years)):
		    try:
		        AG.add_edge(str(years[i]),str(years[i+1]),fake=True)
		    except:
		        break


		# adding inter-cluster edges
		for e in G.edges_iter():
		    s = e[0]
		    t = e[1]
		    # print s,"->",t
		    if G[s][t] [ G[s][t].keys()[-1] ]["type"] == "nodes1":
		        ys = int(s.split("::")[1].split("_")[0].split("-")[1])
		        yt = int(t.split("::")[1].split("_")[0].split("-")[1])
		        if ys<the_limit and yt<the_limit:
		            S = IDs_str2int[s]
		            T = IDs_str2int[t]
		            if ys > yt: AG.add_edge(T,S)
		            else: AG.add_edge(S,T)

		# Identifying heritage conflicts:
		Roots = []
		first_year = years[0]
		for i in AG:
		    if AG.in_degree(i)==0 and "y" in AG.node[i]: # It's a PARENT
		            if AG.node[i]["y"] > first_year:
		                # print AG.in_degree(i) , "\t" ,AG.node[i]["label"]
		                a_root = { "id":i , "y" : AG.node[i]["y"] }
		                Roots.append( a_root )

		# Solving heritage conflict:
		les_ans = years
		for r in Roots:
		    # print r
		    begin = les_ans[0]
		    end = r["y"]
		    for i in range(len(les_ans)):
		        try:
		            ID = r["id"]
		            fakenode1 = ID+"___fake"+str(les_ans[i])
		            fakenode2 = ID+"___fake"+str(les_ans[i+1])
		            if les_ans[i+1] < end:
		                # print "adding fake link:" , fakenode1," -> ",fakenode2
		                Year_CL[les_ans[i]][fakenode1] = "fake"+str(les_ans[i])
		                Year_CL[les_ans[i+1]][fakenode2] = "fake"+str(les_ans[i+1])
		                AG.add_node( fakenode1 , shape="square" , fake=True , y=les_ans[i] , label="fake"+str(les_ans[i]), fontsize=7)
		                AG.add_node( fakenode2 , shape="square" , fake=True , y=les_ans[i+1] , label="fake"+str(les_ans[i+1]), fontsize=7)
		                AG.add_edge( fakenode1 , fakenode2 , fake=True)
		            else:
		                if les_ans[i+1] == end:
		                    # print "adding fake link:" , fakenode1," -> ",ID
		                    Year_CL[les_ans[i]][fakenode1] = "fake"+str(les_ans[i])
		                    AG.add_node( fakenode1 , shape="square" , fake=True , y=les_ans[i] , label="fake"+str(les_ans[i]), fontsize=7)
		                    AG.add_edge( fakenode1 , ID , fake=True )
		                else: 
		                    break
		        except:
		            break


		# Identifying heritage conflicts:
		heritage_conflict = []
		for n in AG.nodes_iter():
		    if "fake" not in AG.node[n]:
		        parents = AG.predecessors(n)
		        if len(parents)>0:
		            # print n
		            # print "\tparents:",parents
		            for i in parents:
		                year_kiddo = AG.node[n]["y"]
		                year_parent = AG.node[i]["y"]
		                if (year_kiddo-year_parent)>1:
		                    # AG.node[i]["color"] = "yellow"
		                    # AG.node[n]["color"] = "yellow"
		                    # AG.node[i]["style"] = "filled"
		                    # AG.node[n]["style"] = "filled"
		                    kiddo = { "id":n , "y":year_kiddo }
		                    parent = { "id":i , "y":year_parent }
		                    heritage_conflict.append( [ parent , kiddo ] )
		                    # print "\t\t",AG.node[i]["y"] ,"vs", AG.node[n]["y"]
		            # print

		# Solving heritage conflict:
		for c in heritage_conflict:
		    begin = c[0]["y"]
		    end = c[1]["y"]
		    les_ans = range(begin+1,end+1)
		    ID = c[1]["id"]
		    # print c


		    fakenode1 = ID+"___fake"+str(begin+1)
		    Year_CL[begin+1][fakenode1] = "fake"+str(begin+1)
		    AG.add_node( fakenode1 , shape="square" , fake=True , y=(begin+1) , label="fake"+str(begin+1), fontsize=7)
		    AG.add_edge( c[0]["id"] , fakenode1 , fake=True)
		    # print "\tadding fake link:" , c[0]["id"]," -> ",fakenode1


		    for i in range(len(les_ans)):
		        try:
		            fakenode1 = ID+"___fake"+str(les_ans[i])
		            fakenode2 = ID+"___fake"+str(les_ans[i+1])

		            if les_ans[i+1] < end:
		                Year_CL[les_ans[i]][fakenode1] = "fake"+str(les_ans[i])
		                Year_CL[les_ans[i+1]][fakenode2] = "fake"+str(les_ans[i+1])
		                AG.add_node( fakenode1 , shape="square" , fake=True , y=les_ans[i] , label="fake"+str(les_ans[i]), fontsize=7)
		                AG.add_node( fakenode2 , shape="square" , fake=True , y=les_ans[i+1] , label="fake"+str(les_ans[i+1]), fontsize=7)
		                AG.add_edge( fakenode1 , fakenode2 , fake=True)
		                # print "\tadding fake link:" , fakenode1," -> ",fakenode2
		            else:
		                if les_ans[i+1] == end:
		                    Year_CL[les_ans[i]][fakenode1] = "fake"+str(les_ans[i])
		                    AG.add_node( fakenode1 , shape="square" , fake=True , y=les_ans[i] , label="fake"+str(les_ans[i]), fontsize=7)
		                    AG.add_edge( fakenode1 , ID , fake=True )
		                    # print "\tadding fake link:" , fakenode1," -> ",ID
		                else: 
		                    break
		        except:
		            break





		A = nx.to_agraph(AG)

		for y in Year_CL:
		    # print
		    # print y
		    # pprint.pprint(Year_CL[y])
		    A.add_subgraph([str(y),Year_CL[y].keys()] , rank='same')



		# Export stuff

		A.layout(prog='dot')

		A.draw(inputfile+'.png', prog='dot')



		NodesDict = []

		for i in A:
		    if "fake" not in AG.node[i]:
		        n=A.get_node(i)
		        coord = n.attr["pos"].split(",")
		        # # print " label =", n.attr["label"]# , " : (" , coord[0] , "," , coord[1] , ")"
		        # if int(n.attr["y"])==years[-1]:
		        #     print n.attr
		        infodict = { "id":i , "label":n.attr["label"] , "shape":"square" , "x":float(coord[0]) , "y":float(coord[1]) }
		        NodesDict.append(infodict)


		EdgesDict = []
		for e in A.edges_iter():
		    s = e[0]
		    t = e[1]
		    if "fake" not in AG[s][t]:
		        infodict = {"s":s , "t":t , "w":1 , "type":"line" }
		        EdgesDict.append(infodict)

		Graph = {  
		   "graph":[],
		   "directed":False,
		   "multigraph":False,
		   "nodes": NodesDict,
		   "links": EdgesDict
		}

		import json
		f = open(inputfile+".json","w")
		f.write(json.dumps(Graph))
		f.close()

		return inputfile+".json"

