##################################################################
# A* Search on 15 Puzzle - Manhattan Distance Heuristic Function
# 
# Description: This Python program does a A* Search on a 15-piece sliding puzzle
#              to solve. The program then returns stats regarding the search.
#
# Course: CS 411, Spring 2024
# Author: Joshua Hontanosas
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
#   state - Current board state (Board data type)
#   parent - Parent Node (Node data type)
#   action - Direction to move empty tile (String data type)
#   depth  - # of edges from the root node
class Node:
    def __init__(self, state, parent, action, gscore, fscore):
        self.state = state      
        self.parent = parent    
        self.action = action
        self.gscore = gscore
        self.fscore = fscore

    # __repr__() - Returns string representation of the state
    def __repr__(self):
        return str(self.state.tiles)

    # __eq__() - Comparing current node with other node. They are equal if states are equal
    def __eq__(self, other):
        if(type(self) != type(other)):
            return False
        return self.state.tiles == other.state.tiles

    # __hash__() - Returns the Node's current state tiles as a hash value
    def __hash__(self):
        return hash(tuple(map(tuple, self.state.tiles)))
    
    # parentExists() - Returns true if parent exists (not None)
    def parentExists(self):
        return self.parent != None
    
    # is_Cycle() - Returns true if a cycle exists
    def is_Cycle(self):
        cur_node = self
        while cur_node:  # Keep backtracking till either None or the self node if found
            cur_node = cur_node.parent
            if(cur_node == self):   # Cycle is found
                return True
        return False    # No cycle was found

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
            childrenList.append(Node(parent_node.state.execute_action(action), parent_node, action, (parent_node.gscore + 1), 0))
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
    
    # find_position() - Returns row and column of tile location.
    def find_position(self, tile):
        final_tiles = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]]
        i, j = 0, 0
        while i < 4:
            while j < 4:
                if(tile == final_tiles[i][j]):
                    return i, j
                j += 1
            i += 1
        return -1, -1
    
    # misplaced_tiles() - Returns number of tiles that don't match the expected layout.
    def misplaced_tiles(self, node):
        final_tiles = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]]
        i, j, tileCounter = 0, 0, 0
        while i < 4:
            while j < 4:
                if(node.state.tiles[i][j] != final_tiles[i][j]):
                    tileCounter += 1
                j += 1
            i += 1
        return tileCounter
    
    # total_manhattan_distance - Returns culmulative distance each tile is from expected location.
    def total_manhattan_distance(self, node):
        totalDistance = 0
        i, j = 0, 0
        while i < 4:
            while j < 4:
                currentTile = node.state.tiles[i][j]
                if currentTile != 0:
                    row, column = self.find_position(currentTile)
                    totalDistance += abs(row - i) + abs(column - j)
                j += 1
            i += 1
        return totalDistance
    
    # run_a_star() - Runs A* search for the puzzle solution. Uses the passed heuristic function.
    def run_a_star(self, root_node, heuristic_function):
        solvedPuzzle = 0
        solutionNode = None
        # Declare and intialize return variables
        path = []               # list of char
        expanded_nodes = 0      # int
        time_taken = ''         # str + "ms"
        memory_consumed = ''    # str + "kb"

        startTime = time.time()                 # Used to calculate time_taken
        process = psutil.Process(os.getpid())   # Used to calculate memory_consumed
        
        # -- Start of A* Search --
        frontier = [root_node]  # Will use deque as a FIFO queue.
        cameFrom = None # cameFrom is the node preceding the current node.
        root_node.gscore = 0
        root_node.fscore = heuristic_function(root_node)
        returnValue = 'Failure'
        while len(frontier) != 0:
            # Sort frontier, then remove lowest value
            frontier.sort(key=lambda node: node.fscore, reverse=False)
            currentNode = frontier.pop(0)
            # Check if current node is solution.
            if self.goal_test(currentNode.state.tiles):
                returnValue = currentNode
                break
            # Expand current node and calculate gscore and fscore for children.
            currentChildren = self.get_children(currentNode)    
            expanded_nodes += 1
            for child in currentChildren:
                # Children of current node will always have a depth one more than current node. No need to calculate edge weight.
                tentative_gScore = currentNode.gscore + 1
                # Update child values
                child.parent = currentNode
                child.gscore = tentative_gScore
                child.fscore = tentative_gScore + heuristic_function(child)
                # Add child if not already in frontier.
                if child not in frontier:
                    frontier.append(child)
        # -- End of A* Search --
                    
        if(returnValue == 'Failure'):
            print("Could not solve puzzle.")
            exit()
        solutionNode = returnValue
        
        # Evaluate return variables
        time_taken = "{} ms".format(str((time.time() - startTime)*60))
        memory_consumed = "{} bytes".format(str((process.memory_info().rss)))
        path = self.find_path(solutionNode)

        # Return the values
        return path, expanded_nodes, time_taken, memory_consumed

    # solve() - Solve the given input
    def solve(self, input):
        initial_list = [int(s) for s in input.split() if s.isdigit()]
        root = Node(Board(initial_list), None, None, 0, 0)
        path, expanded_nodes, time_taken, memory_consumed = self.run_a_star(root, self.total_manhattan_distance)
        print("Moves: " + " ".join(path))
        print("Number of expanded Nodes: " + str(expanded_nodes))
        print("Time Taken: " + str(time_taken))
        print("Max Memory (Bytes): " + str(memory_consumed))
        return "".join(path)

# Testing the algorithm locally
if __name__ == '__main__':
    agent = Search()
    agent.solve("1 0 2 4 5 7 3 8 9 6 11 12 13 10 14 15")