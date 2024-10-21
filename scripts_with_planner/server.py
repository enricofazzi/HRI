import os, sys
import threading
from tornado.ioloop import IOLoop
user_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(user_dir)
from utils import *
from solver import *
from solver_1 import *
# Handles the main HTTP requests from Websocket Server
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("WebSocket Server is running.")

########################################## WEBSOCKET SERVER ################################################################
class Server(tornado.websocket.WebSocketHandler):
    # Connected clients
    clients = []
    # Flag to start the plan
    start_plan = False

    # Thread for the planner
    def thread_plan(self, planner, paintings):
        while not self.start_plan:
            pass
        loop = IOLoop()
        loop.make_current()        
        actions = planner.start_plan(paintings)
        new_message = "The actions to execute are: %s" % (actions)
        # Sends message to the client Pepper
        Server.forward_message(self, new_message)
    
    # Thread for the planner1
    def thread_plan1(self, planner, room):
        loop = IOLoop()
        loop.make_current()        
        actions = planner.start_plan(room)
        new_message = "The actions to execute are: %s" % (actions)
        # Sends message to the client Pepper
        Server.send_message(self, new_message)

    # When connection is opened with a client
    def open(self):
        # Extract client name from the URL
        client_name = self.get_client_name_from_uri(self.request.uri)
        print("WebSocket opened for " + client_name)
        client_dict = {'name': client_name, 'info': self}
        Server.clients.append(client_dict)

    # Handles incoming WebSocket messages
    def on_message(self, message):
        client_name = self.get_client_name_from_uri(self.request.uri)
        print("Received message from " + client_name + ": " + message)
        
        # Message sent by the tablet when the user starts the interaction with tablet
        if message == "Start Tour":
            Server.forward_message(self, message)

        # Message sent by the tablet when the user selects the number of participants
        if message.startswith("Participants:"):
            Server.forward_message(self, message)
        
        # Probsbly useless
        if message.startswith("Painting name:"):
            Server.forward_message(self, message)

        # Message sent by the tablet when the user clicks on the next button on the tablet --> it passes to the successive action
        if message == "Next":                          
            Server.forward_message(self, message)

        # Message sent when we want to finish the tour before it is completed
        if message == "Exit":
            Server.forward_message(self,message)
             
        # Message received when the tour is aborted with the current room in which the robot is
        if message.startswith("Tour aborted:"):
            print("In Tour aborted code")
            room = message.split(":l")[1]
            room = int(room)
            print("room = ", room)
            planner = Planning_1()
            print(planner)
            thread = threading.Thread(target=self.thread_plan1,args=(planner, room))
            thread.start()
            thread.join(timeout = 20)

        if message.startswith("Ready to start visit"):
            Server.forward_message(self,message)
            
        # Message sentto the tablet when all the actions from the planner are executed
        if message ==  "Tour finished":
            Server.forward_message(self, message)

        # Messaged received with the satisfaction level of the user
        if message.startswith("Stars:"):
            Server.forward_message(self, message)

       
        # Message sent from Pepper to Tablet to pass the order of the paints
        if message.startswith("The order of the paintings is:"):
            Server.forward_message(self, message)

        # Message sent from Pepper to Tablet to communicate that someone used the flash when not allowed
        if message.startswith("Someone took a photo with flash!"):
            Server.forward_message(self, message)

        # Message received from tablet that includes the works to visit chosen by the user
        if message.startswith("Selected works:"):
            # Forward message to Pepper
            Server.forward_message(self, message)
            # Set start planner flag to True
            self.start_plan = True
            # Extracts the paints from the message
            index_part = message.split(":")[1].strip("[]")
            paintings = [str(elem.strip()) for elem in index_part.split(",")]
            paintings = [p_index(p) for p in paintings]
            print("the goal paints are", paintings)
            # Passes the paintings to the planner in a new thread
            planner = Planning()
            thread = threading.Thread(target=self.thread_plan,args=(planner, paintings))
            thread.start()
            thread.join(timeout = 20)
            print("done")

        # Message sent by tablet when user clicks on a detail to be analyzed - Persistence of Memory
        if message.startswith("pm"):
            Server.forward_message(self, message)
            
        # Message sent by tablet when user clicks on a detail to be analyzed - Supper at Emmaus
        if message.startswith("se"):
            Server.forward_message(self, message) 
            
        # Message sent by tablet when user clicks on a detail to be analyzed - Starry Night
        if message.startswith("sn"):
            Server.forward_message(self, message) 
            
        # Message sent by tablet when user clicks on a detail to be analyzed - Birth of Venus
        if message.startswith("bv"):
            Server.forward_message(self, message) 
            
        # Message sent by tablet when user clicks on a detail to be analyzed - Mona Lisa
        if message.startswith("ml"):
            Server.forward_message(self, message) 

        # Message sent by tablet when user clicks on a detail to be analyzed - Last judgement
        if message.startswith("lj"):
            Server.forward_message(self, message)  

        # Message sent by tablet when user clicks on a detail to be analyzed - The Scream
        if message.startswith("ts"):
            Server.forward_message(self, message)  

        # Message sent by tablet when user clicks on a detail to be analyzed - The Kiss
        if message.startswith("ki"):
            Server.forward_message(self, message)   

    # When connection with a client is closed
    def on_close(self):
        print("WebSocket closed")
        # Remove the closed WebSocket from the clients list
        Server.clients = [client_dict for client_dict in Server.clients if client_dict['info'] != self]
    
    # Forwards the message to all the other connected clients except the sender
    @classmethod
    def forward_message(cls, sender_client, message: str):
        for client_dict in cls.clients:
            other_client = client_dict['info']
            if other_client != sender_client:
                try:
                    other_client.write_message(message)
                    print(f"Forwarding message {message} to client {client_dict['name']}.")
                except tornado.websocket.WebSocketClosedError:
                    print(f"Client {client_dict['name']} not connected. Not forwarding the message.")
    
    # Sends message to specified client
    @classmethod
    def send_message(cls, client, message: str):
        print("In send_message. Client = ", client)
        for client_dict in cls.clients:
            if client_dict['info'] == client:
                try:
                    print(f"Sending message {message} to client {client_dict['name']}.")
                    client.write_message(message)
                    print("SENT")
                except tornado.websocket.WebSocketClosedError:
                    print("Client not connected")
                # No need to continue searching once the client is found
                break
            else:
                print(f"Client {client_dict['name']} not found.")

    @staticmethod
    def get_client_name_from_uri(uri):
        # Extract client name from the URL
        match = re.match(r'/websocket/(\w+)', uri)
        if match:
            return match.group(1)
        return None
########################################################################################################
    
# Create a Tornado web application with WebSocket support
def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket/Tablet', Server),
        (r'/websocket/Pepper', Server)],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
    )

# Run the IO_loop of the WebSocket app
def main():
    app = make_app()
    app.listen(server_port)
    server = tornado.httpserver.HTTPServer(app)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("Keyboard Interrupt ...")
        tornado.ioloop.IOLoop.current().stop()
        server.stop()

if __name__ == "__main__":
    main()
