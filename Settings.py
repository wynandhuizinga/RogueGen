# SETUP Parameters
number_of_generations = 5
SeedOverride = "" #54787032 #"provide 8 digit number without quotes"
playDirectory = "" #"./assets/generated/v016/20241215-54787032-llama2-13b-orca-8k-3319-True/" # define folder with forward (/) slashes, end with slash --> ./assets/generated/.../

lengthOfGame = 1

gameDimX = 1344 # 1536
gameDimY = 838
multiplication = 1.6 # SD background upscale multipliar
propsAmount = 5 # 40 # TODO - put back to 40 # number of generation attempts for props (can still drop to lower if images are not passing tests)

charactersfolder = "./assets/generated/"
logfilename = "batch-log.txt" # Verbose logging
perfname = "performance.txt" # Verbose logging

CGtesting = False # Turns script into dummy values
SDChartesting = False # Turns off SD
SDProptesting = False # Turns off SD
SDBGskipping = True # Turns off Background rendering
ChatSystemTesting = True
SDDebugging = False # generates images for all assets (as opposed to solely create json files)

# SDtestingGrand = True
VerboseLogging = True
FailureLogging = True

Races = ["Caucasian","White","Asian","Indian"]
Moods = ["cranky","extremely happy","lazy","talkative","businessminded","mindblown","lush","explorative","Dead tired","depressed","excited","spiritual","pleasing","Joyful","Melancholy","Content","Anxious","Angry","Hopeful","Fearful","Excited","Frustrated","Nostalgic","Confident","Guilty","Lonely","Grateful","Bored","Embarrassed","Curious","Loving","Resentful"]
Styles = ["goth","diva","god","feminist","villain","superhero","demon","devil","celestial","military person","high-school student","dumb shit","survivor","sorcerer","medieval princess","business lady","hospital nurse","doctor","holographic","multi dimensional space entity","viking","hypnotist","mind-reader","magician","vampire","samurai","mermaid","mma fighter","pro-wrestler","skater","librarian","policeman","gardener","master judoka","street-dancer","flight attendant","shaman","celestial","gate-keeper","hitch-hiker","barber","journalist","receptionist","teacher","health educator","waitress","secret agent","company boss","forest ranger","jail warden","plumber","carpenter","dermatologist","shaolin kungfu monk","kpop dancer","Actor","Bartender","Dentist","Makeup Artist","Musician","Salesperson","Taxi Driver","Zookeeper"]
SceneryFilter = ["bed","bedroom"]


playercolor = "alice blue"
playersubject = "cat"

API_SETTINGS = {
    'LLMendpoint': 'http://localhost:5000',
    'SDendpoint': 'http://127.0.0.1:7860'
}

selected_style = name_response = specialization_response = description_response = first_name = chosen_style = SD_prompt_subj_response_final = scenario_response_final = ""
