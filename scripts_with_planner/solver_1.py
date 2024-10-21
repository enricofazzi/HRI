### pip3 install unified-planning[fast-downward], pyperplan, pddl
from definition_1 import *
import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.engines import PlanGenerationResultStatus
import os
import re
# Disable the credits stream to avoid unnecessary output
# up.shortcuts.get_env().credits_stream = None
class Planning_1():
    def __init__(self, algorithm_name="fast-downward", heuristic_name=""): #other option: astar-hadd
        self.domain_file = user_dir + "/museum_domain_1.pddl"
        self.problem_file = user_dir + "/museum_problem_1.pddl"
        self.algorithm_name = algorithm_name
        self.heuristic_name = heuristic_name

    # Generate the new PDDL files and execute the new PDDL, from the generated plan return the actions that make it
    def solve_1(self, locations, connections, entrances, at_rob): 
        actions = []
        generate_pddl_files_1(locations, connections, entrances, at_rob)
        plan = self.generate_plan_1()
        if self.check_empty_plan(plan):
            return None
        print("The plan is: %s  with length: %d" % (plan, len(plan)))
        actions = self.extract_actions(plan)
        return actions

    # Generate the plan with fast-downward
    def generate_plan_1(self): 
        reader = PDDLReader()
        plan = []
        pddl_problem = reader.parse_problem(self.domain_file, self.problem_file)
        with OneshotPlanner(name='fast-downward',optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
            result = planner.solve(pddl_problem, timeout=30)
        if result.plan is not None:
            for action in result.plan.actions:
                plan.append(str(action))
        return plan
    # Check if the plan is empty or not
    def check_empty_plan(self, plan):
        if len(plan) == 0:
            return True
        else:
            return False
    
    # Extract the actions from the plan
    def extract_actions(self, plan):
        actions = []
        for action in plan:
            action_str = str(action).split('\n')[0]
            actions.append(action_str)
        return actions

    def main_plan_1(self, at_rob):
    # Example usage
        locations = generate_constants_1(20, 'l')  # Adjust the number based on the museum layout.. how many crossable places?
        entrances = generate_constants_1(3, 'e')  # Adjust based on the number of entrances and exits
        connections = [
        ('l0', 'l1'), ('l0', 'l19'), ('l1', 'l0'), ('l1', 'l2'), ('l1', 'l18'), ('l2', 'l1'), ('l2', 'l3'), ('l2', 'l9'), ('l2', 'l17'), ('l3', 'l2'), 
        ('l3', 'l4'), ('l4','l5'), ('l4', 'l3'), ('l5', 'l4'), ('l7','l8'), ('l8', 'l7'), ('l8', 'l9'), ('l9','l2'), ('l9','l8'), ('l9', 'l10'), 
        ('l10', 'l17'), ('l10', 'l9'), ('l12', 'l5'), ('l14', 'l15'), ('l15', 'l16'), ('l15', 'l12'), ('l15', 'l14'), ('l16','l17'), ('l16','l15'), ('l17', 'l18'), 
        ('l17','l2'), ('l17','l10'), ('l17', 'l16'), ('l18','l19'),  ('l18','l1'), ('l18', 'l17'), ('l19','l0'), ('l19','l18')]# room connections
        planner = Planning_1()
        #goal_list = [1,2]
        actions = planner.solve_1(locations, connections, entrances, at_rob)
        return actions
                      
    def start_plan(self, at_rob):
    #inp = input("Please select which paintings you want to see insering a number from 0 to 2, separating them by spaces:\n")
    #p_list = inp.split()
        plan = Planning_1()
        actions = plan.main_plan_1(at_rob)
        if actions:
            print("Planned actions:")
            for action in actions:
                print(action)
            return actions
        else:
            print("No plan found.")
