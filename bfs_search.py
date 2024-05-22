##################################################################
# Breadth First Search on 15 Puzzle
# 
# Description: This Python program does a BFS on a 15-piece sliding puzzle
#              to solve. The program then returns stats regarding the search.
#
# Course: CS 411, Spring 2024
# Author: Joshua Hontanosas
# * Used starter code by Sarit Adhikari
# * Referenced this site to calculate memory consumed: https://stackoverflow.com/questions/938733/total-memory-used-by-python-process
##################################################################

import random
import math
import time
import psutil
import os
from collections import deque
import sys

# class Board - This class defines the state of the problem in terms of board configuration
# Class Variables:
#   tiles - 2D list representing the layout of the board
class Board:
    # Default Constructor
    def __init__(self, tiles):
        # Convert tiles 1D list to a 2D list
        boardGrid = [tiles[i:i+4] for i in range(0, len(tiles), 4)]
        self.tiles = boardGrid

    # get_empty_position() - Gets x,y coordinates of the empty tile (0)
    def get_empty_position(self):
        yPos = 0
        while 0 not in self.tiles[yPos]: # Get y position of 0
            yPos += 1
        xPos = self.tiles[yPos].index(0) # Get x position of 0
        return yPos, xPos

    # execute_action() - This function returns the resulting state from taking particular action from current state
    # Actions to take: U - Up, D - Down, L - Left, R - Right
    def execute_action(self, action):
        boardGrid = [l.copy() for l in self.tiles]  # Make a copy of the tiles
        yPos, xPos = self.get_empty_position()      # Get x,y coordinates of the empty tile
        # Swap the empty tile with the one specified by action
        if action == "U":   #Up
            boardGrid[yPos][xPos], boardGrid[yPos-1][xPos] = boardGrid[yPos-1][xPos], boardGrid[yPos][xPos]
        elif action == "D": #Down
            boardGrid[yPos][xPos], boardGrid[yPos+1][xPos] = boardGrid[yPos+1][xPos], boardGrid[yPos][xPos]
        elif action == "L": # Left
            boardGrid[yPos][xPos], boardGrid[yPos][xPos-1] = boardGrid[yPos][xPos-1], boardGrid[yPos][xPos]
        elif action == "R": # Right
            boardGrid[yPos][xPos], boardGrid[yPos][xPos+1] = boardGrid[yPos][xPos+1], boardGrid[yPos][xPos]
        else:               # Error
            exit()
        # Flatten list (for creating a new Board object)
        flattenList = []
        for row in boardGrid:
            flattenList.extend(row)
        return Board(flattenList)   # Return resulting state

# class Node - This class defines the node on the search tree, consisting of state, parent and previous action.
# Class Variables:
#   state - # Current board state (Board data type)
#   parent - Parent Node (Node data type)
#   action - Direction to move empty tile (String data type)
class Node:
    def __init__(self, state, parent, action):
        self.state = state      
        self.parent = parent    
        self.action = action

    # __repr__() - Returns string representation of the state
    def __repr__(self):
        return str(self.state.tiles)

    # __eq__() - Comparing current node with other node. They are equal if states are equal
    def __eq__(self, other):
        return self.state.tiles == other.state.tiles

    # __hash__() - Returns the Node's current state tiles as a hash value
    def __hash__(self):
        return hash(tuple(map(tuple, self.state.tiles)))
    
    # parentExists() - Returns true if parent exists (not None)
    def parentExists(self):
        return self.parent != None

# class Search - Contains functions related to BFS search
class Search:

    # get_children() - This function returns the list of children obtained after simulating the actions on current node
    def get_children(self, parent_node):
        childrenList = []               # Will store 4 Node objects
        actionList = ["U","D","L","R"]  # Up, Down, Left, Right
        # Remove actions that go beyond board
        yPos, xPos = parent_node.state.get_empty_position()  
        if(yPos == 0): actionList.remove("U")
        if(yPos == 3): actionList.remove("D")
        if(xPos == 0): actionList.remove("L")
        if(xPos == 3): actionList.remove("R")

        for action in actionList:       # Create a new node for each direction
            childrenList.append(Node(parent_node.state.execute_action(action), parent_node, action))
        return childrenList

    # find_path() - This function backtracks from current node to reach initial configuration. The list of actions would constitute a solution path
    def find_path(self, node):
        currentPath = []
        cur_node = node
        while cur_node:  # Backtrack and record moves
            if(cur_node.action != None): currentPath.append(cur_node.action)
            cur_node = cur_node.parent
        currentPath.reverse()
        print("Path: ", currentPath)
        return currentPath

    # goal_test() - Check if current tiles matches the expected board
    def goal_test(self, cur_tiles):
        final_tiles = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]]
        return cur_tiles == final_tiles
    
    # run_bfs() - This function runs breadth first search from the given root node and returns path, number of nodes expanded and total time taken
    def run_bfs(self, root_node):
        solvedPuzzle = -1
        solutionNode = None
        # Declare and intialize return variables
        path = []               # list of char
        expanded_nodes = 0      # int
        time_taken = ''         # str + "ms"
        memory_consumed = ''    # str + "kb"

        startTime = time.time()                 # Used to calculate time_taken
        process = psutil.Process(os.getpid())   # Used to calculate memory_consumed

        # -- Start of Breadth-First-Search --
        # 1. Check on root node, the initial node, if it is the goal (the solved puzzle)
        if(self.goal_test(root_node.state.tiles)): solvedPuzzle = 1
        # 2. Declare and initialize frontier and reached.
        frontier = deque([root_node])  # Doubly ended queue for the frontier. Add 
        reached = set({root_node})     # Hashset for explored nodes
        # 3. Loop while frontier is full or puzzle hasn't been solved yet.
        while len(frontier) != 0 and solvedPuzzle == -1:
            currentNode = frontier.popleft()                        # 3.1. Pop the front of the frontier
            currentChildren = self.get_children(currentNode)    # 3.2. Get children of currentNode
            expanded_nodes += 1
            for child in currentChildren:                       # 3.3. Evaluate each child
                s = child.state.tiles
                if self.goal_test(s):       # 3.4. If child is the goal, accept as the solution and end BFS.
                    solutionNode = child
                    solvedPuzzle = 1
                    break
                if child not in reached:    # 3.5. Add child if it is not in reached set (not explored already)
                    #expanded_nodes += 1
                    reached.add(child)          # Add child to reached nodes
                    frontier.append(child)  # Add child to frontier
        # 4. If the goal was not reached, return error
        if(solvedPuzzle == -1): 
            print("Could not solve puzzle.")
            exit()
        # -- End of Breadth-First-Search --

        # Evaluate return variables
        time_taken = "{} ms".format(str((time.time() - startTime)*60))
        memory_consumed = "{} bytes".format(str((process.memory_info().rss)))
        path = self.find_path(solutionNode)

        # Return the values
        return path, expanded_nodes, time_taken, memory_consumed
            
    # solve() - Solve the given input
    def solve(self, input):
        initial_list = [int(s) for s in input.split() if s.isdigit()]
        root = Node(Board(initial_list), None, None)
        path, expanded_nodes, time_taken, memory_consumed = self.run_bfs(root)
        print("Moves: " + " ".join(path))
        print("Number of expanded Nodes: " + str(expanded_nodes))
        print("Time Taken: " + str(time_taken))
        print("Max Memory (Bytes): " + str(memory_consumed))
        return "".join(path)

# Testing the algorithm locally
if __name__ == '__main__':
    agent = Search()
    #agent.solve("1 2 3 4 5 6 7 8 9 10 11 0 13 14 15 12")
    agent.solve("1 0 2 4 5 7 3 8 9 6 11 12 13 10 14 15")