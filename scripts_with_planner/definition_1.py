# -*- coding: utf-8 -*-
#definition

#from utils import*
from pyperplan.pddl.parser import Parser
from pyperplan import grounding, planner
from pddl.logic import Predicate, variables, constants
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements
from pddl.logic.base import And, Not, Or
import random 
import os
user_dir = (os.path.dirname(os.path.abspath(__file__)))

def generate_constants_1(num_const, prefix):      # generates PDDL constants
    const_list = []
    for i in range(num_const):
        const_list.append(constants(prefix + str(i)))
    return const_list


def define_predicates_1(robot, l1 ,l2, e):    #definition of the used predicates
    robot_pred = Predicate("robot", robot)
    loc_pred = Predicate ("location", l1)
    entrance_pred = Predicate ("entrance", e)
    at_pred = Predicate("at", robot, l1)
    connected_pred = Predicate("connected", l1, l2)
    return robot_pred, loc_pred, at_pred, connected_pred, entrance_pred

def define_actions_1(r, l1, l2, robot_pred, loc_pred, at_pred, connected_pred, entrance_pred): 
    ## to make the robot move, passes from x to y
    move_action = Action(   
        "move",
        parameters=[r,l1,l2],
        precondition= robot_pred(r) & Or(loc_pred(l1), entrance_pred(l1)) & Or(loc_pred(l2), entrance_pred(l2)) & (at_pred(r,l1) & connected_pred(l1,l2)),
        effect=(at_pred(r, l2) & ~at_pred(r,l1)) #& visited_pred(l1)
    )
    return [move_action]


def define_domain_1(requirements, predicates, actions):           #definition of the PDDL domain
    return Domain("museum_guide", requirements=requirements, predicates=predicates, actions=actions)


def define_initial_state_1(locations, robot, connections, entrances, robot_pred, loc_pred, at_pred, connected_pred, entrance_pred, at_rob):     ##definition of the initial state --> initial conditions
    entrance = 0
    # Define robot, locations and entrances
    initial_state = [robot_pred(robot)]
    initial_state.extend([loc_pred(locations[loc][0]) for loc in range(len(locations))]) #initialize locations
    initial_state.extend([entrance_pred(entrances[entr][0]) for entr in range(len(entrances))]) #initialize entrances
     # Define first position for the robot in an entrance 
    initial_state.extend([at_pred(robot, locations[at_rob][0])])
    # Connect locations assuming bidirectional connections between rooms
    initial_state.extend([connected_pred(constants(loc1)[0], constants(loc2)[0]) for loc1,loc2 in connections])
    initial_state.extend([connected_pred(constants(loc2)[0], constants(loc1)[0] )for loc1, loc2 in connections])  
    # Connect entrances to locations bidirectionally
    initial_state.extend([connected_pred(entrances[0][0], locations[0][0])]) 
    initial_state.extend([connected_pred(locations[0][0], entrances[0][0])])
    initial_state.extend([connected_pred(entrances[1][0], locations[14][0])]) 
    initial_state.extend([connected_pred(locations[14][0], entrances[1][0])])  
    initial_state.extend([connected_pred(entrances[2][0], locations[8][0])]) 
    initial_state.extend([connected_pred(locations[8][0], entrances[2][0])])    
    return initial_state

# Definition of the goal state
def define_goal_state_1(robot, at_pred, entrances):
    at = [at_pred(robot, e[0]) for e in entrances]
    goal_state = Or(*at)
    return goal_state

# Writes the pddl files - Domain and Problem
def write_domain_and_problem_to_files_1(domain, prob_string):
    domain_path = os.path.join(user_dir, "museum_domain_1.pddl")
    problem_path = os.path.join(user_dir, "museum_problem_1.pddl")
    with open(domain_path, "w") as domain_file:
        domain_file.write(domain_to_string(domain))
    with open(problem_path, "w") as problem_file:
        problem_file.write(prob_string)

# Generates pddl files
def generate_pddl_files_1(locations, connections, entrances, at_rob):
    # Define the requirements and variables
    requirements = [Requirements.STRIPS]
    l1,l2,r,e = variables("l1 l2 r e")
    # Define predicates
    robot_pred, l_pred, at_pred, connected_pred, entrance_pred  = define_predicates_1(r, l1, l2, e)
    # Define actions
    actions = define_actions_1(r, l1, l2, robot_pred, l_pred, at_pred, connected_pred, entrance_pred)
    # Define the domain
    domain = define_domain_1(requirements, [robot_pred, l_pred, at_pred, connected_pred, entrance_pred], actions)
    # Define robot as PDDL constants
    robot_constant = constants("pepper")
    # Define initial state
    initial_state = define_initial_state_1(locations, robot_constant[0], connections, entrances, robot_pred, l_pred, at_pred, connected_pred, entrance_pred, at_rob)
    # Define goal state
    goal_state = define_goal_state_1(robot_constant[0], at_pred, entrances)
    # Define the problem
    objects = set(sum(locations,[]))
    objects.add(robot_constant[0])
    for i in range(len(entrances)):
        objects.add(entrances[i][0])
    problem = Problem(
        "museum_problem",
        domain=domain,
        objects=objects,
        requirements=None,
        init=initial_state,
        goal=goal_state
    )
    # Convert the problem to a string format
    prob_string = problem_to_string(problem).replace("(:requirements :strips)", '')
    # Write the domain and problem to files
    write_domain_and_problem_to_files_1(domain, prob_string)
