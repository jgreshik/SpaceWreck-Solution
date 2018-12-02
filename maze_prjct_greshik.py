# MadMaze Spacewreck Maze Problem
# Author: Joseph Greshik 
# 
#	This script reads in a formatted maze blueprint and 
# 	builds a graph containing the information in the 
#	blueprint. The graph is condensed to a state where
#	a bfs traversal can determine whether the maze
# 	has a solution. If a solution is found, the script
# 	outputs to standard output the step-by-step solution
#	The initial and condensed graphs are visualized
#
#   Maze blueprint is structured as follows:
#       line 1 contains two integers, n and m
#       Line 2 contains n-1 chars where the ith char represents the color of 
#           the ith vertex. The vertex with index n is the exit and has no color
#       Line 3 contains two integers s1 and s2, representing the index of the 
#           starting vertices of Captain Rocket and Lieutenant Lucky, respectively
#       each of the next m lines contains two integers a and b and one char c,
#           in that order, representing a corridor with color c from a to b
#           note that a, b are within 1 to n
#       

import networkx as nx
import matplotlib.pyplot as plt
from collections import namedtuple
import string

######## CODE FOR SOLUTION ########

# State tuple is how nodes are stored in RUG. 
# State contains locations of Rocket (R) and
# Lucky (L) as integers corresponding to nodes
# of original graph
# Need for:
#	creating RUG nodes
#	declaring source in bfs of RUG
#	checking items in bfs tree
State=namedtuple("State","R L")

#### makeGraph:
####	takes file of defined structure and returns directed graph & final location
####    we will output locations as A=1, B=2,...Z=26,AA=27
####    but for ease of indexing we will use A=0, B=1,... in the graph nodes 
def makeGraph(file_name):
	G=nx.DiGraph()
	file=open(file_name)
	n,m=file.readline().replace("\n", "").replace("\r", "").split(" ")
	q=file.readline().replace("\n", "").replace("\r", "").split(" ")
	solnLoc=len(q)
	for i in range(len(q)): G.add_node(i,color=q[i])
	# adding FINAL node, with color WHITE
	G.add_node(len(q),color='W')
	# setting starting vertices
	R,L=file.readline().replace("\n", "").replace("\r", "").split(" ")
	R=int(R)-1
	L=int(L)-1
	# making graph edges
	for i in range(int(m)):
		line=file.readline().replace("\n", "").replace("\r", "").split(" ")
		G.add_edge(int(line[0])-1,int(line[1])-1,color=str(line[2]))
	return G,solnLoc

#### refurbish:
#### 	convert old_graph into DAG consisting of directed state nodes
####    states represent Rocket and Lucky's location on the game board
####    states are represented as State named tuple where 
####    astronaut locations are denoted as  0=A, 1=B, ..., 26=AA, 27=end
####    Possible states (succeeding current state) are added iff Rocket 
####    or Lucky can move to the state depending on each other's current state
def refurbish(old_graph,solLoc,loc_Rocket,loc_Lucky):
    G=nx.DiGraph()
    check_points=[[-1 for i in range(solLoc+1)] for j in range(solLoc+1)]
    
    def check(state,next_node,isL):
        if isL:
            if old_graph.edges()[(state[0],next_node)]['color']==old_graph.nodes()[state[1]]['color']:
                next_state=State(next_node,state[1])
                G.add_node(next_state)
                if check_points[next_state[0]][next_state[1]]==-1: G.add_edge(state,next_state)
                refurb(next_state)
        else:
            if old_graph.edges()[(state[1],next_node)]['color']==old_graph.nodes()[state[0]]['color']:
                next_state=State(state[0],next_node)
                G.add_node(next_state)
                if check_points[next_state[0]][next_state[1]]==-1: G.add_edge(state,next_state)
                refurb(next_state)
            
    
    def refurb(state):
        if check_points[state[0]][state[1]]!=-1: return
        check_points[state[0]][state[1]]=state
        for next_left in list(old_graph.adj.items())[state[0]][1]: check(state,next_left,True)  
        for next_right in list(old_graph.adj.items())[state[1]][1]: check(state,next_right,False)
    
    starting_state=State(loc_Rocket,loc_Lucky)
    refurb(starting_state)
    
    return G

#### print_node_alpha:
#### 	returns alpha string of node for ease of reading when 
####   outputting final path
def print_node_alpha(num,s):
	out=""
	if num==s+1: return 'end'
	for i in range(int((num-1)/26)+1):
	    out=out+list(string.ascii_uppercase)[(num-1)%26]
	    num=num-26
	return out

#### get_diff:
#### 	return who moved in bfs parent-child relationship
def get_diff(state_list,s):
    if state_list[0][0]==state_list[1][0]: return('L '+str(state_list[0][1]+1)+' # Lucky moves to '+print_node_alpha(state_list[0][1]+1,s))
    else: return('R '+str(state_list[0][0]+1)+' # Rocket moves to '+print_node_alpha(state_list[0][0]+1,s))

#### traverse_bfs_tree:
####	traverse tree made by reduced_graph bfs according to networkx bfs predecessor fn
def traverse_bfs_tree(tree,solnLoc):
    finished=False
    out=[]
    for i in range(len(tree)):
        if finished==False and tree[-i-1][0][0] or tree[-i-1][0][1]==solnLoc: 
            finished=True
            out.append(get_diff(tree[-i-1],solnLoc))
            index=i
        if finished==True and tree[-i-1][0]==tree[-index-1][1]:
            index=i
            out.append(get_diff(tree[-i-1],solnLoc))
    if finished:
        for i in range(len(out)):
            print(out[-i-1])
    else:
        print('No solution')
        
######## VISUALIZATION CODE ########

#### drawVanillaGraph: 
####	draw full graph with colored, numbered nodes and colored, directed edges
def drawVanillaGraph(graph, pos):
    # all colors, white for end node
    colors=('B','R','Y','G','W')	
    plt.style.use(['dark_background'])
    # size of plot
    plt.figure(figsize=(8,8),dpi=100)
    # set up position of graph items
    
        
    # draw nodes
    colored_nodes={}
    for color in colors:
        colored_nodes[color]=[]
    for node in graph.nodes():
        colored_nodes[graph.nodes[node]['color']].append(node)
    for col in colored_nodes:
        nx.draw_networkx_nodes(graph, pos,
                               nodelist=colored_nodes[col],
                               node_color=col, node_size=250, alpha=0.9)

    # draw edges
    colored_edges={}
    for color in colors:
        colored_edges[color]=[]
    for edge in graph.edges:
        colored_edges[graph.edges[edge]['color']].append(edge)
    for col in colored_edges:
        nx.draw_networkx_edges(graph, pos,
                               edgelist=colored_edges[col],
                               width=3, alpha=0.9, edge_color=col)
    # draw network labels
    labels={}
    for node in graph.nodes():
        # label according to PDF problem statement node labeling standard
        labels[node]=node+1  
    # the FINAL NODE is WHITE and labeled as END
    labels[len(graph.nodes())-1]='end'
    nx.draw_networkx_labels(graph, pos, labels, font_size=8, font_weight='bold')
    
    plt.axis('off')
    plt.show()

#### drawRefurbishedGraph:
####	draw refurbished graph of character states
def drawRefurbishedGraph(graph, pos):
    # size of plot
    plt.figure(figsize=(10,10),dpi=100)
    # set up position of graph items
        
    # draw nodes
    for node in graph.nodes():
        nx.draw_networkx_nodes(graph, pos,
                               nodelist=list(graph.nodes()),
                               node_size=250, node_color='R', alpha=0.9)

    # draw edges
    for edge in graph.edges:
        nx.draw_networkx_edges(graph, pos,
                               edgelist=list(graph.edges()),
                               width=3, alpha=0.9, edge_color='grey')
    # draw network labels
    labels={}
    for node in graph.nodes():
        # label according to PDF problem statement node labeling standard
        labels[node]=str(node[0]+1)+", "+str(node[1]+1)
    nx.draw_networkx_labels(graph, pos, labels, font_size=5)
    
    plt.axis('off')
    plt.show()


######## MAIN FUNCTION ########
        
#### main:
####	this is where all script happenings happen
def main():
    # create graph from problem statement input
    # keeping track of where the solution location should be in the graph
    (original_graph,solution_location)=makeGraph("input.txt") 
    #draw our graph 'corr'
    drawVanillaGraph(original_graph,pos=nx.kamada_kawai_layout(original_graph))
    # refurbish graph to better fit our needs
    # our needs are to find if a path exists to 'end' from the starting location
    # making new graph R(efurbished) U(ltimate) G(raph)
    RUG=refurbish(original_graph,solution_location,0,1)
    drawRefurbishedGraph(RUG,pos=nx.fruchterman_reingold_layout(RUG))
    # now print a bfs traversal of the refurbished graph
    # bfs predecessors and parents stored in y 
    # Rocket starts at 0 (A) and Lucky starts at 1 (B)
    y=list(nx.bfs_predecessors(RUG,State(R=0,L=1))) 
    # now traverse bfs tree and output solution (or lack thereof)
    traverse_bfs_tree(y,solution_location)

main()
