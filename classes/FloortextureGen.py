import numpy as np
from PIL import Image, ImageOps
import requests
import random
import json
import base64
import os
import io
from classes.Settings import API_SETTINGS
from classes.APICallHandler import APICallHandler

api_handler = APICallHandler(API_SETTINGS)

class FloortextureGen():
    def __init__(self,path,seed=random.randint(0,10000),iteration=0, char_type='player', color_str=str((random.randint(0,255),random.randint(0,255),random.randint(0,255))), floormaterial="wood"):
        self.alpha_img_path = './templates/biggerframe.png'
        self.final_alpha_img_path = './templates/lightframe.png'
        random.seed(seed)
        self.seed = seed
        self.path = path
        self.char_type = char_type
        self.iteration=iteration
        self.color = tuple(map(int, color_str.replace('(','').replace(')','').split(',')))

    def create_noise_pattern(self, size=(512, 512)):
        noise = np.random.rand(*size, 3) * 255
        noise_img = Image.fromarray(noise.astype('uint8')).convert('RGBA')
        return noise_img

    def apply_color_wash(self, img, color, intensity=0.35):
        color_layer = Image.new('RGBA', img.size, color)
        blended = Image.blend(img, color_layer, intensity)
        return blended

    def combine_with_alpha(self, img, alpha_img_path):
        alpha_img = Image.open(alpha_img_path).convert('RGBA')
        combined = Image.alpha_composite(img, alpha_img)
        return combined

    def process_image(self, seed, prompt, negprompt, steps, cfg_scale, strength, width, height, sampler_name):
        player_image_data = {}
        player_image_data['floor_tile_data'] = []
        
        for i in range(1,11):
            noise_img = self.create_noise_pattern()
            color_wash_img = self.apply_color_wash(noise_img, self.color)
            combined_img = self.combine_with_alpha(color_wash_img, self.alpha_img_path)
            
            buffer = io.BytesIO()
            combined_img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            processed_image_data = api_handler.send_data_to_stable_diffusion(seed+i, img_str, prompt, negprompt, steps, cfg_scale, strength, width, height, sampler_name)
            
            processed_image_data_decoded = base64.b64decode(processed_image_data)
            processed_image = Image.open(io.BytesIO(processed_image_data_decoded)).convert('RGBA')
                        
            final_alpha_img = Image.open(self.final_alpha_img_path).convert('RGBA')
            final_combined_img = Image.alpha_composite(processed_image, final_alpha_img)
            
            downsized = final_combined_img.resize((64, 64), Image.Resampling.LANCZOS)
            
            #washed = self.apply_color_wash(downsized, (255,255,255),intensity=0.50)
            washed = self.apply_color_wash(downsized, (50,50,50),intensity=0.20)

            final_buffered = io.BytesIO()
            washed.save(final_buffered, format="PNG")
            final_img_str = base64.b64encode(final_buffered.getvalue()).decode("utf-8")
            
            player_image_data['floor_tile_data'].append(final_img_str)
                    
            final_image_path = api_handler.save_image(final_img_str, self.path,f'{self.iteration} - {self.char_type}-floortexture{i}.png')
        
        return player_image_data

    def process_image_neutral(self, seed, prompt, negprompt, steps, cfg_scale, strength, width, height, sampler_name):
        player_image_data = {}
        player_image_data['floor_tile_data'] = []
        for i in range(1,11):
            noise_img = self.create_noise_pattern()
            color_wash_img = self.apply_color_wash(noise_img, self.color)
            combined_img = self.combine_with_alpha(color_wash_img, self.alpha_img_path)
            
            buffer = io.BytesIO()
            combined_img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            processed_image_data = api_handler.send_data_to_stable_diffusion(seed+i, img_str, prompt, negprompt, steps, cfg_scale, strength, width, height, sampler_name)
            
            processed_image_data_decoded = base64.b64decode(processed_image_data)
            processed_image = Image.open(io.BytesIO(processed_image_data_decoded)).convert('RGBA')
                        
            final_alpha_img = Image.open(self.final_alpha_img_path).convert('RGBA')
            final_combined_img = Image.alpha_composite(processed_image, final_alpha_img)
            
            downsized = final_combined_img.resize((64, 64), Image.Resampling.LANCZOS)
            
            #washed = self.apply_color_wash(downsized, (255,255,255),intensity=0.60)
            washed = self.apply_color_wash(downsized, (50,50,50),intensity=0.35)

            final_buffered = io.BytesIO()
            washed.save(final_buffered, format="PNG")
            final_img_str = base64.b64encode(final_buffered.getvalue()).decode("utf-8")
            
            player_image_data['floor_tile_data'].append(final_img_str)
                    
            final_image_path = api_handler.save_image(final_img_str, self.path,f'neutral-floortexture{i}.png')
            
        return player_image_data
