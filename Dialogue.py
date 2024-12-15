import pygame
import random
import textwrap
import base64
import json
from Settings import *
from APICallHandler import APICallHandler
from io import BytesIO
import io
from PIL import Image

api_handler = APICallHandler(API_SETTINGS)

class Dialogue():
    def __init__(self, seed, screen, FPS, clock):
        self.screen = screen
        self.FPS = FPS
        self.clock = clock
        self.seed = seed
        self.message_number = 0
        self.spend = 0

    def dialogue(self, conversingEnemy, player, gun_list):
        input_text = ''
        
        chat_history = [
            {"role": "system", "content": conversingEnemy.jsondata['scenario'] + ". You are a " + conversingEnemy.jsondata['CharGen_data']['selected_style'] + "."},
            {"role": "assistant", "content": random.choice(conversingEnemy.jsondata['CharGen_data']['taunts'])}
        ]

        scroll_offset = 0
        run = True
        line_spacing = 1
        backspace_timer = 0
        backspace_interval = 30
        player.credits += 2000 # TODO - Remove
        print("player gets additional free 100 moneys, new balance: ", player.credits) # TODO - Remove

        while run:
            self.clock.tick(self.FPS)
            self.screen.fill((0, 0, 0))
            chat_box_width = self.screen.get_width() // 3
            chat_box_height = self.screen.get_height() * 4 // 5
            chat_box_x = (self.screen.get_width() - chat_box_width) // 2
            chat_box_y = (self.screen.get_height() - chat_box_height) // 2

            max_width = chat_box_width - 20
            y_offset = chat_box_y + 10 + scroll_offset

            # Calculate the total height of the chat history
            total_height = 0
            for message in chat_history:
                if message['role'] == "user":
                    total_height += self.draw_text(f"You: {message['content']}", 25, chat_box_x + 10, 0, max_width, (255, 255, 255), "right", line_spacing) + 10
                elif message['role'] == "assistant":
                    total_height += self.draw_text(f"{conversingEnemy.jsondata['name']}: {message['content']}", 25, chat_box_x + 10, 0, max_width, (255, 100, 100), "left", line_spacing) + 10
                else:
                    height = 0
            pygame.draw.rect(self.screen, (50, 50, 50), (chat_box_x, chat_box_y, chat_box_width, chat_box_height))

            # Display chat history
            y_offset = chat_box_y + 10 + scroll_offset
            for message in chat_history:
                if message['role'] == "user":
                    height = self.draw_text(f"You: {message['content']}", 25, chat_box_x + 10, y_offset, max_width, (255, 255, 255), "right", line_spacing)
                elif message['role'] == "assistant":
                    height = self.draw_text(f"{conversingEnemy.jsondata['name']}: {message['content']}", 25, chat_box_x + 10, y_offset, max_width, (255, 100, 100), "left", line_spacing)
                y_offset += height + 10  # Adjust based on font size and line height

            scroll_offset = min(0, max(scroll_offset, chat_box_height - total_height - 20))

            input_lines = textwrap.wrap('You: ' + input_text, width=max_width // 15)
            for i, line in enumerate(input_lines):
                self.draw_text(line, 25, chat_box_x + 10, chat_box_y + chat_box_height - 40 * (len(input_lines) - i), max_width, (255, 255, 255), "right", line_spacing)

            pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.screen.get_width(), chat_box_y))
            pygame.draw.rect(self.screen, (0, 0, 0), (0, chat_box_y + chat_box_height, self.screen.get_width(), self.screen.get_height() - (chat_box_y + chat_box_height)))

            self.draw_text('Press Enter to send', 30, self.screen.get_width() // 3, self.screen.get_height() - 50, max_width, (255, 255, 255), "right", line_spacing)
            
            self.draw_text('ESC to exit', 30, 40, 40, max_width, (255, 255, 255), "left", line_spacing)
            self.draw_text('Tilde to open shop', 30, 40, 70, max_width, (255, 255, 255), "left", line_spacing)

            
            if self.spend > 1000:
                conversingEnemy.draw_character_won()
            elif self.spend > 500:
                conversingEnemy.draw_character_wet()
            else:
                conversingEnemy.draw_character()
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    self.state = "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        return "common_area", player, gun_list
                    elif event.key == pygame.K_RETURN:
                        user_message = {"role": "user", "content": input_text}
                        chat_history.append(user_message)
                        response_text = api_handler.gameChat(self.seed + self.message_number, chat_history, 100, 4, 0.9, 0.9, 50)
                        self.message_number += 1
                        assistant_message = {"role": "assistant", "content": response_text}
                        chat_history.append(assistant_message)
                        input_text = ''
                        total_height = sum(self.draw_text(f"{msg['role']}: {msg['content']}", 25, 0, 0, max_width, (255, 255, 255), "right", line_spacing) + 10 for msg in chat_history)
                        scroll_offset = min(0, chat_box_height - total_height - 20)
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        backspace_timer = 10
                    elif event.key == pygame.K_UP:
                        scroll_offset = min(scroll_offset + 20, 0)
                    elif event.key == pygame.K_DOWN:
                        scroll_offset = max(scroll_offset - 20, min(chat_box_height - total_height - 20, 0))
                    elif event.key == pygame.K_PAGEUP:
                        scroll_offset = min(scroll_offset + chat_box_height, 0)
                    elif event.key == pygame.K_PAGEDOWN:
                        scroll_offset = max(scroll_offset - chat_box_height, min(chat_box_height - total_height - 20, 0))
                    elif event.key == pygame.K_BACKQUOTE:
                        print("hit")
                        gun_list = self.open_shop(conversingEnemy, player, gun_list)
                    else:
                        input_text += event.unicode

                if event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE:
                    backspace_timer = 0

            if backspace_timer > 0:
                if backspace_timer % backspace_interval == 0:
                    input_text = input_text[:-1]
                backspace_timer += 1
            pygame.display.update()

    def draw_text(self, text, size, x, y, max_width=700, color=(255, 255, 255), align="left", line_spacing=5):
        font = pygame.font.Font(None, size)
        wrapped_text = textwrap.wrap(text, width=max_width // (size // 2))
        total_height = len(wrapped_text) * (size + line_spacing)

        for i, line in enumerate(wrapped_text):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect()
            if align == "right":
                text_rect.topright = (x + max_width, y + i * (size + line_spacing))
            else:
                text_rect.topleft = (x, y + i * (size + line_spacing))
            self.screen.blit(text_surface, text_rect)

        return total_height
                
    def open_shop(self, conversingEnemy, player, gun_list):
        run = True
        selected_gun_index = 0
        scroll_offset = 0
        item_height = 150
        temp_counter = 0
        gun_image = None

        while run:
            self.clock.tick(self.FPS)
            self.screen.fill((0, 0, 0))
            y_offset = 50 + scroll_offset

            for i, gun in enumerate(gun_list):

                if y_offset < self.screen.get_height() + 150 and y_offset >  -150:                        
                    gun_image_data = gun['base_gun_image_data'] if not gun['upgraded'] else gun['upgraded_gun_image_data']
                    gun_image_bytes = base64.b64decode(gun_image_data)
                    gun_image = pygame.image.load(io.BytesIO(gun_image_bytes)).convert_alpha()                                
                    width = item_height / gun_image.get_height() * gun_image.get_width()
                    gun_image = pygame.transform.scale(gun_image, (width, item_height))
                    self.screen.blit(gun_image, (-100, y_offset))
                else:
                    gun_image = None
                if i == selected_gun_index:
                    pygame.draw.rect(self.screen, (255, 255, 255), (20, y_offset, 660, 150), 3)
                if not gun['owned']:
                    self.draw_text(f"{gun['category']} - not owned - {gun['price']} credits", 20, 260, y_offset + 120, max_width=400, color=(170, 170, 170), align="right")
                elif gun['owned'] and not gun['upgraded']:
                    self.draw_text(f"{gun['category']} - upgradable - {gun['price']} credits", 20, 260, y_offset + 120, max_width=400, color=(255, 255, 110), align="right")
                else:
                    self.draw_text(f"{gun['category']} - Maxed!", 20, 260, y_offset + 120, max_width=400, color=(150, 255, 110), align="right")
                y_offset += item_height
            
            if temp_counter <= 0 or temp_counter == 2 or temp_counter == 4 or temp_counter == 6:
                self.draw_text(f"Wallet: $ {player.credits}", 40, self.screen.get_width()//2-320, 60, max_width=500, color=(170, 170, 255), align="right")
            else:
                self.draw_text(f"Wallet: $ {player.credits}", 40, self.screen.get_width()//2-320, 60, max_width=500, color=(255, 50, 50), align="right")
            if temp_counter > -1:            
                temp_counter -= 1
            
            if self.spend > 1000:
                conversingEnemy.draw_character_won()
            elif self.spend > 500:
                conversingEnemy.draw_character_wet()
            else:
                conversingEnemy.draw_character()
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    self.state = "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        return gun_list
                    elif event.key == pygame.K_w:
                        if selected_gun_index > 0:
                            selected_gun_index -= 1
                            if selected_gun_index * item_height + scroll_offset < 0:
                                scroll_offset += item_height
                    elif event.key == pygame.K_s:
                        if selected_gun_index < len(gun_list) - 1:
                            selected_gun_index += 1
                            if (selected_gun_index + 1) * item_height + scroll_offset > self.screen.get_height():
                                scroll_offset -= item_height
                    elif event.key == pygame.K_RETURN:
                        gun = gun_list[selected_gun_index]
                        #category, idx, gun_image_data, rate_of_fire, damage, gun_upgrade_image_data, owned, upgraded, price = gun_list[selected_gun_index]
                        if not gun['owned'] and not gun['upgraded'] and player.credits >= gun['price']:
                            player.credits -= gun['price']
                            self.spend += gun['price']
                            gun_entry = {
                                    "category": gun['category'],
                                    "idx": gun['idx'],  # Use total_count as a unique index
                                    "base_gun_image_data": gun['base_gun_image_data'],
                                    "rate_of_fire": gun['rate_of_fire'],
                                    "damage": gun['damage'],
                                    "upgraded_gun_image_data": gun['upgraded_gun_image_data'],
                                    "owned": True,
                                    "upgraded": gun['upgraded'],
                                    "price": gun['price'] + gun['price']*random.randint(1,11) // 5,
                                    "base_projectile_data": gun['base_projectile_data'],
                                    "base_splash_data": gun['base_splash_data'],
                                    "upgraded_projectile_data": gun['upgraded_projectile_data'],
                                    "upgraded_splash_data": gun['upgraded_splash_data']
                                }
                            gun_list[selected_gun_index] = gun_entry# (category, idx, gun_image_data, rate_of_fire, damage, gun_upgrade_image_data, True, upgraded, price + price*random.randint(1,11) // 5)
                        elif not gun['upgraded'] and player.credits >= gun['price']:
                            player.credits -= gun['price']
                            self.spend += gun['price']
                            rate_of_fire = gun['rate_of_fire']
                            rate_of_fire -= 15
                            if rate_of_fire < 1:
                                rate_of_fire = 1
                            damage = gun['damage']
                            damage += random.randint(1,16)
                            gun_entry = {
                                    "category": gun['category'],
                                    "idx": gun['idx'],  # Use total_count as a unique index
                                    "base_gun_image_data": gun['base_gun_image_data'],
                                    "rate_of_fire": rate_of_fire,
                                    "damage": damage,
                                    "upgraded_gun_image_data": gun['upgraded_gun_image_data'],
                                    "owned": gun['owned'],
                                    "upgraded": True,
                                    "price": 0,
                                    "base_projectile_data": gun['base_projectile_data'],
                                    "base_splash_data": gun['base_splash_data'],
                                    "upgraded_projectile_data": gun['upgraded_projectile_data'],
                                    "upgraded_splash_data": gun['upgraded_splash_data']
                                }
                            gun_list[selected_gun_index] = gun_entry #(category, idx, gun_image_data, rate_of_fire, damage, gun_upgrade_image_data, owned, True, price)

                            trigger_reload = True
                        else:
                            temp_counter = 12 # too expensive blinker

    def decode_image(self, image_data):
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)