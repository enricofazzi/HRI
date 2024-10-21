import os, sys
sys.path.append(os.getenv('PEPPER_TOOLS_HOME') + '/cmd_server')
user_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(user_dir)
from pepper_cmd import *
from utils import *
from motion import *

############################################ ROBOT CLASS  #########################################################
class RobotPepper:
    def __init__(self, client, session, tts_service):
        self.flag = None
        self.thread = None
        self.task = None
        self.session= session
        self.tts_service = tts_service
        self.client = client
        self.planned_actions = ""

    
    # Greets the visitor
    def greeting(self):
        sentence = sentences(0)
        move_talk(robot = self.session, text = sentence, char = "greeting", service = self.tts_service)

    # Useless for now  
    def choose_length(self):
        if not self.client.stop_questions:
            time_question = sentences(3)
            move_talk(robot = self.session, text = time_question, char = " ", service = self.tts_service)
            t = input_with_timeout("Enter the time that you can spend in the museum (1 for three hours, 2 for one hour, 3 for half an hour or less): ", timeout)
            if not t:
                return None
        else:
            return None
        t = int(t)
        
        if t == 1:
            length = tourLength(0)
        elif t == 2:
            length = tourLength(1)
        elif t == 3:
            length = tourLength(2)
        else:
            length = tourLength(0)
            
        return length
    
    # Useless for now
    def choose_tour(self, length):
        if length == "all":
            sentence = sentences(4)
            move_talk(robot = self.session, text = sentence, char = " ", service = self.tts_service)
        elif length == "medium":
            sentence = sentences(5)
            move_talk(robot = self.session, text = sentence, char = "greeting", service = self.tts_service)
        elif length == "short":
            sentence = sentences(6)
            move_talk(robot = self.session, text = sentence, char = "greeting", service = self.tts_service)

        beware_sentence = bewareSentences(0)
        move_talk(robot = self.session, text = beware_sentence, char = " ", service = self.tts_service)
            
        kind_sentence = kindSentences(0)
        move_talk(robot = self.session, text = kind_sentence, char = " ", service = self.tts_service)

    # Moves  
    def intro_moves(self):
        sentence = sentences(2)
        move_talk(robot = self.session, text = sentence, char = "talk", service = self.tts_service)

    def queue_in_visit(self, p, l):
        sentence = "There is too much queue in"+  p + " , we will not visit this paint. Let's move to " + l
        move_talk(robot = self.session, text = sentence, char = " ", service = self.tts_service)
        
    def speech_move(self, l1, l2, prev):
        sentence = "Let's move from " + l1 + " to " + l2
        move_talk(robot = self.session, text = sentence, char = " ", service = self.tts_service)
        time.sleep(1)
        motion_rooms(robot= self.session, l1 = l1, l2 = l2, prev = prev)
        
    def no_take_pictures(self):
        sentence = bewareSentences(1)
        move_talk(robot = self.session, text = sentence, char = "no", service = self.tts_service)

    def taking_pictures(self, p):
        sentence = "You are taking a picture of" + p + " with flash! It is strictly forbidden!"
        move_talk(robot = self.session, text = sentence, char = "no", service = self.tts_service)

    def visit_work(self, p):
        sentence = "We have arrived at"+ p + ", let's visit it!"
        move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
        sentence = painting_info[p]
        move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
        sentence = "If you would like to have more details on the paint please consult my tablet"
        move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
        show (robot = self.session)   

    def too_close(self, p):
        sentence = "Someone is too close to " + p + ", please move away!"
        move_talk(robot = self.session, text = sentence, char = "no", service = self.tts_service)
        time.sleep(1)
    
    def check_details(self, pepperClient):

        # Persistance of Memory
        if pepperClient.pm1:
            sentence = pm_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.pm1 = False

        elif pepperClient.pm2:
            sentence = pm_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.pm2 = False
        
        elif pepperClient.pm3:
            sentence = pm_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.pm3 = False

        elif pepperClient.pm4:
            sentence = pm_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.pm4 = False

        elif pepperClient.pm5:
            sentence = pm_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.pm5 = False

        # Mona Lisa
        elif pepperClient.ml1:
            sentence = ml_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ml1 = False

        elif pepperClient.ml2:
            sentence = ml_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ml2 = False
        
        elif pepperClient.ml3:
            sentence = ml_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ml3 = False

        elif pepperClient.ml4:
            sentence = ml_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ml4 = False

        elif pepperClient.ml5:
            sentence = ml_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ml5 = False

        # Birth of Venus
        elif pepperClient.bv1:
            sentence = bv_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.bv1 = False

        elif pepperClient.bv2:
            sentence = bv_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.bv2 = False
        
        elif pepperClient.bv3:
            sentence = bv_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.bv3 = False

        elif pepperClient.bv4:
            sentence = bv_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.bv4 = False

        elif pepperClient.bv5:
            sentence = bv_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.bv5 = False
        
         # Starry Night
        elif pepperClient.sn1:
            sentence = sn_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.sn1 = False

        elif pepperClient.sn2:
            sentence = sn_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.sn2 = False
        
        elif pepperClient.sn3:
            sentence = sn_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.sn3 = False

        elif pepperClient.sn4:
            sentence = sn_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.sn4 = False

        elif pepperClient.sn5:
            sentence = sn_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.sn5 = False

        # Supper at Emmaus
        elif pepperClient.se1:
            sentence = se_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.se1 = False

        elif pepperClient.se2:
            sentence = se_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.se2 = False
        
        elif pepperClient.se3:
            sentence = se_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.se3 = False

        elif pepperClient.se4:
            sentence = se_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.se4 = False

        elif pepperClient.se5:
            sentence = se_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.se5 = False

        # Last Judgement
        elif pepperClient.lj1:
            sentence = lj_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.lj1 = False

        elif pepperClient.lj2:
            sentence = lj_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.lj2 = False
        
        elif pepperClient.lj3:
            sentence = lj_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.lj3 = False

        elif pepperClient.lj4:
            sentence = lj_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.lj4 = False

        elif pepperClient.lj5:
            sentence = lj_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.lj5 = False
         
        # The Scream
        elif pepperClient.ts1:
            sentence = ts_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ts1 = False

        elif pepperClient.ts2:
            sentence = ts_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ts2 = False
        
        elif pepperClient.ts3:
            sentence = ts_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ts3 = False

        elif pepperClient.ts4:
            sentence = ts_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ts4 = False

        elif pepperClient.ts5:
            sentence = ts_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ts5 = False
        
        # The Kiss
        elif pepperClient.ki1:
            sentence = ki_sentences(0)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ki1 = False

        elif pepperClient.se2:
            sentence = ki_sentences(1)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ki2 = False
        
        elif pepperClient.ki3:
            sentence = ki_sentences(2)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ki3 = False

        elif pepperClient.ki4:
            sentence = ki_sentences(3)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ki4 = False

        elif pepperClient.ki5:
            sentence = ki_sentences(4)
            move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service)
            time.sleep(1)
            pepperClient.ki5 = False

        else:
            return





    
    def star_ask(self):
        sentence = "We have arrived to the end of our tour. Thanks for choosing us! Please leave us an evaluation based on your experience with us!"
        show(robot = self.session)
        move_talk(robot = self.session, text = sentence, char = "new_talk", service = self.tts_service) 

    def final_moves(self,stars):
        if stars < 3:
            sentence = sadSentences(0)
            move_talk(robot = self.session, text = sentence, char = "talk", service = self.tts_service)
            goodbye(robot = self.session)
        if stars == 3:
            sentence = kindSentences(1)
            move_talk(robot = self.session, text = sentence, char = "talk", service = self.tts_service) 
            goodbye(robot = self.session)
        if stars > 3:
            sentence = kindSentences(2)
            move_talk(robot = self.session, text = sentence, char = "talk", service = self.tts_service)
            goodbye(robot = self.session)


    # Starts general activity run
    def start_activity(self,task):
        print("\nROBOT THREAD: Pepper starts " + task)
        self.flag = True
        self.task = task
        self.thread = threading.Thread(target=self._activity, args=(task,))
        self.thread.setName("RobotThread")
        if task == "waiting":
            self.thread.daemon = True
        self.thread.start()
        
    # Stops general activity run
    def stop_activity(self):
        self.flag = False
        self.thread = None
        if self.task == "waiting":
            print("\nROBOT THREAD: Human Approached")
        elif self.task == "running":
            print("\nROBOT THREAD: Pepper stopped")
            
    # Runs cotinuosly general activites until flag
    def _activity(self, task):
        while self.flag:
            print("\nROBOT THREAD: Pepper is " + task)
            time.sleep(8)
