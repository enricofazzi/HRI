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

def generate_constants(num_const, prefix):      # generates PDDL constants
    const_list = []
    for i in range(num_const):
        const_list.append(constants(prefix + str(i)))
    return const_list


def define_predicates(robot, l1 ,l2, p, e):    #definition of the used predicates
    robot_pred = Predicate("robot", robot)
    loc_pred = Predicate ("location", l1)
    entrance_pred = Predicate ("entrance", e)
    paint_pred = Predicate ("paints", p)
    at_pred = Predicate("at", robot, l1)
    connected_pred = Predicate("connected", l1, l2)
    has_painting_pred = Predicate("has_painting", l1, p)
    visited_pred = Predicate("visited", p)
    queue_pred = Predicate("queue", p)
    return robot_pred, loc_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred

def define_actions(r, l1, l2, p, robot_pred, loc_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred): 
    ## to make the robot move, passes from x to y
    move_action = Action(   
        "move",
        parameters=[r,l1,l2],
        precondition= robot_pred(r) & Or(loc_pred(l1), entrance_pred(l1)) & Or(loc_pred(l2), entrance_pred(l2)) & (at_pred(r,l1) & connected_pred(l1,l2)),
        effect=(at_pred(r, l2) & ~at_pred(r,l1)) #& visited_pred(l1)
    )
     # to make the robot visit the paint 
    visit_action = Action(     
        "visit",
        parameters=[r,l1,p],
        precondition=robot_pred(r) & loc_pred(l1) & paint_pred(p) & Not(visited_pred(p)) &  Not(queue_pred(p)) & (at_pred(r,l1) & (has_painting_pred(l1, p))), #~queue_pred(variables("l")) no negative preconiditons No paints at entrances so l1 is a location for sure
        effect= visited_pred(p)
    )
    # to make the robot skip the too crowded painting and move to a contiguous room
    queue_action = Action(     
        "is_queue",
        parameters=[r,l1,l2, p],
        precondition=robot_pred(r) & loc_pred(l1) & paint_pred(p) & Or(loc_pred(l2), entrance_pred(l2)) & connected_pred(l1,l2) & Not(visited_pred(p)) &  queue_pred(p) & (at_pred(r,l1) & (has_painting_pred(l1, p))), #~queue_pred(variables("l")) no negative preconiditons No paints at entrances so l1 is a location for sure
        effect= (at_pred(r, l2) & ~at_pred(r,l1)) & Not(queue_pred(p)) & visited_pred(p) # se c'è coda, per ora lo consideriamo come visitato il quadro remove the  move part?
    )
    return [move_action, visit_action, queue_action]


def define_domain(requirements, predicates, actions):           #definition of the PDDL domain
    return Domain("museum_guide", requirements=requirements, predicates=predicates, actions=actions)

# simulate chosing the entrance UPDATE THIS
def random_entrance():
    return random.randint(0,2)

# Define queues 
def islow_queue():  # less probab queue
    return random.choices([0, 1], weights=[99.5, 0.5], k=1)[0]
def ismed_queue():  # medium probab queue
    return random.choices([0, 1], weights=[95, 5], k=1)[0]
def ismuch_queue(): # high probab queue
    return random.choices([0, 1], weights=[80, 20], k=1)[0]

# Simulate choosing the paintings
def random_paintings(paintings):
    # Choose a random number of elements to extract
    num_elements = random.randint(1, len(paintings))  # at least 1 element and at most all elements
    paints = random.sample(paintings, num_elements)     # Randomly extract the elements
    return paints

def define_initial_state(locations, robot, connections, paintings, entrances, robot_pred, loc_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred):     ##definition of the initial state --> initial conditions
    paints_pos = [1,2,2,4,5,7,9,9,9,10,12,15,16,18,19] #modify this to put paintings in positions
    #entrance = random_entrance() #choose the entrance, it can be 0 1 or 2
    entrance = 0
    low_queue = [0,4,6,11,12,14]
    medium_queue = [3,5,13,10]
    high_queue = [1,2,7,8,9]
    # Define robot, locations and entrances
    initial_state = [robot_pred(robot)]
    initial_state.extend([loc_pred(locations[loc][0]) for loc in range(len(locations))]) #initialize locations
    initial_state.extend([entrance_pred(entrances[entr][0]) for entr in range(len(entrances))]) #initialize entrances
     # Define first position for the robot in an entrance 
    initial_state.extend([at_pred(robot, entrances[entrance][0])])
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
    # Define paintings
    for i in range(len(paintings)):
        initial_state.extend([paint_pred(paintings[i][0])]) #define the paintings in crescent order ex. p0,p1 etc.
        initial_state.extend([Not(visited_pred(paintings[i][0]))]) #define the not visited paints (all of them at the beginning)
    # Define locations with paintings
    for i, j in enumerate(paints_pos):
        initial_state.extend([has_painting_pred(locations[j][0], paintings[i][0])]) 
        print(has_painting_pred(locations[j][0], paintings[i][0]))
    # Define queues
    # There is queue if there are more than 2 paintings to visit
    if len(paintings) > 2:
        for i in range(len(paintings)):
            if i in low_queue:
                if islow_queue():
                    initial_state.extend([queue_pred(paintings[i][0])]) #define the paintings in crescent order ex. p0,p1 etc.
            if i in medium_queue:
                if ismed_queue():
                    initial_state.extend([queue_pred(paintings[i][0])]) #define the paintings in crescent order ex. p0,p1 etc.
            if i in high_queue:
                if ismuch_queue():
                    initial_state.extend([queue_pred(paintings[i][0])]) #define the paintings in crescent order ex. p0,p1 etc.
    return initial_state

# Definition of the goal state
def define_goal_state(robot, paintings, visited_pred, at_pred, entrances, goal_list):
    visited = [visited_pred(paintings[i][0]) for i in goal_list]
    print(visited)
    at = [at_pred(robot, e[0]) for e in entrances]
    goal_state = And(*visited)  # All paintings must be visited
    if at: 
         goal_state = And(goal_state, Or(*at))    # Robot must be at any entrance
    return goal_state

# Writes the pddl files - Domain and Problem
def write_domain_and_problem_to_files(domain, prob_string):
    domain_path = os.path.join(user_dir, "museum_domain.pddl")
    problem_path = os.path.join(user_dir, "museum_problem.pddl")
    with open(domain_path, "w") as domain_file:
        domain_file.write(domain_to_string(domain))
    with open(problem_path, "w") as problem_file:
        problem_file.write(prob_string)

# Generates pddl files
def generate_pddl_files(locations, connections, paintings, entrances, goal_list):
    # Define the requirements and variables
    requirements = [Requirements.STRIPS]
    l1,l2,r,p,e = variables("l1 l2 r p e")
    # Define predicates
    robot_pred, l_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred  = define_predicates(r, l1, l2, p, e)
    # Define actions
    actions = define_actions(r, l1, l2, p, robot_pred, l_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred)
    # Define the domain
    domain = define_domain(requirements, [robot_pred, l_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred], actions)
    # Define robot as PDDL constants
    robot_constant = constants("pepper")
    # Define initial state
    initial_state = define_initial_state(locations, robot_constant[0], connections, paintings, entrances, robot_pred, l_pred, paint_pred, at_pred, connected_pred, has_painting_pred, visited_pred, entrance_pred, queue_pred)
    # Define goal state
    goal_state = define_goal_state(robot_constant[0], paintings, visited_pred, at_pred, entrances, goal_list)
    # Define the problem
    objects = set(sum(locations,[]))
    objects.add(robot_constant[0])
    for i in range(len(paintings)):
        objects.add(paintings[i][0])
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
    write_domain_and_problem_to_files(domain, prob_string)
