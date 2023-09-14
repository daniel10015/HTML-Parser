# http syntax: https://spongebob.fandom.com/wiki/<episode_title>/transcript
# Usage: scrapes (nearly) every episode on the spongebob episode wiki (so if it gets updated then the script will always be updated)
#  **Can be modified, just change ep_list = ['desired_episodes', 'go here']** Double check episode names, they must be perfect!!!!!
# prints all sentences to standard output so redirect it to a file
# note1: the last few lines will be data so either directly remove those from the script or account for it if using the output file
# note2: inner boldings will be left in because they denote capital letters

# Example: Output into `output.txt`: python scrape.py >> output.txt 
# What this script does  
# -1. In main get a list of all episodes
# 0. Go to Spongebob Episode and get the html source
# 1. parse http and search for a {Start}
# 2. Everything between {Start} and {End} (usually ) but don't include anything in '[narration blob (ie. description of an action)]'
# 3. stop once {End} (EOL End Of Line)
# Repeat step 1. if not the end 
# End of HTML source, print to standard output, push into a text file
# repeat step 0 until end of list 

import requests as req # make http requests
import time as t # track timing
import multiprocessing # parallel processes for the individual episode http requests and html parsing

# parses a line of the HTML 
def parse(text, index_start, END, delim_start, delim_end):
  generatedText = ""
  i_curr = index_start
  while(not text[i_curr:i_curr+len(END)] == END): # keep going until end of txt
    if(text[i_curr:i_curr+len(delim_start)] == delim_start):
      generatedText += text[index_start:i_curr] # get all previous dialogue
      while(not text[i_curr:i_curr+len(delim_end)] == delim_end): # this checks for italics which is not in dialogue
        i_curr+=1
      index_start = i_curr + len(delim_end) + 1 # new start value for next set of dialogue
    if text[i_curr] == "[": # very few cases where italics fail, but if they do then this'll remove brackets
      generatedText += text[index_start:i_curr]
      while(not text[i_curr] == "]"): # loop until end of bracket
        i_curr+=1
      index_start = i_curr + len(delim_end) + 1 # new start value for next set of dialogue
    
    i_curr+=1
  generatedText += text[index_start:i_curr]
  return generatedText



# make html request then loops through every line of the html, calls parse(line) which parses the given line
def parseEpisode(URL):
  url = URL
  request = req.get(url)
  CHARACTER = "Squidward" # character to look for (Make sure it's spelled PERFECTLY!!!!)
  prefix_start = '<li><b>' # same as end
  start_of_transcript = "<ul><li><i>"
  start='<li><b>'+CHARACTER+':</b>' 
  sentence=""
  end='</li>'
  DELIM="<i>"
  DELIM_CLOSE="</i>"
  source = request.text

  start_index = -1
  end_index = -1
  iters = 0
  ep_sent = ""

  for i in range(0, len(source)-len(start)):
    if(source[i:i+len(start)] == start): # utilize to get previous line (if it fails keep going to previous lines) for prompts
      # search for previous line that is dialogue, if doesn't exist then continue
      iters+=1
      start_index = i + len(start)+1
      sentence = parse(source, start_index, end, DELIM, DELIM_CLOSE)
      sentence = (sentence.encode("utf-8"))
      # print(sentence)
      if iters == 1:
        ep_sent = sentence.decode()
      else:
        ep_sent += f"\n{sentence.decode()}" # add prompts here, then add '#' as a delimeter (surround by {a:b})
  return ep_sent # returns all wanted lines from html 

# gets a list of all spongebob episodes (from spongebob episode wikipedia)
# this is quite complicated since I don't know html very well, 
# but I eventually discovered the unique patterns... it works well! 
def getEpisodeList(url, lineStart):
  evil_curse = {"<"}
  delim_sneak = '">'
  delim_end_seank = "</a>"

  delim_real = 'style="text-align:left">"'
  delim_end_real = '"</td>'
  # delim_real = '">"'
  # delim_end_real = '"</td>'
  # episode_area = 'text-align:left'
  list = []
  src = req.get(url)
  src = src.text

  src = src.split('\n') # split lines into lists
  src = src[lineStart:]
  episode_list = 310
  episode_count = 0
  LELE = ""

  # src = "".join(src[lineStart:]) # join all elements into a string
  for ep in src: # loop each line
    delim = delim_real
    delim_end = delim_end_real
    episode_count += 1
    if(episode_count == 232):
      return list
    if episode_list <= episode_count:
      break
    i=0
    while i < len(ep): # char in line
      #print(i)
      if(ep[i:i+len(delim)] == delim and ep[i+len(delim)] in evil_curse):
        i = i+len(delim) + 1
        delim =  delim_sneak
        delim_end =  delim_end_seank
        # break # not real line, so end while loop

      # elif(ep[i:i+len(delim)] == delim and delim == delim_real and not ep[i-len(episode_area):i] == episode_area): #not an episode
      #   i+5
      #   continue

      elif(ep[i:i+len(delim)] == delim): # start getting episode
        i+=len(delim)
        j = i
        while((not ep[j:j+len(delim_end)] == delim_end)): #or (not ep[j:j+len(delim_end)] == "<br ")):
          j+=1
        list.append(ep[i:j])
        # print(f"hard-episode: {ep[i:j]}")
        i=j+1 # jump
        delim = delim_real
        delim_end = delim_end_real
        # break # line completed
      i+=1 # iterate
  return list

# drives a each process for multiprocessing on different cores
# this speeds up time by T/N where T is time it takes on 1 core and N is number of cores 
# I ran this on an 8-core cpu so I cut my time down from 75 seconds down to 10 seconds.
# The 5 second error is probably because of making HTTP requests at the same time, so there's wasted downtime.
# So, to make this even faster probably make a process that makes HTTP requests WHILE parsing, and this works 
# perfectly for parallel architecture
# However, this is uneccesary at the moment, since parsing is clearly what takes the most time. 
# I'm satisfied, I just need this for training and testing data, so this is just a necessary step to solve a larger problem   
def runProcess(ep_list, url_start, url_end):
  sentences = ""
  count = 0
  for i in ep_list:
    # random thing I was getting at one point (not anymore though), so it's unnecessary but I leave it in just in case
    if(i=='.mw-parser-output .vanchor>:target~.vanchor-text{background-color:#b1d2ff}</style><span class="vanchor"><span id="Squid_Wood"></span><span class="vanchor-text">Squid Wood</span></span>"</td><td style="text-align:center">Andrew Overtoom</td><td style="text-align:center"><i>Written by</i>&#8202;: Casey Alexander, Chris Mitchell, and Dani Michaeli<br /><i>Storyboarded by</i>&#8202;: Casey Alexander and Chris Mitchell <small>(directors)</small></td><td style="text-align:center">July&#160;24,&#160;2007<span style="display:none">&#160;(<span class="bday dtstart published updated">2007-07-24</span>\)</span><sup id="cite_ref-S4V2_124-4" class="reference"><a href="#cite_note-S4V2-124">&#91;DVD 8&#93;'):
      continue
    count += 1
    url = url_start + i + url_end
    sentence = ""
    # only add sentence IF dialogue exists in an episode (this removes unecessary whitespace)
    if count == 1 or sentences=="":
      sentence = f"{parseEpisode(url)}"
      if not sentence == "":
        sentences = sentence
    else:
      sentence += f"{parseEpisode(url)}"
      if not sentence == "":
        sentences += f"\n{sentence}"
  
  # try blocks are incase unicode outside of ascii (such as a circle or music note) gets parsed returned in the line
  # if an (encoding) exception occurs, then parse sentences for the character that's no ascii, then remove it from sentence   
  try:
    print(sentences) # attempt to print to stdout
  except:
    i=0
    while i < len(sentences): # while loop allows for dynamic boundaries
      if ord(sentences[i]) >= 128: # if not ascii then remove from sentences
        sentences = sentences[0:i] + sentences[i+1:len(sentences)]
      i+=1 # iterate because python for-loop is not good when upper-bound is dynamic
    print(sentences) # print cleaned up sentences to stdout


# Driver of the script
# 
def main():
  start_time = t.time() 
  # the 'root' of the url is the episode name (ie, 'Help_Wanted')
  url_start = "https://spongebob.fandom.com/wiki/" # prefix-link to transcript
  url_end = "/transcript" # postfix-link to transcript

# episode list that I USED to use (generated by chatgpt), but it covered less than half the episodes ever aired
#   episode_list = ["Help_Wanted", "Reef_Blower", "Tea_at_the_Treedome"
# "Bubblestand", "Ripped_Pants", "Jellyfishing"
# "Plankton!", "Naughty_Nautical_Neighbors", "Boating_School"
# "Pizza_Delivery", "Home_Sweet_Pineapple", "Mermaid_Man_and_Barnacle_Boy"
# "Pickles", "Hall_Monitor", "Jellyfish_Jam"
# "Sandy's_Rocket", "Squeaky_Boots", "Nature_Pants"
# "Opposite_Day", "Culture_Shock", "F.U.N."
# "MuscleBob_BuffPants", "Squidward_the_Unfriendly_Ghost", "The_Chaperone"
# "Employee_of_the_Month", "Scaredy_Pants", "I_Was_a_Teenage_Gary"
# "SB-129", "Karate_Choppers", "Sleepy_Time"
# "Arrgh!", "Rock_Bottom", "Texas"
# "Walking_Small", "Fools_in_April", "Neptune's_Spatula"
# "Hooky", "Mermaid_Man_and_Barnacle_Boy_II", "The_Paper"
# "Squilliam_Returns", "The_Algae's_Always_Greener", "SpongeBob_B.C."
# "Wet_Painters", "Krusty_Krab_Training_Video", "Party_Pooper_Pants"
# "Chocolate_with_Nuts", "Mermaid_Man_and_Barnacle_Boy_V", "New_Student_Starfish"
# "Clams", "Ugh", "The_Great_Snail_Race"
# "Mid-Life_Crustacean", "Born_Again_Krabs", "I_Had_an_Accident"
# "Krabby_Land", "The_Camping_Episode", "Plankton's_Army"
# "Missing_Identity", "The_Sponge_Who_Could_Fly", "SpongeBob_Meets_the_Strangler"
# "Pranks_a_Lot", "Fear_of_a_Krabby_Patty", "Shell_of_a_Man"
# "The_Lost_Mattress", "Krabs_vs._Plankton", "Have_You_Seen_This_Snail?"
# "Skill_Crane", "Good_Neighbors", "Selling_Out"
# "Funny_Pants", "Dunces_and_Dragons", "Selling_Out"
# "The_Krusty_Sponge", "Sing_a_Song_of_Patrick", "A_Flea_in_Her_Dome"
# "The_Donut_of_Shame", "The_Krusty_Plate", "BlackJack"
# "Banned_in_Bikini_Bottom", "Stanley_S._SquarePants", "Goo_Goo_Gas"
# "Atlantis_SquarePantis", "Picture_Day", "Pat_No_Pay"
# "Blackened_Sponge", "Mermaid_Man_vs._SpongeBob", "The_Inmates_of_Summer"
# "The_Battle_of_Bikini_Bottom", "Pest_of_the_West", "The_Two_Faces_of_Squidward"
# "SpongeHenge", "Banned_in_Bikini_Bottom", "Stanley_S._SquarePants"
# "House_Fancy", "Krabby_Road", "Penny_Foolish"
# "Nautical_Novice", "Spongicus", "Suction_Cup_Symphony"
# "Not_Normal", "Gone", "The_Splinter"
# "Slide_Whistle_Stooges", "A_Life_in_a_Day", "Sun_Bleached"
# "Giant_Squidward", "No_Nose_Knows", "Patty_Caper"
# "Plankton's_Regular", "Boating_Buddies", "The_Krabby_Kronicle"
# "The_Slumber_Party", "Grooming_Gary", "SpongeBob_SquarePants_vs._The_Big_One"
# "A_Life_in_a_Day", "Sun_Bleached", "Giant_Squidward"
# "No_Nose_Knows", "Patty_Caper", "Plankton's_Regular"
# "Boating_Buddies", "The_Krabby_Kronicle", "The_Slumber_Party"
# "Grooming_Gary", "SpongeBob_SquarePants_vs._The_Big_One", "Porous_Pockets"
# "Choir_Boys", "Krusty_Krushers", "The_Card"
# "Dear_Vikings", "Ditchin'", "Grandpappy_the_Pirate"
# "Cephalopod_Lodge", "Squid's_Visit", "To_SquarePants_or_Not_to_SquarePants"
# "Shuffleboarding", "Professor_Squidward", "Pet_or_Pests"
# "Komputer_Overload", "Gullible_Pants", "Overbooked"
# "No_Hat_for_Pat", "Toy_Store_of_Doom", "The_Clash_of_Triton"
# "Sand_Castles_in_the_Sand", "Shell_Shocked", "Chum_Bucket_Supreme"
# "Single_Cell_Anniversary", "Truth_or_Square", "Pineapple_Fever"]
  
  # HTTP request to the wiki page (skips the first 728 lines) and returns list of every episode
  ep_list = getEpisodeList('https://en.wikipedia.org/wiki/List_of_SpongeBob_SquarePants_episodes', 729) 
  
  # multiprocess the html parsing 
  processes = []
  # split ep_list in 8 (for the 8 cores)
  cut = int(len(ep_list)/8)
  # print(len(ep_list)) # prev was 2142, 
  for i in range(0, len(ep_list), cut):
    p = multiprocessing.Process(target=runProcess, args=(ep_list[i:i+cut], url_start, url_end))
    processes.append(p)
    p.start() # start parsing
      
  for process in processes:
      process.join() # wait for parsing to finish
  # data collection:
  print(f"Number of episodes pulled from: {len(ep_list)}") 
  start_time = t.time() - start_time # start_time is now total_time 
  print(f"time taken: {start_time}")

if __name__ == "__main__":
  main()
  print("successful") # prints if main() finishes 