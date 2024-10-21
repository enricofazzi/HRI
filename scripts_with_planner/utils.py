# -*- coding: utf-8 -*-
import sys,os
import tornado.ioloop, tornado.websocket, tornado.httpserver
import threading, time
from threading import Timer 
import select
import random, re
import qi
import ast
import argparse
from collections import OrderedDict
painting_name = None
pepperRobot = None
pepperClient = None

############################################# SHARED CONSTANTS #####################################################
# Set the Server IP as the local host (of my PC)
IPAddress = "0.0.0.0" # ACCEPT ALL CONNECTIONS 
server_port = "8888"
websocket_address = "ws://"+IPAddress+":"+ server_port + "/websocket"
print("The server has address: " + websocket_address)

# Pepper robot simulation connection 
session = None
tts_service = None

# Paints with no flash allowed
no_photo = ["Mona Lisa","The Birth of Venus","The Lovers","The Young Ladies of Avignon","The Kiss","The Return of the Prodigal Son"]

############################################ TIMED INPUT FUNCTION #################################################
timeout = 10 # global timeout set to 10 seconds

# Function that returns None if no input is received 
def input_with_timeout(prompt, timeout):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        return None

########################################### UTILITY SHOWS ACTIVE THREADS ##########################################
def print_active_threads():
    print("Active threads:", threading.active_count())
    print("Thread IDs:", threading.enumerate())


########################################### UTILITY DEFINITIONS ##########################################
# Spoken sentences
def sentences(idx):
    sentence = ["Hello, my name is Pepper and I will help you to visit DIAG Museum.",
                "DIAG Museum has a very interesting history that is worth to be know.",
                "Let's start with my tablet!",
                "How much time do you have to visit this museum?",
                "According to your answer you can visit all the works in this museum",
                "According to your answer you can visit the most important works in this museum and some others that are less important, but as wonderful as the others.",
                "According to your answer you can visit only the most important works in this museum",
                "Please select the works you are most interested in",
                "Perfect! Let's start the tour!"]
    return sentence[idx]

# Probably useless
def tourLength(idx):
    length = ['All',
              "Medium",
              "Short"
              ]
    return length[idx]

def bewareSentences(idx):
    beware_sentences = [
        "Please, during the tour don't touch the work, don't take pictures where is not allowed and be quiet during the tour.",
        "In the following painting it is prohibited to take photos with flash as shown by our panel"
    ]
    return beware_sentences[idx]

def kindSentences(idx):
    kind_sentences = ["Enjoy this tour!", 
                      "Thank you for choosing this museum, we will do our best to improve your satisfaction! Come back soon!",
                      "Thank you for choosing this museum, we are delighted to know you enjoyed this tour! We hope to see you soon, have a nice day!"]
    return kind_sentences[idx]

def sadSentences(idx):
    sad_sentences = ["Oh we are sorry you did not enjoy our museum! We guarantee we will work hard everyday to offer you the best experience possible!"]
    return sad_sentences[idx]

# Paintings names and related descriptions
painting_info = OrderedDict([ 
               ("Mona Lisa", "Monna Lisa is a world-famous portrait painted by Leonardo da Vinci in the early 16th century. It depicts a woman with an enigmatic expression, often described as a mysterious smile. The painting is renowned for its exquisite detail, masterful use of sfumato technique, and its captivating, lifelike quality."),
               ("The Birth of Venus", "The Birth of Venus is a celebrated painting by Sandro Botticelli, created in the mid-1480s. It depicts the goddess Venus emerging from the sea on a shell, symbolizing her birth. The scene captures a moment of ethereal beauty, with Venus's flowing hair and delicate pose epitomizing classical ideals of grace and divine beauty. The painting is renowned for its harmonious composition, elegant figures, and intricate detailing."),
               ("Supper at Emmaus","The Supper at Emmaus is a remarkable painting by Caravaggio, completed in 1601. The artwork depicts the biblical scene where the resurrected Jesus reveals his identity to two of his disciples during a meal at Emmaus. The painting is renowned for its dramatic use of light and shadow, known as chiaroscuro, which Caravaggio expertly employs to highlight the astonished expressions and dynamic gestures of the figures. The realistic details, from the food on the table to the disciples' weathered faces, create a powerful sense of immediacy and intimacy."),
               ("The Starry Night", "The Starry Night is a famous painting by Vincent van Gogh, created in 1889. It depicts a swirling night sky over a tranquil village, dominated by a luminous crescent moon and radiant stars. The dynamic, swirling patterns of the sky contrast with the serene village below, where cypress trees rise towards the heavens. Van Gogh's expressive brushstrokes and bold color palette convey a sense of emotion and movement, capturing the artist's unique vision and inner turmoil."),
               ("Bond of Union", "Bond of Union is a captivating artwork by the Dutch artist M.C. Escher, created in 1956. This lithograph features the heads of a man and a woman, intricately intertwined as a series of ribbons that form their faces in a continuous, seamless loop. The ribbons create a sense of three-dimensionality and movement, symbolizing the interconnectedness and complexity of human relationships. Escher's masterful use of perspective and illusion challenges the viewer's perception, making Bond of Union a striking example of his exploration of infinity and the nature of reality. The artwork remains one of Escher's most celebrated pieces, exemplifying his unique blend of art and mathematics."),
               ("The Scream", "The Scream is an iconic painting by Edvard Munch, created in 1893. It depicts a figure standing on a bridge, clutching their face in agony against a swirling, tumultuous sky. The vibrant colors and wavy lines convey intense emotion and existential angst, reflecting the inner turmoil and anxiety of the human condition. This haunting image has become a universal symbol of fear and despair."),
               ("The Persistence of Memory", "The Persistence of Memory is a surrealist masterpiece by Salvador Dalí, painted in 1931. It features melting clocks draped over a barren landscape, suggesting the fluidity and distortion of time. The dreamlike scene includes a distorted face in the center, contributing to the painting's enigmatic and otherworldly atmosphere. Dalí's work challenges perceptions of reality, blending the bizarre with the familiar."),
               ("The Lovers", "The Lovers is a surreal painting by René Magritte, created in 1928. It portrays a couple kissing, but their faces are obscured by cloth, preventing direct contact. The shrouded faces evoke a sense of mystery and intrigue, symbolizing themes of secrecy, unattainable intimacy, and the unknowable nature of human relationships. Magritte's work invites viewers to question what lies beneath the surface."),
               ("The Young Ladies of Avignon", "The Young Ladies of Avignon (Les Demoiselles d'Avignon) is a groundbreaking painting by Pablo Picasso, completed in 1907. It depicts five nude women with abstracted, angular forms, influenced by African art and Iberian sculpture. The bold use of geometric shapes and fragmented space marks a significant departure from traditional representation, heralding the advent of Cubism and modern art."),
               ("The Last Judgement", "The Last Judgement is a monumental fresco by Michelangelo, painted between 1536 and 1541. It illustrates the Second Coming of Christ and the final judgement of souls, with a dynamic composition of resurrected figures rising to heaven or descending to hell. The powerful, expressive figures and dramatic use of space convey the themes of redemption and damnation."),
               ("Water Lily Pond", "Water Lily Pond is a serene painting by Claude Monet, created in 1899 as part of his Water Lilies series. It depicts a tranquil scene of a Japanese-style bridge arching over a pond filled with blooming water lilies. Monet's use of light and color captures the reflections and natural beauty of the scene, exemplifying the Impressionist emphasis on capturing the fleeting effects of light and atmosphere."),
               ("The Kiss", "The Kiss is a renowned painting by Gustav Klimt, completed in 1908. It features a couple locked in an intimate embrace, adorned in elaborate, golden robes adorned with intricate patterns. The rich use of gold leaf and the decorative, mosaic-like approach reflect the influence of Byzantine art. Klimt's work celebrates love, intimacy, and the transcendence of human connection."),
               ("The Card Players", "The Card Players is a series of oil paintings by Paul Cézanne, created in the early 1890s. It depicts Provençal peasants absorbed in a game of cards, with a focus on their stoic expressions and solid, geometric forms. Cézanne's careful composition and brushwork emphasize the stillness and gravity of the scene, highlighting the simplicity and dignity of rural life."),
               ("The Return of the Prodigal Son","The Return of the Prodigal Son is a poignant painting by Rembrandt, completed in the mid-1660s. It portrays the biblical parable of the prodigal son returning home in repentance, greeted by his forgiving father. The use of light and shadow, combined with the tender expressions and gestures of the figures, conveys deep emotional resonance and themes of forgiveness and reconciliation."),
               ("The Absinthe Drinker", "The Absinthe Drinker is a painting by Edgar Degas, created in 1876. It depicts a woman sitting alone at a café table, staring blankly ahead with a glass of absinthe in front of her. The composition and muted colors capture a sense of isolation and melancholy, reflecting the social issues and bohemian lifestyle of Parisian life in the late 19th century. Degas' work offers a glimpse into the effects of absinthe consumption and the urban experience.")
               ])
# Creates a dictionary to map p{number} to artwork names directly from the artworks keys
painting_map = {"p%d" % i: key for i, key in enumerate(painting_info.keys())}

# New function to get the index of the painting by its title
def p_map(painting_info):
    return {title: index for index, title in enumerate(painting_info.keys())}

def p_index(title):
    painting_indices = p_map(painting_info)
    return painting_indices.get(title, None)

# Phrases on the details to be said 

def pm_sentences(idx):
    sentence = ["Soft clocks: Most obvious are clocks that appear to melt or be soft, resting on branches and rocks. These clocks symbolize the relativity of time and its fluidity, as well as representing the distortion of reality.",
                "Rock formations: In the desert landscape in the background, there are rock formations that seem to be suspended or floating, creating a sense of unreality and estrangement. ",
                "Anthropomorphic Forms: Another element are anthropomorphic or semi-anthropomorphic forms, such as the face or figure that seems to arise from tree branches or rocks. These figures add a dreamlike and surreal element to the work. ",
                "Calm ocean or lake: In the lower part of the painting, there is a calm body of water, reflecting the blue sky. This element creates a sense of tranquility and contrasts with the strangeness of the surrounding clocks and shapes. ",
                "Insect or animal shapes: Some of the figures emerging from the clocks can also be interpreted as insect or animal shapes, adding an additional layer of ambiguity and strangeness to the work. "
               ]
    return sentence[idx]

def bv_sentences(idx):
    sentence = ["Venus on the Shell: At the center of the painting is Venus, the goddess of beauty and love, emerging from the waters of the sea on a large shell. She is depicted nude, modestly covering her body with her hands and hair. This pose recalls the classical iconography of the 'demure Venus.'",
                "Zephyrus and Chloris: On the left of the painting, Zephyrus, the western wind god, and the nymph Chloris represent the wind blowing toward the shore, pushing Venus on the shell toward the land. Zephyrus is often depicted with wings and Clori is wrapped in a transparent cloak floating in the air.",
                "Clock of the seasons: To the right of Venus, a female figure waits on the shore to greet her. This figure is identified as one of the Hours, the goddesses of the seasons and the hours of the day. She holds a rich cloak embroidered with floral patterns, ready to cover Venus.",	 
                "Open shell: The shell on which Venus stands is open and clearly visible, with the inside decorated with a spiral pattern. This detail not only symbolizes the birth of the goddess from the sea but also lends a sense of movement and dynamism to the composition.",	 
                "Seascape and landscape background: The background of the painting shows a calm sea with gentle waves and a clear, bright sky. A grove of trees can be seen in the background to the right, giving depth to the scene and balancing the composition."
                ]
    return sentence[idx]

def ml_sentences(idx):
    sentence = ["Left Panorama: The left side of the Mona Lisa's background unveils rolling hills and a stone bridge enveloped in a mysterious haze, adding depth and intrigue to the landscape.",
                "Eyes: Her eyes captivate with an enigmatic gaze that seems to follow the viewer, conveying a sense of depth and introspection, reflecting Leonardo da Vinci's mastery of expression.", 
                "Mouth: The Mona Lisa's mouth carries a subtle, ambiguous smile that fluctuates between tranquility and secrecy, embodying a timeless allure that has fascinated viewers for centuries.", 
                "Right Panorama: On the right, a winding path cuts through rugged terrain and a meandering river, contrasting with the serene backdrop of hills, creating a dynamic balance in the composition.",	 
                "Hands: Her hands are delicately intertwined, resting gracefully, a testament to da Vinci's attention to detail and his ability to portray elegance and poise in his subjects." 
                ]
    return sentence[idx]

def se_sentences(idx):
    sentence = ["Christ: depicted with an androgynous face that recalls the image of the Good Shepherd, a beardless and androgynous-looking young man, symbolizing the promise of eternal life and harmony between opposites. His hands are raised in a gesture of blessing over the bread and wine, representing the moment of revelation to the disciples. This iconographic choice recalls early Christian art and emphasizes the theme of rebirth and hope.", 
                "Light: Caravaggio masterfully uses light to direct the viewer's eye to the highlights of the painting. The refraction of light is particularly evident in the bottle and white wine glass on the table, which reflect and reverberate light, creating a realistic, three-dimensional effect. The predominant colors of red, white and green allude to the three theological virtues: Faith, Hope and Charity.",
                "Fruit Basket: The fruit basket, containing various fruits including a scab-affected apple, hangs dangerously over the edge of the table. Its precarious position emphasizes the three-dimensionality of the painting and draws the viewer into the drama of the scene. The still life on the table is described with great virtuosity, combining realism and symbolism associated with the transience of life and Original Sin. The fruit basket, for example, hangs dangerously from the edge of the table and contains painted fruits with their imperfections, such as the apple affected by scab. This detail not only accentuates three-dimensionality and realism, but also symbolizes the transience of creatures and Original Sin. The Trompe-l'œil technique used by Caravaggio amplifies the idea of movement and the connection between the painting and the viewer.", 
                "Cleophas (left): Cleophas rises from his seat, displaying his bent elbow in a gesture that enhances the dynamism of the scene. His movement helps to bridge the shadowed area with the illuminated parts of the painting, adding to the overall sense of depth and spatial complexity. This action underscores the dramatic intensity and the profound spatial dimension within the composition.",
                "James (right): The disciple, dressed as a pilgrim with a shell on his chest, spreads his arms in a gesture that symbolically evokes the cross, connecting the shadowed area with the illuminated part of the painting. His disproportionately large right hand directs the viewer's gaze towards Christ, emphasizing the focal point. These gestures not only highlight the drama of the scene but also convey a sense of movement and depth. Meanwhile, the innkeeper, positioned at the top left from the observer's perspective, watches the scene with a look of amazement, yet without understanding the event's significance. His presence introduces an element of everyday life and humanity to the scene, contrasting with the divine revelation of which he is an unwitting witness."
                ]
    return sentence[idx]

def sn_sentences(idx):
    sentence = ["Swirling Sky: One of the most distinctive features of the painting is the dynamic, swirling sky. The spirals and swirls across the sky create a sense of movement and energy, contrasting with the more static landscape below.",
                "Moon: The orange light of the crescent moon and the pulsing of the planet Venus add further drama, while dense, circular brushstrokes create an arcane movement of the stars.", 
                "Quiet Village: Beneath the turbulent sky, there is a small village with houses and a church. This village is depicted with more muted colors and a simpler structure, shrouded in darkness and sleep, offering an idea of placid stillness and serenity compared to the turmoil of the sky above. The houses are low, except for the sharp bell tower that rises defiantly against the forces of nature.", 
                "Luminescent Stars: Stars are painted as large dots of intense, almost phosphorescent light that seem to emanate energy as they spin in titanic vortices. These stars shine much more vividly in the night sky than the realistic depiction.", 
                "Dark Cypress: In the left foreground, there is a tall, dark and imposing cypress tree silhouetted against the sky. Its elongated shape and prominent position add depth and contrast to the painting, creating a connection between earth and sky. This tree, almost like a dark flame, adds a dramatic and transcendental dimension to the scene."
                ]
    return sentence[idx]

def lj_sentences(idx):
    sentence = ["Christ the Judge and the Virgin Mary: Christ is at the center of the fresco, with his right arm raised in a gesture of judgment. He is depicted with powerful physicality, surrounded by a luminous halo. Around him are saints and the elect. Mary is portrayed next to Christ, slightly bent in a posture of supplication and prayer. She too is surrounded by a light that distinguishes her from the other blessed.",
                "Saint Peter: Saint Peter holds the keys to Heaven, symbolizing his role as the guardian of the celestial gates. He is one of the saints closest to Christ, depicted with a long beard and curly hair.",             
                "The Blessed: The blessed are depicted ascending towards heaven, aided by angels. They are often shown with serene expressions and elegant poses, their arms raised in a welcoming gesture. The figures are luminous, surrounded by a halo of light symbolizing salvation and eternal beatitude. Some blessed are depicted with attributes identifying their martyrdom or virtues, such as crowns or palms.",
                "The Damned: The damned are depicted being dragged towards hell, with expressions of terror and despair. Their poses are contorted, bodies twisted in agony. Often, demons and monstrous creatures grasp and drag them downward. Their skin is dark, and the atmosphere around them is gloomy, devoid of the light that illuminates the blessed. Some damned are depicted with features reflecting their sins, emphasizing their destiny of eternal punishment.",
                "Angels with the Instruments of the Passion: Two groups of angels carry the instruments of Christ's Passion, such as the cross and the crown of thorns. These angels emphasize Christ's role as redeemer and judge."
                ]
    return sentence[idx]

def ts_sentences(idx):
    sentence = ["The eyes are wide open, eyebrows raised in an expression of intense fear. The mouth is open in a silent scream, lips stretched and teeth visible. The cheeks are hollowed, while the hands, with fingers spread wide, hold onto the sides of the face as if trying to restrain or control the intensity of the emotion. The face is painted with strong, bold strokes, emphasizing the despair and inner torment of the individual.",
                "Wavy Lines of the Sky: The sky is dominated by wavy lines stretching from left to right. These lines, painted in vibrant colors like red, orange, and yellow, create a visual effect of movement and instability.",
                "The Bridge: The bridge on which the main figure stands begins from the bottom left and extends diagonally towards the center-right of the painting. The straight lines of the bridge contrast with the undulations of the sky, adding tension to the image.",
                "Distant Figures: Two indistinct figures dressed in dark clothing walk on the bridge in the distance. These figures seem to disregard the anguish of the main figure and contribute to the sense of isolation and alienation.",
                "Waters of the Fjord: Beneath the bridge, the waters of the fjord are visible, painted in shades of dark blue and black. These waters also exhibit wavy lines, reflecting the turbulent sky and contributing to the eerie atmosphere of the painting."
                ]
    return sentence[idx]

def ki_sentences(idx):
    sentence = ["The faces of the two lovers are the only realistic elements in the painting, with their eyes closed in an expression of abandonment and ecstasy. The garland of ivy leaves on the man's head symbolizes the glory and triumph of love. This crown of green leaves framing the male head is a clear reference to the classical and mythological world. In antiquity, ivy was considered a symbol of love and an attribute of the god Dionysus. This detail, along with other symbols in the painting such as the crown of flowers on the woman, helps create a dreamy and mythological atmosphere around the love scene, elevating it to a plane above reality.",
                "The bodies of the two lovers are fused together in a single contour, symbolizing their perfect union. They occupy the central and lower part of the painting, emphasizing the importance of this moment of intimacy. The black and white rectangular pattern covering the man's clothing symbolizes his strength and masculinity. It occupies the upper left part of the painting, balancing the composition. The floral and circular motifs decorating the woman's dress express her femininity and maternity. They are located in the upper right part of the painting, creating a contrast with the rectangles of the man's outfit.",
                "The hands of the two lovers play a fundamental role in expressing the different gestures and personalities of the protagonists: the man's hands are large and powerful, gripping the woman firmly. This strong hold symbolizes his masculinity and desire for possession. The woman's hands, on the other hand, appear more delicate and tense, as if she is not fully surrendering to the embrace. The right hand encircling the man's neck almost seems to restrain a gesture of passion. The hands contribute to creating an atmosphere of bliss, stripping the work of erotic connotations in favor of spiritual intimacy. Despite the passion, the gestures are measured and delicate, almost as if wanting to preserve the sacredness of the moment. The different gestures of the hands reflect the difference in personality between man and woman in love, capturing the complementarity of the sexes.",
                "Meadow: The meadow on which the two lovers are lying is represented in a stylized and decorative manner, in contrast with the abstraction and gold that envelops the figures. The meadow features an abstract floral pattern, with patches of green color that highlight by contrast the 'warm' love of the two young people. This chromatic choice helps create a dreamy and transcendental atmosphere around the love scene.",
                "The golden mantle that wraps around the two lovers is covered with decorative motifs and stylized forms. It dominates most of the surface of the painting, creating a shimmering and transcendental effect."
                ]
    return sentence[idx]

# Creates a map of the museum with the correspondent directions to follow according to the previous room 
museum_map = {"e0,l0": {"l0": "front"},
              "l0,e0": {"l1": "front", "l19": "left", "e0": "back"},
              "l0,l1": {"e0": "front", "l19": "right", "l1": "back"},
              "l1,l0": {"l2": "front", "l18": "left", "l0": "back"},
              "l1,l18": {"l0": "right", "l2": "left", "l18": "back"},
              "l1,l2": {"l0": "front", "l18": "right", "l2": "back"},
              "l2,l1": {"l3": "right", "l9": "front", "l17": "left", "l1": "back"},
              "l2,l3": {"l1": "left", "l9": "right", "l17": "front", "l3": "back"},
              "l2,l9": {"l1": "front", "l3": "left", "l17": "right", "l9": "back"},
              "l2,l17": {"l1": "right", "l3": "front", "l9":"left", "l17": "back"},
              "l3,l2": {"l4": "front", "l2": "back"},
              "l3,l4": {"l2":"front", "l4": "back"},
              "l4,l3": {"l5": "left", "l3": "back"},
              "l4,l5": {"l3": "right", "l5": "back"},
              "l5,l4": {"l4":"back"},
              "l7,l9": {"l8": "left", "l9":"back"},
              "l7,l8": {"l9": "right", "l8": "back"},
              "l8,l7": {'l10': 'left',  'l7': 'back'},
              "l8,l10": {'l7': 'right', 'l10': 'back'},
              "l8,e2": {'l7': 'left', 'l10': 'front'},
              "l9,l2": {'l10': 'left', 'l7': 'front', 'l2': 'back'},
              "l9,l7": {'l10': 'right', 'l8': 'right', 'l2': 'front', 'l7': 'back'},
              "l9, l10": {'l2': 'right', 'l7': 'left', 'l10': 'back'},
              "l10,l8": {'l17': 'front', 'l9': 'left', 'l8': 'back'},
              "l10,l9": {'l17': 'left', 'l8': 'right', 'l9': 'back'},
              "l10,l17": {'l9': 'right', 'l8': 'front', 'l17': 'back'},
              "l12,l15": {'l15': 'back'},
              "l14,e1": {'l15': 'front'},
              "l15,l12": {'l16': 'left', 'l14': 'right', 'l12': 'back'},
              "l15,l14": {'l12': 'left', 'l16': 'front', 'l14': 'back'},
              "l15,l16": {'l12': 'right', 'l14': 'front', 'l16': 'back'},
              "l16,l15": {'l17': 'front', 'l15': 'back'},
              "l16,l17": {'l15': 'front', 'l17': 'back'},
              "l17,l2": {'l18': 'left', 'l10': 'right', 'l16': 'front', 'l2': 'back'},
              "l17,l10": {'l2': 'left', 'l16': 'right', 'l18': 'front', 'l10': 'back'},
              "l17,l16": {'l10': 'left', 'l18': 'right', 'l2': 'front', 'l16': 'back'},
              "l17,l18": {'l16': 'left', 'l2': 'right', 'l10': 'front', 'l18': 'back'},
              "l18,l1": {'l19': 'left', 'l17': 'right', 'l1': 'back'},
              "l18,l17": {'l1': 'left', 'l19': 'front', 'l17': 'back'},
              "l18,l19": {'l1': 'right', 'l17': 'front', 'l19': 'back'},
              "l19,l18": {'l0': 'left', 'l18': 'back'},
              "l19,l0": {'l18': 'right', 'l0': 'back'}
}

########################################### FUNCTIONS DEFINITIONS ##########################################

# Extracts rooms from the action move
def get_rooms(action):
    # Extract the arguments inside the parentheses
    open_paren_index = action.find('(')
    close_paren_index = action.find(')')
    if open_paren_index != -1 and close_paren_index != -1:
        arguments = action[open_paren_index+1:close_paren_index]
        args_list = arguments.split(", ")
        if len(args_list) == 3:
            l1 = args_list[1]
            l2 = args_list[2]
    return l1,l2

# Extracts the paint from the action visit
def get_work(action):
    # Extract the arguments inside the parentheses
    open_paren_index = action.find('(')
    close_paren_index = action.find(')')
    if open_paren_index != -1 and close_paren_index != -1:
        arguments = action[open_paren_index+1:close_paren_index]
        args_list = arguments.split(", ")
        if len(args_list) == 3:
            p1 = args_list[2]
    return p1

# Extracts room and related paint from action is_queue
def get_room_and_work(action):
    # Extract the arguments inside the parentheses
    open_paren_index = action.find('(')
    close_paren_index = action.find(')')
    if open_paren_index != -1 and close_paren_index != -1:
        arguments = action[open_paren_index+1:close_paren_index]
        args_list = arguments.split(", ")
        if len(args_list) == 4:
            l1 = args_list[2]
            p1 = args_list[3]
    return l1,p1

# Infers the order of the paints to visit according to the planned actions
def get_paints_order(actions):
    p_order = []
    for action in actions:
        if action.startswith("visit"):
            p1 = get_work(action)
            p1 = painting_map.get(p1)
            p_order.append(p1)
    return p_order

# Defines an event in which the user is too close to a work, probability increases with a higher number of visitors
def is_too_close(num_pers):
    if num_pers < 5:
        return weighted_choice([0, 1],[0.85, 0.15])
    elif num_pers >= 5 and num_pers < 8:
        return weighted_choice([0, 1],[0.65, 0.35])
    elif num_pers >= 8:
        return weighted_choice([0, 1],[0.5, 0.5])

#  Return a random element from the non-empty sequence `choices` with the probability of each element defined by `weights`.
def weighted_choice(choices, weights):
    total = sum(weights)
    cumulative_weights = []
    cumulative_sum = 0
    for weight in weights:
        cumulative_sum += weight
        cumulative_weights.append(cumulative_sum)
    
    x = random.uniform(0, total)
    for choice, cumulative_weight in zip(choices, cumulative_weights):
        if x < cumulative_weight:
            return choice