# RogueGen
[![Demo on Youtube](https://img.youtube.com/vi/A0NcyUApxUw/0.jpg)](https://www.youtube.com/watch?v=A0NcyUApxUw)
Click to watch on youtube
## What's this?
This repository is the result of an exploration providing GPT4.o to a non-developer in pursuit of 'developing' a game. In this exploration, the goal was to develop a game without editor, which procedurally generates all assets by leveraging 
1) A locally hosted LLM - for generation of character context (llama2-13b-orca-8k-3319 - on huggingface).
2) Stable diffusion 1.5 - for associated graphical assets with Stable diffusion (1.5 - model Lascivious v2 on CivitAI).

## Getting started
### Pre-requisites:
Hardware (GPU):
- Any Nvidia graphics card of 3rd generation or later: (i.e. 3060 Ti 12gb vram)
Succesful installation of:
- Python 3.12.2 --> ensure it's properly set in environment variables/PATH
- Stable diffusion 1.5 --> A1111 worked for me
- Oobabooga --> any LLM host should do as long as it has API endpoints for 'chat', 'completion' and 'embeddings'. 
- Cuda toolkit --> saves you a lot of time! Be sure to checkout which specific version your installation of stable diffusion requires.

### Installation
#### Cloning & configuration
- open cmd, type ```git clone https://github.com/wynandhuizinga/RogueGen.git```
- in CMD: ```cd RogueGen```
- open Settings.py and update:
	- number_of_generations --> recommend to start with 3
	- LLMendpoint --> ensure endpoint is available prior to first run
	- SDendpoint --> ensure endpoint is available prior to first run
	After one generation you can also update playDirectory to 'replay' same seed and skip the 3hr generation process. Leave blank for first run. 

#### Installation
- in CMD: ```python -m venv venv```
	- activate it: ```.\venv\Scripts\activate```
- in CMD (venv): ```pip install -r requirements.txt``` --> can take a few minutes
- in CMD (venv): ```pip install requests Pillow numpy opencv-python pygame``` --> had to split it out - suggestions welcome.
- in CMD (venv): ```python game.py``` -> this should trigger first character generation, then player generation, and eventually launch the game. 

## Result
The result is a seeded game which takes forever to load (2-3 hours easily), but does provide a new experience each run. Although no story elements have been implemented this far, characters do generate their own back stories, avatars and appearances. Each character adds a set of guns to the game which can be purchased and upgraded. In game, characters can also converse based on their 'generated' emotions. It's by no means perfect, but it can certainly be enhanced and empowered with new prompt engineering, additional conversation history context tracking and by using different LLMs. 

One observation which surprized me most was that although some pieces of code came out absolutely horrible, others where surprisingly complex and efficient. This repository definitely has code repetitions which are far from ideal. 

## 'Development' process
The process of 'development' consisted for approximately 95% prompting. The remaining 5% was coded by leveraging knowledge adopted along the way, and simple adjustments. The initial prompts started out super basic requesting for a topdown python game where a character could run around. Subsequently, that code base would be inserted into a new prompt with additional requests for extensions. Due to limitations of context, it was sometimes required to selectively leave out certain methods/fields/entire classes. 

## Conclusions
Being an IT consultant, it is relevant for me to stay updated with potential in organizational changes. What can an existing workforce do in 2025 to increase efficiency. In this exploration, I've chosen to assess game development as games can be tedious to build. Game development is more than what's required when compairing it to simpler applications: i.e. an app which allows a resource to automate parts of his job in analysing / filtering textual data generating a small report.

I strongly recommend anyone to start building apps as it may help internal communication in an organization. It can help speed up your day-to-day tasks. Do however note that at this moment your generated apps shouldn't be put to use for critical business processes without a proper software development lifecycle to address proper maintenance & support processes. 





