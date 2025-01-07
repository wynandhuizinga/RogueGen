import requests 
import json
import re
import os
import random
import time
import base64
import math
from datetime import datetime

# Custom
from classes.Settings import *
from classes.PromptVault import PromptVault as PV
from classes.Logger import Logger
from classes.PropGenerator import PropGenerator
from classes.FloortextureGen import *
from classes.PlayGen import *
from classes.DataValidator import DataValidator
from classes.APICallHandler import APICallHandler
from classes.GunGen import GunGen

api_handler = APICallHandler(API_SETTINGS)

class CharGen():

    def __init__(self,seed):
        self.seed = seed
        self.filepath = ""
        self.CharGenVersion = "v016"
        self.model_name = api_handler.modelname()

        
    def setup(self):
        # Setup 1: Create folder structure & logger
        self.filepath = str(charactersfolder) + str(self.CharGenVersion) +"/"+ str(datetime.today().strftime("%Y%m%d"))  +"-" + str(self.seed) +"-"+str(self.model_name) +"-"+str(ChatSystemTesting)+"/"
        
        if not os.path.exists(self.filepath):
            try:
                os.makedirs(self.filepath)
            except Exception as e:
                print(e)
                raise
        self.logger = Logger(self.filepath,logfilename,perfname)
        return self.filepath
        
    
    def generate(self,seed):
        generations = number_of_generations

        print("Planning to generate ",generations," fictional characters")

        # setup 2 - Input Parameters
        init_seed = self.seed
        ProgramStartTime = time.time()
        imagename = "" # placeholder
        gunGenerator = GunGen(self.seed, self.filepath)
    
        # Setup 3 - Instigation of API handler
        v_c = {
            "v_nameGen": 0,
            "v_nameGen_abort": 0,
            "v_genSpec": 0,
            "v_genSpec_abort": 0,
            "v_genPers_contName": 0,
            "v_genPers_abort": 0, 
            "v_genTaunt_abort": 0,
            "v_genBully_abort": 0,
            "v_genStakeRaise_abort": 0,
            "v_genSD": 0,
            "v_genSDBG": 0,
            "v_genSDBG_abort": 0,
            "v_genSD_abort": 0,
            "v_genProps": 0,
            "v_genProps_abort": 0,
            "v_genProps_failed_amount": 0,
            "v_genProps_noprops_abort": 0,
            "v_genScen_negEnvironments": 0,
            "v_genScen_negEnvironments_abort": 0,
            "v_total": 0
        }

        # Setup 4: Instigation of Prompt Vault and Data validator
        DV = DataValidator(api_handler, self.logger, FailureLogging)
        

        #=============================================#
        #           -+- Generation loop -+-           #
        #=============================================#

        for y in range(1, generations+1):
            # Step 1: Generation setup
            starttime = time.time()
            Failed = False
            FailureCounter = 0
            self.seed = init_seed + y
            chosen_mood = Moods[random.Random(self.seed).randint(0, len(Moods) -1)]
            chosen_style = Styles[random.Random(self.seed).randint(0, len(Styles) -1)]
            chosen_race = Races[random.Random(self.seed).randint(0, len(Races) -1)]
            selected_style = chosen_mood + " " + chosen_style
                
            with open('./templates/colorpicker.json', 'r', encoding="utf8") as file:
                colordata = json.load(file)

            fav_color_index = random.randint(0, len(list(colordata.get('color').keys()))-1)
            fav_color = list(colordata.get('color').keys())[fav_color_index] # get name at index
            fav_color_rgb = colordata.get('color', {}).get(list(colordata.get('color').keys())[fav_color_index]) # get rgb at index

            self.logger.logGeneration(str("Initiating: character nr: "+str(y)+", seed: "+str(self.seed)+", Style: "+selected_style))
            
            #JSON lists        
            data = {}
            CharGen_data = {}
            data['CharGen_data'] = CharGen_data
            CharGen_data['race'] = chosen_race
            CharGen_data['seed'] = self.seed
            CharGen_data['CharGen_version'] = self.CharGenVersion
            CharGen_data['selected_style'] = selected_style
            CharGen_data['mood'] = chosen_mood
            CharGen_data['fav_color'] = fav_color
            CharGen_data['fav_color_rgb'] = fav_color_rgb
            CharGen_data['llm-modelname'] = self.model_name
            Image_data = {}
            
            
            # Step 1: Generate name
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 1: Generate name", "selected style: ", selected_style, end='\r')
                
                retries = 10
                for x in range(0, retries+1):
                    if ChatSystemTesting:
                        name_response = api_handler.chat2(self.seed+x,PV.namePrePrompt(),PV.namePrompt(selected_style),20,4,1.3,0.9,90) # testing agentic generation
                    else:
                        name_response = api_handler.chat(self.seed+x,PV.namePrompt(selected_style),7,4,1,0.9,50) # testing non-agentic generation
                    name_response = name_response.replace("\n", "").replace("Name: ","").replace("name: ","")
                    if not(DV.nameValidate(name_response) and name_response.count(" ") < 3):
                        if FailureLogging: self.logger.logGeneration(str("ERROR Failed attempt ("+str(x)+") to generate name, Attempted name: "+name_response))
                        v_c["v_nameGen"] += 1
                    else:
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define name for seed: "+self.seed+". Character nr: ", y, " >= Retries: ", retries))
                    v_c["v_nameGen_abort"] += 1
                    Failed = True
                    
            if not (CGtesting or Failed):
                first_name = name_response.split(' ', 1)[0]
                filename = self.filepath + str(y-FailureCounter) + " - " + str(self.seed) + " - " + name_response+" - "+ selected_style +".json"
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Name identified: "+name_response+", (first name is: "+first_name+")"))
                data['name'] = name_response
                if VerboseLogging: self.logger.logTime("step-1")
                

            # Step 2a: Generate specialization
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 2a: Generate specialization", end='\r')
                specializationPrompt = PV.specializationPrompt(selected_style)

                retries = 10
                for x in range(0, retries+1):
                    specialization_response = api_handler.completion(self.seed+x,specializationPrompt,40,10,1,1,50)
                    specialization_response_c1 = first_name+" is specialized in: "+specialization_response
                    if not DV.validateSpecialization(specialization_response_c1,first_name): # BOGUS Check
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+x+"), Specialization prompt: "+specializationPrompt+" === result: "+specialization_response_c1))
                        v_c["v_genSpec"] += 1
                    else:
                        specialization_response_final = specialization_response_c1
                        CharGen_data['Specialization'] = specialization_response_final
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define specialization. Iteration (x): "+str(x)+" >= Retries: "+str(retries)))
                    v_c["v_genSpec_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Specialization identified: "+specialization_response_final))
                if VerboseLogging: self.logger.logTime("step-2a")

            # Step 2b: Generate looks description
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 2b: Generate looks description", end='\r')
                #description_response = api_handler.chat(self.seed,PV.descriptionPrompt(selected_style, name_response),150,40,1,0.9,50)
                if ChatSystemTesting:
                    description_response = api_handler.chat2(self.seed,PV.descriptionPrePrompt(), PV.descriptionPrompt(selected_style, name_response),150,40,1,0.9,50) # testing agentic generation
                else:
                    description_response = api_handler.chat(self.seed,PV.descriptionPrompt(selected_style, name_response),150,40,1,0.9,50) # testing non-agentic generation
                description_response_final = description_response.split('.',-1)[0]
                data['physical-description'] = description_response_final
                # TODO - Add validation
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Looks identified: "+description_response))
                if VerboseLogging: self.logger.logTime("step-2b")
                
            # Step 2c: Generate interaction description
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 2c: Generate interaction description", end='\r')
                #des_interaction_response = api_handler.chat(self.seed,PV.interactionPrompt(specialization_response, name_response),120,60,1,0.9,50)
                if ChatSystemTesting:
                    des_interaction_response = api_handler.chat2(self.seed,PV.interactionPrePrompt(),PV.interactionPrompt(specialization_response, name_response,chosen_mood),120,60,0.9,0.9,50) # testing agentic generation
                else: 
                    des_interaction_response = api_handler.chat(self.seed,PV.interactionPrompt(specialization_response, name_response),120,60,1,0.9,50) # testing non-agentic generation
                des_interaction_response_final = des_interaction_response.split('.',-1)[0]
                data['interaction-description'] = des_interaction_response_final
                # TODO - Add validation
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Interaction description identified: "+des_interaction_response))
                if VerboseLogging: self.logger.logTime("step-2c")
            
            # step 2e: Consolidate and combine descriptions
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 2d: combining descriptions", end='\r')
                combined_description = description_response_final + " " + des_interaction_response_final
                combined_description_final = (
                    combined_description
                    .replace(name_response, "{{char}}")
                    .replace(" she ", " {{char}} ")
                    .replace("She ", "{{char}} ")
                    .replace(" he ", " {{char}} ")
                    .replace("He ", "{{char}} ")
                    .replace(first_name, "{{char}}")
                    )
                data['description'] = combined_description_final
                if VerboseLogging: self.logger.logTime("step-2d")


            # Step 3: Generate personality
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 3: Generate personality", end='\r')
                retries = 10
                for x in range(0, retries+1):
                    #personality_response = api_handler.chat(self.seed+x,PV.personalityPrompt(description_response),50,4,1,0.9,50)
                    if ChatSystemTesting:
                        personality_response = api_handler.chat2(self.seed+x,PV.personalityPrePrompt(),PV.personalityPrompt(description_response),50,4,1.1,0.9,50) # testing agentic generation
                    else:
                        personality_response = api_handler.chat(self.seed+x,PV.personalityPrompt(description_response),50,4,1,0.9,50) # testing non-agentic generation
                    personality_response = re.sub('(\n|)[0-9]{1,2}. ',', ',personality_response)
                    personality_response = re.sub('\n- ',', ',personality_response)
                    if re.search(first_name, personality_response):
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt ("+str(x)+"), first name: "+first_name+" is found in string: "+ personality_response))
                        v_c["v_genPers_contName"] += 1
                    else:
                        personality_response_final = personality_response
                        if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Personality description identified: "+personality_response_final))
                        data['personality'] = personality_response_final
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to generate personality. Iteration (x): "+str(x)+" >= Retries: "+str(retries)))
                    v_c["v_genPers_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-3")


            # Step 4a: Generate scenario
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 4: Generate scenario", end='\r')
                scenarioPrompt = PV.scenarioPrompt(name_response,selected_style, ", ".join(SceneryFilter))
                retries = 10
                for x in range(0, retries+1):
                    #scenario_response = api_handler.chat(self.seed+x,scenarioPrompt,150,4,1,0.9,50)
                    if ChatSystemTesting:
                        scenario_response = api_handler.chat2(self.seed+x,PV.scenarioPrePrompt(), scenarioPrompt,200,4,1,0.9,50) # testing agentic generation
                    else:
                        scenario_response = api_handler.chat(self.seed+x,scenarioPrompt,150,4,1,0.9,50) # testing non-agentic generation
                    scenario_response = (scenario_response
                        .replace("I ", "{{user}} ")
                        .replace(name_response, "{{char}}")
                        .replace(" she ", " {{char}} ")
                        .replace("She ", "{{char}} ")
                        .replace(" he ", " {{char}} ")
                        .replace("He ", "{{char}} ")
                        .replace(first_name, "{{char}}")
                        )
                    SceneryInvalid = False
                    for i in SceneryFilter: # filters words you don't want the response to have to prevent monotonic repsonses
                        if scenario_response.find(i) > 1: # subst. LLM validation y/n
                            if FailureLogging: self.logger.logGeneration(str("Failed attempt ("+str(x)+"), scenario filter: "+i+" is found in string: "+ scenario_response))
                            v_c["v_genScen_negEnvironments"] += 1
                            self.seed += 1
                            SceneryInvalid = True
                            if SceneryInvalid: 
                                break
                    if not SceneryInvalid:            
                        scenario_response_final = scenario_response
                        if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Scenario description identified: "+scenario_response_final))
                        data['scenario'] = scenario_response_final
                        break
                    if x >= retries:
                        if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to generate scenario. Iteration (x): "+str(x)+" >= Retries: "+str(retries)))
                        v_c["v_genScen_negEnvironments_abort"] += 1
                        Failed = True
                if VerboseLogging: self.logger.logTime("step-4a")
            
            # Step 4b: Generate floor material
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 4b: Generate floor material", end='\r')
                text = api_handler.completion(self.seed+x,PV.floorMaterial(selected_style,scenario_response_final),15,3,1.4,1.2,80)
                floor_spec_final = text.split('.',1)[0].split(',',1)[0]
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Floor material description identified: "+floor_spec_final))
                data['floormaterial'] = floor_spec_final
                # TODO - Data validation
                if VerboseLogging: self.logger.logTime("step-4b")
            
            # Step 4c: Generate weapon element material
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 4c: Generate weapon element", end='\r')
                text = api_handler.completion(self.seed+x,PV.element(first_name,chosen_style,personality_response_final,description_response_final,specialization_response_final),25,3,0.9,0.9,80)
                elemental_final = text.split('.',1)[0].split(',',1)[0]
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Magical elemental description identified: "+elemental_final))
                data['magical-element'] = elemental_final
                if VerboseLogging: self.logger.logTime("step-4c")  
            
            # Step 4d: Generate element explosion
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 4d: Generate weapon explosion", end='\r')
                text = api_handler.completion(self.seed+x,PV.explosion(elemental_final),20,3,1.0,1.0,80)
                explosion_final = text.split('.',1)[0].split('\n',1)[0]
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Explosion description identified: "+explosion_final))
                data['magical-explosion'] = explosion_final
                if VerboseLogging: self.logger.logTime("step-4d")    


            # Step 5a: Generate first message
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 5a: Generate greeting", end='\r')
                greeting_gen_prompt = PV.greetingPrompt(scenario_response_final, first_name, chosen_style, chosen_mood)
                if ChatSystemTesting:
                    greeting_response = api_handler.chat2(self.seed,PV.greetingPrePrompt(),greeting_gen_prompt,200,10,0.9,1.2,80) # testing agentic generation
                else:
                    greeting_response = api_handler.chat(self.seed,greeting_gen_prompt,200,10,1,0.9,50) # testing non-agentic generation
                greeting_response_c1 = (greeting_response
                    .replace("I ", "{{user}} ")
                    .replace(name_response, "{{char}}")
                    .replace(" she ", " {{char}} ")
                    .replace("She ", "{{char}} ")
                    .replace(" he ", " {{char}} ")
                    .replace("He ", "{{char}} ")
                    .replace(first_name, "{{char}}")
                    .replace(" me ", " {{user}} ")
                    .replace(" me.", " {{user}}.")
                    .replace(" you ", " {{user}} ")
                    .replace("\r\n", " ")
                    .replace("\n", " "))
                greeting_response_final = "*" + greeting_response_c1.replace(greeting_response_c1.split(".")[-1], "") + "*"
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: First message identified: "+greeting_response_final))
                data['first_mes'] = greeting_response_final
                if VerboseLogging: self.logger.logTime("step-5a")

            # Step 5b: Generate taunt
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 5b: Generate taunt", end='\r')
                prompt = PV.tauntPrompt(combined_description,chosen_style)
                pattern = r'"(.*?)"'
                for x in range(0, retries+1):
                    failedAttempt = False
                    taunt_response = api_handler.completion(self.seed+10*x+3,prompt,150,4,1,1,50)
                    taunt_response_list = re.findall(pattern, taunt_response)
                    for i in range(len(taunt_response_list) - 1, -1, -1): # backward iteration to prevent empty slots
                        if first_name in taunt_response_list[i]:
                            taunt_response_list.pop(i)
                    if len(taunt_response_list) < 1:
                        failedAttempt = True
                    else:
                        for i in taunt_response_list:
                            i = (i
                                .replace("I ", "{{user}} ")
                                .replace(name_response, "{{char}}")
                                .replace(" she ", " {{char}} ")
                                .replace("She ", "{{char}} ")
                                .replace(" he ", " {{char}} ")
                                .replace("He ", "{{char}} ")
                                .replace(first_name, "{{char}}")
                                .replace(" me ", " {{user}} ")
                                .replace(" me.", " {{user}}.")
                                .replace("\r\n", " ")
                                .replace("\n", " "))
                    taunt_response_final = taunt_response_list
                    CharGen_data['taunts'] = taunt_response_final
                    if failedAttempt: # or not DV.quoteValidate(taunt_response_final):
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+str(x)+"), taunt prompt: \n"+'\n'.join(taunt_response_final)))
                    else: 
                        if VerboseLogging: self.logger.logGeneration(str("SUCCESS: taunts identified: \n"+'\n'.join(taunt_response_final)+"\nOriginal taunt_response: "+taunt_response))
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define taunt. Iteration (x): "+str(x)+ " >= Retries: "+str(retries)))
                    v_c["v_genTaunt_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-5b")
                    
            # Step 5c: Generate bully
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 5c: Generate bully", end='\r')
                prompt = PV.bullyPrompt(combined_description,chosen_style)
                pattern = r'"(.*?)"'
                for x in range(0, retries+1):
                    failedAttempt = False
                    bully_response = api_handler.completion(self.seed+20*x+3,prompt,150,4,1,1,50)
                    bully_response_list = re.findall(pattern, bully_response)
                    for i in range(len(bully_response_list) - 1, -1, -1): # backward iteration to prevent empty slots
                        if first_name in bully_response_list[i]:
                            bully_response_list.pop(i)
                    if len(bully_response_list) < 1:
                        failedAttempt = True
                    else:
                        for i in bully_response_list:
                            i = (i
                                .replace("I ", "{{user}} ")
                                .replace(name_response, "{{char}}")
                                .replace(" she ", " {{char}} ")
                                .replace("She ", "{{char}} ")
                                .replace(" he ", " {{char}} ")
                                .replace("He ", "{{char}} ")
                                .replace(first_name, "{{char}}")
                                .replace(" me ", " {{user}} ")
                                .replace(" me.", " {{user}}.")
                                .replace("\r\n", " ")
                                .replace("\n", " "))
                    bully_response_final = bully_response_list
                    CharGen_data['bullies'] = bully_response_final
                    if failedAttempt: # or not DV.quoteValidate(bully_response_final):
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+str(x)+"), bully prompt: \n"+'\n'.join(bully_response_final)))
                    else: 
                        if VerboseLogging: self.logger.logGeneration(str("SUCCESS: bullys identified: \n"+'\n'.join(bully_response_final)+"\nOriginal bully_response: "+bully_response))
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define bully. Iteration (x): "+str(x)+ " >= Retries: "+str(retries)))
                    v_c["v_genBully_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-5c")
                    
            # Step 5d: Generate stakeRaise
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 5d: Generate stakeRaise", end='\r')
                prompt = PV.stakeRaisePrompt(combined_description,chosen_style)
                pattern = r'"(.*?)"'
                for x in range(0, retries+1):
                    failedAttempt = False
                    stakeRaise_response = api_handler.completion(self.seed+30*x+3,prompt,150,4,1,1,50)
                    stakeRaise_response_list = re.findall(pattern, stakeRaise_response)
                    for i in range(len(stakeRaise_response_list) - 1, -1, -1): # backward iteration to prevent empty slots
                        if first_name in stakeRaise_response_list[i]:
                            stakeRaise_response_list.pop(i)
                    if len(stakeRaise_response_list) < 1:
                        failedAttempt = True
                    else:
                        for i in stakeRaise_response_list:
                            i = (i
                                .replace("I ", "{{user}} ")
                                .replace(name_response, "{{char}}")
                                .replace(" she ", " {{char}} ")
                                .replace("She ", "{{char}} ")
                                .replace(" he ", " {{char}} ")
                                .replace("He ", "{{char}} ")
                                .replace(first_name, "{{char}}")
                                .replace(" me ", " {{user}} ")
                                .replace(" me.", " {{user}}.")
                                .replace("\r\n", " ")
                                .replace("\n", " "))
                    stakeRaise_response_final = stakeRaise_response_list
                    CharGen_data['stakeRaise'] = stakeRaise_response_final
                    if failedAttempt: #or not DV.quoteValidate(stakeRaise_response_final):
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+str(x)+"), stakeRaise prompt: \n"+'\n'.join(stakeRaise_response_final)))
                    else: 
                        if VerboseLogging: self.logger.logGeneration(str("SUCCESS: stakeRaises identified: \n"+'\n'.join(stakeRaise_response_final)+"\nOriginal stakeRaise_response: "+stakeRaise_response))
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define stakeRaise. Iteration (x): "+str(x)+ " >= Retries: "+str(retries)))
                    v_c["v_genStakeRaise_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-5d")


            # Step 6a: Try render SD Picture - Prep prompt subject
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 6a: Try render SD Picture - Prep prompt subject", end='\r')
                retries = 10
                for x in range(0, retries+1):
                    sdprepPrompt = PV.sdprepPrompt(description_response, first_name)
                    if ChatSystemTesting:
                        SD_prompt_subj_response = api_handler.chat2(self.seed+x,PV.sdprepPrePrompt(),sdprepPrompt,150,20,1.2,1.2,80) # testing agentic generation
                    else:
                        SD_prompt_subj_response = api_handler.chat(self.seed+x,sdprepPrompt,150,20,0.9,0.8,50) # testing non-agentic generation
                    SD_prompt_subj_response = re.sub('(\n|)- ',', ',SD_prompt_subj_response)
                    SD_prompt_subj_response = re.sub('(\n|)[0-9]{1,2}. ',', ',SD_prompt_subj_response)
                    SD_prompt_subj_response = re.sub('^, ','',SD_prompt_subj_response)
                    SD_prompt_subj_response = SD_prompt_subj_response.strip()
                    SD_prompt_subj_response = re.sub('^.*?:','',SD_prompt_subj_response)
                    SD_prompt_subj_response = re.sub('^.*?is wearing','',SD_prompt_subj_response)
                    if not DV.validateSD(self.seed+x,SD_prompt_subj_response):
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+str(x)+"), SD prompt: "+SD_prompt_subj_response))
                        v_c["v_genSD"] += 1
                    else:
                        SD_prompt_subj_response_final = chosen_style + ", " +SD_prompt_subj_response
                        CharGen_data['SD-prompt'] = SD_prompt_subj_response_final
                        if VerboseLogging: self.logger.logGeneration(str("SUCCESS: SD insertion identified: "+SD_prompt_subj_response_final))
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define SD picture prompt. Iteration (x): "+str(x)+ " >= Retries: "+str(retries)))
                    v_c["v_genSD_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-6a")

            # Step 6b: Render SD Picture --> base picture to get enhanced
            print("\t\t\t\t Step 6b: Try render SD Picture - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed):
                sdrenderPrompt = PV.sdrenderPrompt(SD_prompt_subj_response_final, chosen_race,fav_color,chosen_mood)
                generated_image = api_handler.SDRender(self.seed,sdrenderPrompt,PV.sdrenderPromptNeg(),30,12,448,768,"DDIM")
                imagetitle = name_response+" - "+ selected_style +".png"           
                imagename = self.filepath + str(y) + " - " + str(self.seed) + " - " + imagetitle
                data['Image_data'] = Image_data
                Image_data['base'] = imagename
                if SDDebugging or AvatarTesting:
                    with open(imagename, 'wb') as f:
                        f.write(base64.b64decode(generated_image['images'][0]))
                if VerboseLogging: self.logger.logTime("step-6b")
            
            # Step 6c: Render SD Beaten Picture
            print("\t\t\t\t Step 6c: Try render SD Beaten Picture - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed):
                image_path = imagename
                result_content = api_handler.send_data_to_stable_diffusion(self.seed,generated_image['images'][0],PV.sdrenderBeatenPrompt(chosen_race),PV.sdrenderBeatenNegPrompt(),40,13,0.9,448,768,"DDIM") # self,seed,image_path,prompt,negprompt,steps,cfg_scale,strength,width,height,sampler_name
                Image_data['beaten'] = result_content
                if AvatarTesting: new_image_path = api_handler.save_image(result_content, image_path,"-beaten",AvatarTesting)
                else: new_image_path = api_handler.save_image(result_content, image_path,"-beaten")
                if VerboseLogging: self.logger.logTime("step-6c")
            
            # Step 6d: Render SD Wet Picture
            print("\t\t\t\t Step 6d: Try render SD Wet Picture - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed):
                image_path = imagename
                prompt = PV.sdrenderWetPrompt(chosen_race,chosen_mood)
                result_content = api_handler.send_data_to_stable_diffusion(self.seed,generated_image['images'][0],prompt,PV.sdrenderWetNegPrompt(),30,12,0.75,448,768,"DDIM") # self,seed,image_path,prompt,negprompt,steps,cfg_scale,strength,width,height,sampler_name
                Image_data['wet'] = result_content
                if AvatarTesting: new_image_path = api_handler.save_image(result_content, image_path,"-wet",AvatarTesting)
                else: new_image_path = api_handler.save_image(result_content, image_path,"-wet")
                if VerboseLogging: self.logger.logTime("step-6d")
            
            # Step 6e: Render SD regular Picture
            print("\t\t\t\t Step 6d: Try render SD Regular Picture - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed):
                image_path = imagename
                prompt = PV.sdrenderRegularPrompt(chosen_race,chosen_mood)
                result_content = api_handler.send_data_to_stable_diffusion(self.seed,generated_image['images'][0],prompt,PV.sdrenderRegularNegPrompt(),30,12,0.75,448,768,"DDIM") # self,seed,image_path,prompt,negprompt,steps,cfg_scale,strength,width,height,sampler_name
                Image_data['regular'] = result_content
                if AvatarTesting: new_image_path = api_handler.save_image(result_content, image_path,"-regular",AvatarTesting)
                else: new_image_path = api_handler.save_image(result_content, image_path,"-regular")
                if VerboseLogging: self.logger.logTime("step-6e")
                
            # Step 6f: define backgrounds:
            print("\t\t\t\t Step 6f: Try render SD background - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed):
                sdprepPrompt = PV.sdrenderBackgroundPrep(scenario_response_final) # chosen_style)
                retries = 10
                for x in range(0, retries+1):
                    SD_BG_prompt_subj_response = api_handler.completion(self.seed+x,sdprepPrompt,40,2,1,0.95,50)                
                    SD_BG_prompt_subj_response_final = ''.join(SD_BG_prompt_subj_response.split("\"")) #''.join(SD_BG_prompt_subj_response.split("\""))
                    CharGen_data['SD_BG_prompt'] = SD_BG_prompt_subj_response_final
                    if DV.validateSDBackground(SD_BG_prompt_subj_response_final):
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+str(x)+"), SD prompt: "+SD_BG_prompt_subj_response_final))
                        v_c["v_genSDBG"] += 1
                    elif VerboseLogging: 
                        self.logger.logGeneration(str("SUCCESS: SD BG prompt identified: "+SD_BG_prompt_subj_response_final))
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define SD BG picture prompt. Iteration (x): "+str(x)+ " >= Retries: "+str(retries)))
                    v_c["v_genSDBG_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-6f")
                
            # Step 6g: Render SD BG Picture --> base picture to get enhanced
            print("\t\t\t\t Step 6g: Try render SD BG Picture - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed or SDBGskipping):
                if y % 2 == 0:
                    generated_image = api_handler.SDRender(self.seed,PV.sdrenderBackground(SD_BG_prompt_subj_response_final),PV.sdrenderBackgroundNeg(),30,14,gameDimX,gameDimY,"DDIM")
                else: 
                    generated_image = api_handler.SDRender(self.seed,PV.sdrenderBackground2(SD_BG_prompt_subj_response_final),PV.sdrenderBackgroundNeg(),30,14,gameDimX,gameDimY,"DDIM")
                Image_data['background'] = generated_image['images'][0] # TODO - refactor to be consistent with other SD methods
                imagetitle = name_response+" - "+ selected_style + "-background.png"           
                imagename = self.filepath + str(y) + " - " + str(self.seed) + " - " + imagetitle
                with open(imagename, 'wb') as f:
                    f.write(base64.b64decode(generated_image['images'][0]))
                if VerboseLogging: self.logger.logTime("step-6g")

            # Step 6h: Render SD upscale background
            print("\t\t\t\t Step 6h: Try render SD BG Upscale Picture - stable diffusion calls", end='\r')
            if not (SDChartesting or Failed or SDBGskipping):
                image_path = imagename # TODO - depending on actual image whilst data is enough - 
                result_content = api_handler.upscale(image_path,"R-ESRGAN 4x+",multiplication) # self,seed,image_path,factor,upscaler_name
                Image_data['background-upscaled'] = result_content
                new_image_path = api_handler.save_image(result_content, image_path,"-background-upscaled")
                if VerboseLogging: self.logger.logTime("step-6h")
                

            # Step 7a: Prepare SD props list
            print("\t\t\t\t Step 7a: Prepare SD props list", end='\r')
            if not (CGtesting or Failed):
                retries = 10
                pattern = re.compile(r'\n- \(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+\s*\)')
                for x in range(0, retries+1):
                    props_response = api_handler.completion(self.seed+x,PV.propsQuery(SD_BG_prompt_subj_response_final),250,200,0.9,0.9,50)
                    props_response = "\n- "+props_response
                    parsedObjects = []
                    props = props_response.split('\n') 
                    valid_props = [prop for prop in props if pattern.match(f'\n{prop}')]
                    for prop in props:
                        prop = re.sub(r'[^a-zA-Z, ]', '', prop)
                        prop = re.sub(r'^\s', '', prop)
                        prop.replace('\n','')
                        prop = re.sub(r'made out of ','', prop)
                        prop = re.sub(r'made of ','', prop)
                        properties = prop.split(", ")
                        parsedObjects.append(properties)
                    parsedObjects = [obj for obj in parsedObjects if obj != [''] and len(obj) == 4]
                    parsedObjects = [obj for obj in parsedObjects if obj[1] in ["small", "medium", "large"] and obj[2] in ["breakable","unbreakable","nonbreakable"]]
                    if len(parsedObjects) < 4:
                        if FailureLogging: self.logger.logGeneration(str("Failed attempt (chargen) ("+str(x)+"), SD Props list too small: "+str(len(parsedObjects)) +", list of props: " +str(parsedObjects)))
                        v_c["v_genProps"] += 1
                    else:                                            
                        # TODO - correcting prop[1] (size) - is a book really large?
                        # TODO - where would you typically position each object?
                        props_response_final = parsedObjects
                        break
                if x >= retries:
                    if FailureLogging: self.logger.logGeneration(str("ABORT Failure (chargen) - Failed to define props. Iteration (x): "+str(x)+" >= Retries: "+str(retries)))
                    v_c["v_genProps_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Props identified: "+str(props_response_final)))
                if VerboseLogging: self.logger.logTime("step-7a")
                
            # Step 7b: Render SD sprites
            print("\t\t\t\t Step 7b: Try render SD Sprites - stable diffusion calls", end='\r')
            if not (SDProptesting or Failed):
                propCount = 1
                propList = []
                propAttempts = math.ceil(propsAmount/len(props_response_final))
                appender = []
                for i in range (0,propAttempts): # dirt
                    appender += props_response_final
                for prop in appender:
                    generated_image = api_handler.SDRender(self.seed+propCount,PV.propSpriteSDPrompt(prop[0],fav_color),PV.propSpriteSDPromptNeg(),30,14,512,512,"DDIM") # rectangles #TODO - update to 512x512
                    Image_data['props'] = Img = generated_image['images'][0] # TODO - refactor to be consistent with other SD methods
                    imagetitle = name_response+" - "+ selected_style + " - prop-orig - " + str(propCount) +" - " + prop[1] +" - "+ prop[0]+".png"           
                    imagename = self.filepath + str(y) + " - " + str(self.seed) + " - " + imagetitle
                    propCount += 1
                    prop = prop + [Img]
                    propList.append(prop)
                                
                if VerboseLogging: self.logger.logTime("step-7b")
                
            # Step 7c: Convert Sprites to transparent PNGs
            print("\t\t\t\t Step 7c: Convert Sprites to transparent PNGs", end='\r')
            if not (SDProptesting or Failed):
                propGenerator = PropGenerator()
                semi_tranparent_props = propGenerator.generateProp(propList,20)
                
                propcounter = 1
                storedProps = []
                for prop in semi_tranparent_props:
                    Image_data['propstransp'] = prop[5] # TODO - refactor to be consistent with other SD methods
                    if prop[4]:
                        imagetitle = name_response+" - "+ selected_style + " - prop-transp - "+ str(propcounter) + " - " + prop[1] +" - "+ prop[0] +" - "+ str(prop[4])+".png"           
                        imagename = self.filepath + str(y) + " - " + str(self.seed) + " - " + imagetitle
                        if SDDebugging:
                            with open(imagename, 'wb') as f:
                                f.write(base64.b64decode(prop[5]))
                        storedProps.append(prop)
                        propcounter += 1
                    elif FailureLogging: 
                        self.logger.logGeneration("Failed to generate prop with sufficient transparent borders (left, top, right)(chargen)")
                        v_c["v_genProps_failed_amount"] += 1
                if propcounter > 1:
                    CharGen_data['PropsList'] = storedProps 
                else: 
                    if FailureLogging: self.logger.logGeneration("ABORT Failure (chargen) - Failed to define any props.")
                    v_c["v_genProps_noprops_abort"] += 1
                    Failed = True
                if VerboseLogging: self.logger.logTime("step-7c")
                
            # Step 8: Generate enemy assets
            if not (SDProptesting or Failed):
                print("\t\t\t\t Step 8: Build character assets", end='\r')
                player = Player(self.filepath,self.logger,iteration=y,seed=seed+y,char_type='enemy',subject=chosen_style, element=elemental_final, splash=explosion_final)
                CharGen_data['PlayerSprites'] = player.coordinate_generations('enemy')
                floortextures = FloortextureGen(self.filepath,seed=seed+y,iteration=y,char_type="enemy", color_str=fav_color_rgb)
                CharGen_data['FloorSprites'] = floortextures.process_image(seed+y, PV.floor(floor_spec_final), PV.floorNeg(), 50, 13, 0.95, 512, 512, "DDIM") # neutral textures
                print("\t\t\t\t Step 8: Built character assets", end='\r')
                if VerboseLogging: self.logger.logTime("step-8x")
                
            # Step 9: Generate enemy guns for sale
            if not (SDProptesting or Failed):
                print("\t\t\t\t Step 9: Build character weapon assets", end='\r')
                Gun_Data = {}
                data['Gun_Data'] = Gun_Data
                Rifles = Rocket_Launchers = Magic_Wands = Gatling_Guns = {}

                data['Gun_Data']['Rifles'] = gunGenerator.generate("Rifle",2,5,fav_color, fav_color_rgb, iteration=y)
                data['Gun_Data']['Rocket_Launchers'] = gunGenerator.generate("Rocket Launcher",2,4,fav_color, fav_color_rgb,iteration=y)
                data['Gun_Data']['Magic_Wands'] = gunGenerator.generate("((magic wand))",2,4,fav_color, fav_color_rgb,iteration=y)
                data['Gun_Data']['Gatling_Guns'] = gunGenerator.generate("Gatling Gun",2,3,fav_color, fav_color_rgb,iteration=y)
                
                print("\t\t\t\t Step 9: Built character weapon assets", end='\r')
                if VerboseLogging: self.logger.logTime("step-9")


            # Step 10: Build JSON
            if not (CGtesting or Failed):
                print("\t\t\t\t Step 10: Build JSON", end='\r')
                endtime = time.time()
                duration = (endtime - starttime)
                CharGen_data['generated_date'] = str(endtime)
                CharGen_data['generation_time'] = str(duration)
                json_data = json.dumps(data) # Bogus?
                if VerboseLogging: self.logger.logTime("step-10")


            # Step 11: Store to file
                        
            if Failed: 
                FailureCounter += 1 
                filename = self.filepath + str(y-FailureCounter) + " - " + str(self.seed) + " - " + name_response+" - "+ selected_style +".json"

                
            if not (CGtesting or SDChartesting or Failed):
                print("\t\t\t\t Step 11: Store to file", end='\r')
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("character number: ", str(y), "Seed: ", self.seed, "generation_time: ",str("{:.2f}".format(duration)), ", stored as: ", filename)
                SuccessReport = "Success - Seed: "+str(self.seed)+", Character: "+str(y)+", time spent: "+str("{:.2f}".format(duration))
                if VerboseLogging: self.logger.logGeneration(str("SUCCESS: Finished character nr: "+str(y)+" seed: "+str(self.seed)+" name: "+name_response+", in "+str("{:.2f}".format(duration))+" seconds, file path: "+self.filepath+filename))
                if VerboseLogging: self.logger.logTime("step-11")
            elif Failed:
                if FailureLogging: self.logger.logGeneration(str("Failed to create a file for Seed: "+str(self.seed)+", character nr: "+str(y)))
                v_c["v_total"] += 1
                if VerboseLogging: self.logger.logTime("Failed Step: ")
            else:
                print("Total failure / debugging")
                
            if y < generations:
                print("Forcasted time left: ", str("{:.2f}".format((time.time() - ProgramStartTime) / (y) * (generations-y))), ". Average generation speed: ",str("{:.2f}".format((time.time() - ProgramStartTime) / (y))),"\n============\n")
            else: 
                print("Batch Complete in: ", str("{:.2f}".format(time.time() - ProgramStartTime)))
            if VerboseLogging: self.logger.record_averages()

                
                
        # Step 12: Generate Player
        #if not (SDProptesting or Failed):
        print("\t\t\t\t Step 11: Build player assets", end='\r')
        
        if VerboseLogging: self.logger.logTime("\n\nPlayer assets\n****************")
        playerData = {}
        CharGen_data = {}
        playerData['CharGen_data'] = CharGen_data
        Gun_Data = {}
        playerData['Gun_Data'] = Gun_Data
        Rifles = Rocket_Launchers = Magic_Wands = Gatling_Guns = {}
        
        # Pick random color for player
        with open('./templates/colorpicker.json', 'r', encoding="utf8") as file:
            jsondata = json.load(file)
        if fav_color == "":
            fav_color_index = random.randint(0, len(list(jsondata.get('color').keys()))-1)
            fav_color = list(jsondata.get('color').keys())[fav_color_index] # get name at index
            fav_color_rgb = jsondata.get('color', {}).get(list(jsondata.get('color').keys())[fav_color_index]) # get rgb at index
            print("CHARGEN: Player's Fav_color:",fav_color,"- fav_color_rgb:",fav_color_rgb)
        else: 
            fav_color_rgb  = jsondata.get('color', {}).get(fav_color)
            print("CHARGEN: Player's Fav_color:",fav_color)#,"- fav_color_rgb:",fav_color_rgb)
        
        playerData['Gun_Data']['Rifles'] = gunGenerator.generate("Rifle",2,5,fav_color, fav_color_rgb, iteration=0)
        playerData['Gun_Data']['Rocket_Launchers'] = gunGenerator.generate("Rocket Launcher",1,4,fav_color, fav_color_rgb,iteration=0)
        playerData['Gun_Data']['Magic_Wands'] = gunGenerator.generate("((magic wand))",1,5,fav_color, fav_color_rgb,iteration=0)
        playerData['Gun_Data']['Gatling_Guns'] = gunGenerator.generate("Gatling Gun",1,3,fav_color, fav_color_rgb,iteration=0)

        
        player = Player(self.filepath,self.logger,seed=seed+generations*2,char_type='player',fav_color=fav_color,subject="Robot")
        playerData['CharGen_data']['PlayerSprites'] = player.coordinate_generations('player')
        floortextures = FloortextureGen(self.filepath,seed=seed+generations*2,char_type="player", color_str=str(player.fav_color_rgb))
        playerData['CharGen_data']['FloorSprites'] = floortextures.process_image(seed, PV.floor("wood"), PV.floorNeg(), 50, 13, 0.95, 512, 512, "DDIM")
        playerData['FloorSprites-neutral'] = floortextures.process_image_neutral(seed+100, PV.floor("grass"), PV.floorNeg(), 50, 13, 0.95, 512, 512, "DDIM") # neutral textures
        with open(self.filepath+"/0 - "+str(seed)+" - player.json", 'w', encoding='utf-8') as f:
            json.dump(playerData, f, ensure_ascii=False, indent=4)
        if VerboseLogging: self.logger.logTime("step-11")        
        
        # Bad correction for aborted character generations
        generations = generations - FailureCounter

        # Step 13: End summary
        if VerboseLogging: self.logger.logGeneration(str("\n\n\nFINAL STATS\n============\n"+str(v_c | DV.valCount())))
        
