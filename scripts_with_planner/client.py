import sys,os
user_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(user_dir)
from utils import*
from main import*
from motion import*

### Client class
class ClientPepper:
    def __init__(self, io_loop):
        # WebSocket connection object
        self.connection = None
        # Tornado I/O loop
        self.io_loop = io_loop
        # Client name
        self.name = "/Pepper"
        # Name of the current painting
        self.painting_name = None                                                       # da verificare, penso sia inutile
        # Save pepperRobot class
        self.pepperRobot = None
        # List of actions received by the planner
        self.actions = []
        # Flag for the starting of the tour
        self.start_tour = False
        # Number of participants selected form tablet
        self.participants = 0
        # Type of the tour selected from tablet
        self.tour_mode = ""
        # Paintings to visit selected from tablet
        self.paintings = ""
        # Flag to start the planning
        self.start_plan = False
        # Flag to pass to the next action in the planner's sequence of actions
        self.next = False
        # Flag to pass to the second planner to exit the museum
        self.end = False
        # Number of stars received
        self.stars = 0
      # Flags for Persistence of Memory details
        self.pm1 = False
        self.pm2 = False
        self.pm3 = False
        self.pm4 = False
        self.pm5 = False
      # Flags for Mona Lisa details
        self.ml1 = False
        self.ml2 = False
        self.ml3 = False
        self.ml4 = False
        self.ml5 = False
      # Flags for Supper at Emmaus details
        self.se1 = False
        self.se2 = False
        self.se3 = False
        self.se4 = False
        self.se5 = False
      # Flags for Starry Night details
        self.sn1 = False
        self.sn2 = False
        self.sn3 = False
        self.sn4 = False
        self.sn5 = False
      # Flags for Birth of Venus details
        self.bv1 = False
        self.bv2 = False
        self.bv3 = False
        self.bv4 = False
        self.bv5 = False
      # Flags for Last Judgement details
        self.lj1 = False
        self.lj2 = False
        self.lj3 = False
        self.lj4 = False
        self.lj5 = False
      # Flags for The Scream details
        self.ts1 = False
        self.ts2 = False
        self.ts3 = False
        self.ts4 = False
        self.ts5 = False
      # Flags for Birth of Venus details
        self.ki = False
        self.ki2 = False
        self.ki3 = False
        self.ki4 = False
        self.ki5 = False

    # Initialize client
    def start(self):
        self.connect_and_read()

    # Stops client
    def stop(self):
        print("StoppingI/O loop...")
        self.io_loop.add_callback(self.io_loop.stop)

    # Initialize condition
    def connect_and_read(self):
        print("\nCLIENT THREAD: Connecting to " + websocket_address + " ...")
        tornado.websocket.websocket_connect(
            url=websocket_address + self.name,
            callback=self.maybe_retry_connection,
            on_message_callback=self.on_message,
            ping_interval=10,
            ping_timeout=50,
        )

    # Retries if connection is unsuccessful
    def maybe_retry_connection(self, future):
        try:
            self.connection = future.result()
            self.send_message_from_client("Hello from Pepper Client!")
        except:
            print("\nCLIENT THREAD: Could not reconnect, retrying in 3 seconds...")
            self.io_loop.call_later(3, self.connect_and_read)

    
    # Retrieve the robot class
    def get_robot(self, robotClass):
        self.pepperRobot = robotClass
    
    def send_actions(self, actions):
        self.pepperRobot.planned_actions = actions      

    # Incoming messages 
    def on_message(self, message):

        # Handles case where the message is empty.
        if message is None:
            print("\nCLIENT THREAD: Message is empty")
            self.connect_and_read()

        else:
            print("\nCLIENT THREAD: Received from Server: " +  message)

            # Sets the flag true when the tour starts
            if message.startswith("Start Tour"):
                self.start_tour = True

             # Extracts the actions from the message and it saves them in a list
            if message.startswith("The actions to execute are:"):     
                list_start = message.index("[")
                list_end = message.index("]") + 1
                actions_str = message[list_start:list_end]
                # Converts the string representation of the list to an actual list
                actions_str = ast.literal_eval(actions_str)
                actions = str(actions_str)
                self.actions = actions

            # Receives the number of participants
            if message.startswith("Participants:"):
                message = str(message)
                number_str = message.split(":")[1]
                # Convert the extracted part to an integer
                self.participants = int(number_str)
            
            # Sets to true the flag when the works are selected
            if message.startswith("Selected works:"):
                self.start_plan = True
            
            # Message sent by the tablet when the user clicks on the next button on the tablet --> it passes to the successive action
            if message == "Next":                          
               self.next = True
              
            # Message sent by the tablet when the user wants to end the tour before having visited all the works
            if message == "Exit":                          
               self.next = True
               self.end = True

            # Changes flags on Persistence of memory details
            if message == "pm1":                          
               self.pm1 = True
            elif message == "pm2":                          
               self.pm2 = True
            elif message == "pm3":                          
               self.pm3 = True
            elif message == "pm4":                          
               self.pm4 = True
            elif message == "pm5":                          
               self.pm5 = True

            # Changes flags on Mona Lisa details
            if message == "ml1":                          
               self.ml1 = True
            elif message == "ml2":                          
               self.ml2 = True
            elif message == "ml3":                          
               self.ml3 = True
            elif message == "ml4":                          
               self.ml4 = True
            elif message == "ml5":                          
               self.ml5 = True
            
            # Changes flags on Supper at Emmaus details
            if message == "se1":                          
               self.se1 = True
            elif message == "se2":                          
               self.se2 = True
            elif message == "se3":                          
               self.se3 = True
            elif message == "se4":                          
               self.se4 = True
            elif message == "se5":                          
               self.se5 = True

            # Changes flags on Starry Night details
            if message == "sn1":                          
               self.sn1 = True
            elif message == "sn2":                          
               self.sn2 = True
            elif message == "sn3":                          
               self.sn3 = True
            elif message == "sn4":                          
               self.sn4 = True
            elif message == "sn5":                          
               self.sn5 = True
            
            # Changes flags on Birth of Venus details
            if message == "bv1":                          
               self.bv1 = True
            elif message == "bv2":                          
               self.bv2 = True
            elif message == "bv3":                          
               self.bv3 = True
            elif message == "bv4":                          
               self.bv4 = True
            elif message == "bv5":                          
               self.bv5 = True

             # Changes flags on Last Judgement details
            if message == "lj1":                          
               self.lj1 = True
            elif message == "lj2":                          
               self.lj2 = True
            elif message == "lj3":                          
               self.lj3 = True
            elif message == "lj4":                          
               self.lj4 = True
            elif message == "lj5":                          
               self.lj5 = True

            # Changes flags on The Scream details
            if message == "ts1":                          
               self.ts1 = True
            elif message == "ts2":                          
               self.ts2 = True
            elif message == "ts3":                          
               self.ts3 = True
            elif message == "ts4":                          
               self.ts4 = True
            elif message == "ts5":                          
               self.ts5 = True

            # Changes flags on Birth of Venus details
            if message == "ki1":                          
               self.bv1 = True
            elif message == "ki2":                          
               self.bv2 = True
            elif message == "ki3":                          
               self.bv3 = True
            elif message == "ki4":                          
               self.bv4 = True
            elif message == "ki5":                          
               self.bv5 = True


            # Message with the number of stars the user chose to give
            if message.startswith("Stars:"):
                message = str(message)
                number_str = message.split(":")[1]
                # Convert the extracted part to an integer
                self.stars = int(number_str)




    # Sends message from cleint to server
    def send_message_from_client(self, message):
        if self.connection:
            self.connection.write_message(message)
            print("\nCLIENT THREAD: Sent to the Server: " + message)
        else:
            print("Could not send message")

    # Sends the user's answer to the server.
    # Parameters:
    # - answer: User's input (yes or no) to be sent to the server.
    def send_answer_to_server(self, answer):
        message = "Answer is: {}".format(answer.lower())
        self.send_message_from_client(message)

def start_client(event):
        global pepperClient
        io_loop = tornado.ioloop.IOLoop.current()
        pepperClient = ClientPepper(io_loop=io_loop)
        io_loop.add_callback(pepperClient.start)
        # After the initialization set the timer
        event.set()
        io_loop.start()

############################# CONNECT TO SERVER IN ANOTHER THREAD #############################################################
def connect_to_server():
        event = threading.Event()
        ws_thread = threading.Thread(target=start_client, args=(event,))
        ws_thread.daemon = True
        ws_thread.setName("ClientThread")
        ws_thread.start()
        # Wait for the client to start correctly before continuing in the main thread
        event.wait()
        return pepperClient
