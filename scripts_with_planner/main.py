import os, sys
user_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(user_dir)
sys.path.append(os.getenv('PEPPER_TOOLS_HOME') + '/cmd_server')
print(os.getenv('PEPPER_TOOLS_HOME'))
from utils import*
from motion import*
from robot import *
from client import *
############################################ MAIN #####################################################################
def main():
    global pepperRobot, pepperClient, client_thread
    # Initialize Pepper simulation
    session, tts_service = initialize_robot()
    
    # Connect to server on a new thread
    pepperClient = connect_to_server()

    # Initialize robot class, Runs in robot and main thread and pass it to the client
    pepperRobot = RobotPepper(pepperClient, session, tts_service)
    pepperClient.get_robot(pepperRobot)
    pepperClient.send_message_from_client("Interaction started:")
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default="English", help="language")
    parser.add_argument("--speed", type=int, default=8, help="speed")
    # Starting the interaction
    initial_interaction(pepperClient)
    # Awaits for the user to select the works
    while not pepperClient.start_plan:
        time.sleep(1)
    # Eexecutes the actions received from the planner
    planning_interaction(pepperRobot, pepperClient)
    # ADD CONCLUSION OF THE TOUR
    final_interaction(pepperRobot, pepperClient)

def initial_interaction(pepperClient):
        # Approach simulation, the user has to insert start from terminal to start the whole process
        pepperRobot.start_activity("waiting")
        user_input = raw_input("\nMAIN: Enter start to approach the robot: ")
        # After starting, the user is welcomed and instructed to use the tablet
        if user_input == "start": 
            pepperRobot.stop_activity()
            pepperRobot.greeting()
            pepperRobot.intro_moves()
        ## Initial interactions
        print("First interaction")
        # Waits for the user to use the tablet
        pepperRobot.start_activity("waiting")
        while not pepperClient.start_tour:
            time.sleep(1)
        if pepperClient.start_tour:
            pepperRobot.stop_activity()


def planning_interaction(pepperRobot, pepperClient):
    # Previous room he visited, useful to infer the right direction in which the robot has to turn when passing to a new room
    prev = ""
    # List of paintings to visit
    paints_list = []
    time.sleep(5)
    room = "e0" 
    # Receives actions from planner and converts them in a list of strings
    actions = pepperClient.actions
    print(actions)
    actions = ast.literal_eval(actions)
    # Passes the order in which the paints will be visited to the tablet
    paints_list = get_paints_order(actions)
    pepperClient.send_message_from_client("The order of the paintings is: %s" % paints_list)     
    time.sleep(1)
    # Until the tour ends:
    # Proceeds to execute actions
    for action in actions:
    # If there is queue:
        if action.startswith("is_queue"):
        # Extracts from the message the room and the painting
            l1,p1 = get_room_and_work(action)
        # Obtains the title of the paint
            p1 = painting_map.get(p1)
            pepperRobot.queue_in_visit(p1,l1)

        # If it has to move
        elif action.startswith("move"):
            # Extracts the rooms
            l1,l2 = get_rooms(action)
            room = l2        
            pepperRobot.speech_move(l1,l2,prev)
            # Sets the new previous visited room
            prev = l1

        # If it can visit the paint:
        elif action.startswith("visit"):
            # Extracts the paint and its title
            p1 = get_work(action)
            p1 = painting_map.get(p1)
            # If in p1 it is not allowed to take photos with flash:
            if p1 in no_photo:
                # Visitors are warned
                pepperRobot.no_take_pictures()
                # If someone takes photo with flash when not allowed:
                if (weighted_choice([0, 1],[0.6, 0.4])):
                    # Pepper reproaches the visitor
                    pepperRobot.taking_pictures(p1)
                    pepperClient.send_message_from_client("Someone took a photo with flash!")
            # If someone gets too close to a paint:   
            if is_too_close(pepperClient.participants):
                   # Pepper warns the visitor
                pepperClient.send_message_from_client("Someone is too close to a painting!")
                pepperRobot.too_close(p1) 
            # Sends message to tablet and starts visit
            pepperClient.send_message_from_client("Ready to start visit")
            pepperRobot.visit_work(p1)
            # When user clicks on next on tablet, Pepper can proceed to execute the following action
            while not pepperClient.next:
                time.sleep(1)
                pepperRobot.check_details(pepperClient)
            # The next flag is resetted to false
            pepperClient.next = False
        # If the user ends the tour earlier than expected exit the loop
        if pepperClient.end:
            break
    # If the tour ends without being completed we need to pass to the second planner 
    if pepperClient.end:
        # Communicates to the robot the room from which we have to get to the closest exit
        print("room = ", room)
        print(type(room))
        pepperClient.send_message_from_client("Tour aborted:%s" % room)
        # Proceeds to execute the actions until we reach the closest exit
        time.sleep(10)
        actions = pepperClient.actions
        actions = ast.literal_eval(actions) 
        for action in actions:
             # Extracts the rooms
                l1,l2 = get_rooms(action)      
                pepperRobot.speech_move(l1,l2,prev)
            # Sets the new previous visited room
                prev = l1

# Final interaction, it varies according to the level of stars the user chooses to give
def final_interaction(pepperRobot, pepperClient):
    pepperClient.send_message_from_client("Tour finished")
    pepperRobot.star_ask()
    while pepperClient.stars == 0:
        pass
    pepperRobot.final_moves(pepperClient.stars)

if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            print("Main Thread Keyboard Interrupt ...")
            pepperClient.stop()