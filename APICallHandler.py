import requests 
import random
import re
import json
import base64
import os


class APICallHandler():
    
    def __init__(self, settings):
        self.LLMendpoint = settings['LLMendpoint']
        self.SDendpoint = settings['SDendpoint']

    def modelname(self):
        model_name = requests.get(self.LLMendpoint+'/v1/internal/model/info').json()['model_name'] # Retrieve model name
        return model_name

    def chat(self,seed,prompt,max_tokens,min_tokens,temperature,top_p,top_k):
        res = requests.post(self.LLMendpoint+'/v1/chat/completions', 
                            json={
                                "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                    }
                                ],
                                "mode": "instruct",
                                "max_tokens": max_tokens,
                                "min_tokens": min_tokens,
                                "temperature": temperature,
                                "top_p": top_p,
                                "seed": seed,
                                "top_k": top_k,
                                "stream": False
                            })
        result = res.json()['choices'][0]['message']['content']
        return result
        
    def chat2(self,seed,preprompt,prompt,max_tokens,min_tokens,temperature,top_p,top_k):
        res = requests.post(self.LLMendpoint+'/v1/chat/completions', 
                            json={
                                "messages": [
                                {
                                    "role": "system",
                                    "content": preprompt
                                    },
                                {
                                    "role": "user",
                                    "content": prompt
                                    }
                                ],
                                "mode": "instruct",
                                "max_tokens": max_tokens,
                                "min_tokens": min_tokens,
                                "temperature": temperature,
                                "top_p": top_p,
                                "seed": seed,
                                "top_k": top_k,
                                "stream": False
                            })
        result = res.json()['choices'][0]['message']['content']
        return result

    def gameChat(self, seed, messages, max_tokens, min_tokens, temperature, top_p, top_k):
        res = requests.post(self.LLMendpoint + '/v1/chat/completions', 
                            json={
                                "messages": messages,
                                "mode": "instruct",
                                "max_tokens": max_tokens,
                                "min_tokens": min_tokens,
                                "temperature": temperature,
                                "top_p": top_p,
                                "seed": seed,
                                "top_k": top_k,
                                "stream": False
                            })
        print(messages)

        if res.status_code != 200:
            print(f"Error: Status Code {res.status_code}")
            print(f"Response Text: {res.text}")
            return "Sorry, I couldn't process your request."

        try:
            result = res.json()['choices'][0]['message']['content']
        except (KeyError, IndexError, ValueError) as e:
            print(f"Response parsing error: {e}")
            return "Sorry, there was an error processing the response."

        return result

    def completion(self,seed,prompt,max_tokens,min_tokens,temperature,top_p,top_k):
        res = requests.post(self.LLMendpoint+'/v1/completions', 
                            json={
                                "prompt": prompt,
                                "mode": "instruct",
                                "max_tokens": max_tokens,
                                "min_tokens": min_tokens,
                                "temperature": temperature,
                                "top_p": top_p,
                                "seed": seed,
                                "top_k": top_k,
                                "stream": False
                            })
        result = res.json()['choices'][0]['text']
        return result

    def embeddings(self,content): # Requires oobabooga addition: pip install sentence-transformers (in conda activate installer-files/env)
        res = requests.post(self.LLMendpoint+'/v1/embeddings', 
                            json={
                                "input": content
                            })
        if res.status_code == 200:
            result = res.json()['data'][0]['embedding']
            # print(result) # prints embedding vectors
            return result
        else:
            print(f"Request failed with status code {res.status_code}")
            print(f"Request failed with status code {res.text}")

    def SDRender(self,seed,prompt,negprompt,steps,cfg_scale,width,height,sampler_name): # TODO - Refactor
        payload = {
            "prompt": prompt,
            "negative_prompt": negprompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "sampler_name": sampler_name,
            "seed": seed
        }
        res = requests.post(self.SDendpoint+'/sdapi/v1/txt2img', json=payload)
        result = res.json()
        return result
        
    def send_image_to_stable_diffusion(self,seed,image_path,prompt,negprompt,steps,cfg_scale,strength,width,height,sampler_name):
        api_url = self.SDendpoint+'/sdapi/v1/img2img'
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        payload = {
            "seed": seed,  
            "init_images": [image_data],
            "prompt": prompt,
            "negative_prompt": negprompt,
            "steps": 50,
            "cfg_scale": cfg_scale,
            "strength": strength, 
            "width": width,
            "height": height,
            "sampler_name": sampler_name
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_data = response.json()
        processed_image_data = response_data['images'][0]
        return processed_image_data
        
    def upscale(self,image_path,upscaler_name,factor=2):
        api_url = self.SDendpoint+'/sdapi/v1/extra-single-image'
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        payload = {
            "resize_mode": 0,
            "show_extras_results": True,
            "gfpgan_visibility": 0,
            "codeformer_visibility": 0,
            "codeformer_weight": 0,
            "upscaling_resize": 1.5,
            "upscaling_crop": False,
            "upscaler_1": upscaler_name,
            "upscaler_2": "None",
            "extras_upscaler_2_visibility": 0,
            "upscale_first": False,
            "image": image_data
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_data = response.json()
        processed_image_data = response_data['image']
        return processed_image_data

    def save_image(self,base64_image_data, original_path,suffix):
        dir_name, file_name = os.path.split(original_path)
        name, ext = os.path.splitext(file_name)
        new_file_name = f"{name}"+suffix+f"{ext}"
        new_file_path = os.path.join(dir_name, new_file_name)
        image_data = base64.b64decode(base64_image_data)
        with open(new_file_path, 'wb') as new_file:
            new_file.write(image_data)
        return new_file_path
        
    def send_data_to_stable_diffusion(self,seed,image_data,prompt,negprompt,steps,cfg_scale,strength,width,height,sampler_name):
        api_url = self.SDendpoint+'/sdapi/v1/img2img'
        payload = {
            "seed": seed,  
            "init_images": [image_data],
            "prompt": prompt,
            "negative_prompt": negprompt,
            "steps": 50,
            "cfg_scale": cfg_scale,
            "strength": strength, 
            "width": width,
            "height": height,
            "sampler_name": sampler_name
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        response_data = response.json()
        processed_image_data = response_data['images'][0]
        return processed_image_data
