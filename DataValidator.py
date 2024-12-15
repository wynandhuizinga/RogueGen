import requests 
import random
import re

from PromptVault import PromptVault as PV

class DataValidator():

    def __init__(self, api_handler, logger, FailureLogging):
        self.api_handler = api_handler
        self.logger = logger
        self.FailureLogging = FailureLogging
                
        self.v_c = {
            "v_nameGen": 0,
            "v_SD_caps": 0,
            "v_SD_quote": 0,
            "v_SD_comCols": 0,
            "v_SD_YN": 0,
            "v_SD_answer_no": 0,
            "v_SD_any_other_r": 0,
            "v_SD_BG_containsfilterwords": 0
        }
    
    def nameValidate(self, name):
        for c in name:
            if not (c.isalpha() or c.isdigit() or c.isspace()): # validates if name consists of special characters, numbers and spaces.
                if self.FailureLogging: self.logger.logGeneration(str("Problem with character: "+c))
                self.v_c["v_nameGen"] += 1
                return False
        return True

    def quoteValidate(self, quote): # still required?
        if quote.count("\"") < 5:
            if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - There are few few quotes (\")"))
            self.v_c["v_SD_quote"] += 1
            return False
        return True
        
    def validateSD(self,seed,response):
        # TODO - Confidence system - take 100, subtract points based on below validations
        
        # Manual response data validation
        if response.count(",")+5 < len(re.findall('[A-Z]',response)):
            if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - There are too many capitals"))
            self.v_c["v_SD_caps"] += 1
            return False
        elif response.count(",") < response.count(":") * 2:
            if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - There are too many colons"))
            self.v_c["v_SD_comCols"] += 1
            return False

        yesNoValPrompt = PV.yesNoValPrompt(response)

        for x in range(0, 10):
            validation = self.api_handler.chat(seed+x,yesNoValPrompt,3,1,0.9,1,3)
            if len(validation) > 4: # response longer than max logical answer: i.e. yes!
                if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - validation message too long, ("+str(x)+") attempt. Attempted validation: "+validation))
                self.v_c["v_SD_YN"] += 1
            else:
                if validation.lower().find("yes") > -1:
                    return True
                elif validation.lower().find("no") > -1:
                    if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - LLM validation answer is no"))
                    self.v_c["v_SD_answer_no"] += 1
                    return False
                else:
                    if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - Failed to properly figure out if this is a comma separated list of keywords. Input data: "+input+" Seed: "+str(seed)))
                    self.v_c["v_SD_any_other_r"] += 1
                    return false


    def validateSpecialization(self,input,first_name):
        seed = random.randint(1, 10000000)
        
        # Manual response data validation - response starting with first name y/n
        if not input.split(' ', 1)[0].lower() == first_name.lower() :
            if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - Specialization not starting with first name"))
            return False
        else:
            return True

    def validateProps(self,props_response):
        # Manual response data validation - response starting with first name y/n
        
        pattern = re.compile(r'\n- \(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+\s*\)')
        cleaned_props = re.sub(r'[^a-zA-Z,]', '', input_string)
        props = props_response.split('\n')
        valid_props = [prop for prop in props if pattern.match(f'\n{prop}')]
        print(valid_props)
        for prop in props:
            prop = re.sub(r'[^a-zA-Z,]', '', prop)
            properties = prop.split(",")
            prop.append(properties)
        print(valid_props)
        if props_response.lower().find("\n") < 0:
            if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - Specialization not starting with first name"))
            return False
        else:
            return True

    def validateSDBackground(self,input):
        seed = random.randint(1, 10000000)
        failure = False
        filterWords = [' man ',' guy ',' woman ','{{char}}','{{user}}','people','hand','participants','character']
        for filterWord in filterWords:
            if input.lower().find(filterWord) >= 0:
                if self.FailureLogging: self.logger.logGeneration(str("Failure: DV - SD background containing word: "+filterWord+". Found in: "+ input))
                failure = True
                self.v_c["v_SD_BG_containsfilterwords"] += 1
        return failure


    def valCount(self):
        return self.v_c


        '''
        prompt = "Is the following text summing up attributes of somebody's visual appearance?\n\n"+input_text+"\n\nAnswer only with YES or NO"

        for x in range(0, 10):    
            res = requests.post('http://localhost:5000/v1/chat/completions', 
                            json={
                                "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                    }
                                ],
                                "mode": "instruct",
                                "max_tokens": 3,
                                "min_tokens": 1,
                                "temperature": 0.9, #smart?
                                # "top_p": 0.9,
                                "seed": seed,
                                "top_k": 3,
                                "stream": False
                            })
            validation = res.json()['choices'][0]['message']['content']
            
            if len(validation) > 4: # response longer than max logical answer: i.e. yes!
                print("Failure: DV - validation message too long, (", x, ") attempt. Attempted validation: ",validation)
                seed += 1
            else:
                if validation.lower().find("yes") > -1:
                    print("Passed SD description: ",input_text)
                    return True
                elif validation.lower().find("no") > -1:
                    print("Failure: DV - validation answer is no: ",validation.lower().find("no"))
                # Log details
                    ErrorReport = "Validator says no\nSeed: "+str(seed)+", Prompt: "+prompt+"\n, Answer: "+validation
                    with open('datavalidator-err.txt', 'a', encoding='utf-8') as file:
                        file.write('\n======================\n'+ErrorReport)
                        
                    return False
                else:
                    print("Failure: DV - Failed to properly figure out if this is a comma separated list of keywords. Input data: ",input," Seed: ",seed)
                    return false
                    '''
                    
