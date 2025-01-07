
class PromptVault():
        
    def namePrompt(selected_style):
        return "Give me a fictive new name (first name + family name) for my new female " + selected_style + " character. Answer with only the name"
    
    def namePrePrompt():
        return "You are a generator of fictive names, When being asked for a name, you respond merely a name without any fillers or explanations"
    
    def specializationPrompt(selected_style):
        return "A fictive female " + selected_style + " character is expertly specialized in: "
    
    def descriptionPrompt(selected_style, name_response):
        return "For a fictive female " + selected_style + " character named " + name_response + ", provide a verbose imaginitive description of her clothing from top to bottom: physical features, hair color, race, eyes, occupation, gender, etc."
    
    def descriptionPrePrompt():
        return "Without introduction or defining context, you respond by merely providing a comma separated list of clothing items and physical appearances of requested character. You list all clothing items inspired on the context provided by user. You describe all clothes worn above the knees in full details zooming into details such as buttons, zippers, pockets, apparel, glasses, earrings, hairstyle and more."
    
    def interactionPrompt(specialization_response, name_response,chosen_mood):
        return "Describe how " + name_response + " engages in a first conversation. "+name_response+"'s mood is "+chosen_mood+". Be verbose about physical movements and behavior. Pay attention to the character's specialization as: " +specialization_response+ "."
    
    def interactionPrePrompt():
        return "You describe a character's way of behavior. You describe events taking place as a narrator. Incorporate the character's mood in the description. Describe the context in which it happens."
    
    def personalityPrompt(description_response):
        return "Provide me personality traits of the following character: \n" + description_response + ", \n Answer consisely with only 5 comma separated keywords of her personality traits"
    
    def personalityPrePrompt():
        return "You answer consisely with a list of exactly 5 character traits only. No introductions or explanations."
    
    def scenarioPrompt(name_response, selected_style, SceneryFilter):
        return "Provide me description of a fictive scenenery where I run into a character named" + name_response + ". " +name_response +" is a " + selected_style +". Exclude usage of environments: "+SceneryFilter+". Be elaborate about the environmental details"
    
    def scenarioPrePrompt():
        return "You solely describe an engagement between 2 characters inspired on given context. You narrate the environment, and set a scene which forces the 2 characters to engage with each other. Verbosely describe the engagement and their first interaction with each other."
    
    def greetingPrompt(scenario_response_final, first_name, chosen_style, chosen_mood):
        return "Inspired on the following smut scenario: \n\n" + scenario_response_final + "\n\nNarrate verbosely how " + first_name + " leverages aspects as " + chosen_style + " to engage with me. Elaborately incorporate the character's "+chosen_mood+" mood."
    
    def greetingPrePrompt():
        return "You are the character from the provided context. *You solely describe an engagement between the 2 characters in between asterisks*. *You narrate the environment*. \"You greet user from the characters's perspective.\" *You describe how you instigate engagement and or interaction with the user"
    
    def tauntPrompt(combined_description, chosen_style):
        return "'''" + combined_description + "'''\n\nI'm playing a game with a character from above description, the character taunts me during a competitive game. Inspired on the character's style as "+chosen_style+". Here are 10 examples (quotes) of I'm being taunted: \n\n- \"Bring it on boy, have you never played with a "+chosen_style+" before?\"\n- \"I'm gonna beat you, no one beats a "+chosen_style+"\"\n- "
    
    def bullyPrompt(combined_description, chosen_style):
        return "'''" + combined_description + "'''\n\nI'm playing a game with a character from above description. Inspired on her style as "+chosen_style+", the character bullies me. Here are 10 examples (quotes) of how she insults me are: \n\n- \"You're pathetic, never seen a "+chosen_style+"?\"\n- \"I will teabag you gently if you give up already...\"\n- "
    
    def stakeRaisePrompt(combined_description, chosen_style):
        return "'''" + combined_description + "'''\n\nI'm playing a game with a character in the above description. In order to make me take risks, the character provokes me. Here are 10 examples (quotes) of how provocation is applied to me: \n\n- \"If you outplay me quickly, I'll double the reward!\"\n- "
    
    def sdprepPrompt(description_response, first_name):
        return "Analyse following context: \n\"" + description_response + "\"\n\nSummarize "+first_name+"'s what clothing items is the character wearing on its upper body, include details on fastening (zipper, buttons), apparel, hair color,  eyes. Answer by providing approximately 6 items seperated by commas."
    
    def sdprepPrePrompt():
        return "You solely sum up lists of physical descriptions from character provided in context consisely. You reference features above knees. For example: \"short leather skirt, jeans, buttoned office shirt, blond hairbun, blue eyes, large earrings, medal on chest, scar on neck.\" Never mention footwear"
    
    def sdrenderPrompt(SD_prompt_subj_response_final,race,color,chosen_mood,chosen_style):
        return "high resolution cinematic still, ((photo-realistic)), (close-up) masterpiece, high resolution, RAW, ("+chosen_mood+") face, ("+chosen_style+") outfit, ("+ race +"), "+ SD_prompt_subj_response_final + ", ("+color+") colored clothes, detailed, professional, unreal engine, photo-realistic, HD, 8K, soft lighting, lifelike texture, by Agnes Cecile"
    
    def sdrenderPromptNeg():
        return "(worst_quality), (low_quality), lowres, kid, cartoon, (disfigured), illustration, painting, fused fingers, long neck, malformed limbs, mutated hands, malformed hands, watermark, distorted hands, grayscale, monochrome, aberrations, filmgrain, high ISO, bikini, bra, naked, nude"
        
    def sdrenderBeatenPrompt(race,chosen_style):
        return "high resolution cinematic still, ((photo-realistic)), (close-up) masterpiece, high resolution, RAW, exhausted beaten face, sweating, damaged ("+chosen_style+") outfit, ((bruised)), ((punched)) ("+ race +") face, torn clothes, detailed, professional, unreal engine, photo-realistic, HD, 8K, soft lighting, lifelike texture, by Agnes Cecile"
        
    def sdrenderBeatenNegPrompt():
        return "(worst_quality), (low_quality), lowres, kid, cartoon, (disfigured), illustration, painting, fused fingers, long neck, malformed limbs, mutated hands, malformed hands, watermark, distorted hands, grayscale, monochrome, aberrations, filmgrain, high ISO, clothes, wearing, shirt, top, bra"
        
    def sdrenderWetPrompt(race,chosen_mood, chosen_style):
        return "high resolution cinematic still, ((photo-realistic)), (close-up) masterpiece, high resolution, RAW, soaking wet face, (("+ chosen_mood +")) expression, wet ("+chosen_style+") outfit, ("+ race +"), soaking wet clothes, wet hair, water droplets, detailed, professional, unreal engine, photo-realistic, HD, 8K, soft lighting, lifelike texture, by Agnes Cecile"
        
    def sdrenderRegularPrompt(race,chosen_mood,chosen_style):
        return "high resolution cinematic still, ((photo-realistic)), (close-up) masterpiece, high resolution, RAW,  (("+ chosen_mood +")) face, ("+chosen_style+") outfit, ("+ race +"), nurtured skin, nourished, pores, healthy, detailed, professional, unreal engine, photo-realistic, HD, 8K, soft lighting, lifelike texture, by Agnes Cecile"
        
    def sdrenderWetNegPrompt():
        return "(worst_quality), (low_quality), lowres, kid, cartoon, (disfigured), illustration, painting, fused fingers, long neck, malformed limbs, mutated hands, malformed hands, watermark, distorted hands, grayscale, monochrome, aberrations, filmgrain, high ISO, bikini, bra, naked, nude"
    
    def sdrenderBackgroundPrep(scenario_response_final):
        return scenario_response_final + "\n\nGiven the above scenario, the environment of the scenario takes place in a \""
    
    def sdrenderBackground(SD_BG_prompt_subj_response_final):
        return "((photo-realistic)) texture, high resolution, RAW, A texture of a flat (((Wall))), ("+SD_BG_prompt_subj_response_final+") with ((props)), detailed, professional photography, unreal engine, photo-realistic, HD, 8K, soft lighting, lifelike texture"
    
    def sdrenderBackground2(SD_BG_prompt_subj_response_final):
        return "((photo-realistic)) texture, high resolution, RAW, ("+SD_BG_prompt_subj_response_final+") with ((props)), detailed, professional photography, unreal engine, photo-realistic, HD, 8K, soft lighting, lifelike texture"
        
    def sdrenderBackgroundNeg():
        return "(worst_quality), (low_quality), lowres, girl, boy, ((human)), ((individual)), people, person, (man), (woman), kid, cartoon, (disfigured), illustration, painting, watermark, hands, legs, eyes, nose, hair, grayscale, monochrome, aberrations, filmgrain, high ISO, depth, perspective"
    # upscale.
    def sdrenderBGUpscale():
        return "((photo-realistic)) texture, high resolution, RAW, NEF, lyca, intricate details, professional photography, EOS mark IV, unreal engine, high quality photo, HD, 8K, soft lighting, lifelike texture"
        
    def sdrenderBGUpscaleNeg():
        return "(worst_quality), (low_quality), lowres, cartoon, illustration, painting, watermark, grayscale, monochrome, aberrations, filmgrain, high ISO"
        
    def sdrenderRegularNegPrompt():
        return "(worst_quality), (low_quality), lowres, kid, cartoon, (disfigured), illustration, painting, fused fingers, long neck, malformed limbs, mutated hands, malformed hands, watermark, distorted hands, grayscale, monochrome, aberrations, filmgrain, high ISO, bikini, bra, naked, nude"
    
    def yesNoValPrompt(response):
        return "Is the following text summing up attributes of somebody's visual appearance?\n\n"+response+"\n\nAnswer only with YES or NO"
    
    def propsQuery(SD_BG_prompt):
        return "Environment description:\n\n" +SD_BG_prompt + "\n\nGiven the above environment, a list of cinema props (keywords+object size+breakability+explanation why breaks when walking over it) placed in such an environment would be: \n- (chair, medium, unbreakable, made out of hard wood)\n- (plant, small, breakable, made out of fragile materials)\n- (table, large, unbreakable, made out of steel) \n-"
        
    def propSpriteSDPrompt(prop,fav_color): # TODO - substitute red for favorite color of character
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of a "+fav_color+" (("+prop+")), against a ((black-background)), nintendo, 16-bit, HD, 8K, texture"
    
    def propSpriteSDPromptNeg():
        return "watermark, grayscale, monochrome, noise, stem, borders, ground, edges, ((frame))"
        
    def playerFace(playersubject):
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of the (((face))) of a "+playersubject+", ((facing viewer)), armpits, arms, shoulders, against a ((black-background)), nintendo, 16-bit, HD, 8K, texture"
        
    def playerFaceSide(playersubject):
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of the (((face))) of a "+playersubject+", ((facing side)), armpits, arms, shoulders, against a ((black-background)), nintendo, 16-bit, HD, 8K, texture"
        
    def playerFaceNeg():
        return "watermark, grayscale, monochrome, noise, stem, borders, ground, edges, ((frame)), (((face))), legs, neck, nose, eyes, eyebrows, mouth"
        
    def playerBody(playercolor, playersubject):
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of the (((upper body))) of a "+playercolor+" "+playersubject+", ((facing viewer)), armpits, arms, shoulders, against a ((black-background)), nintendo, 16-bit, HD, 8K, texture"

    def playerBodyNeg():
        return "watermark, grayscale, monochrome, noise, stem, borders, ground, edges, ((frame)), (((((face))))), legs, neck, nose, eyes, eyebrows, mouth"
        
    def playerBodyMove(playercolor, playersubject):
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of the (((upper body))) of a "+playercolor+" "+playersubject+", ((sideways)), arms, shoulders, against a ((black-background)), nintendo, 16-bit, HD, 8K, texture"

    def playerLegs(playercolor, playersubject):
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of the (((legs))), (((shoes))) of a "+playercolor+" "+playersubject+", pants, shins, thigh, crotch, shoes, against a ((black-background)), nintendo, 16-bit, HD, 8K, texture"

    def playerLegsNeg():
        return "watermark, grayscale, monochrome, noise, stem, borders, edges, ((frame)), (((face))), (chest), arms, neck, nose, (((eyes))), hair, eyebrows, mouth"

    def attackHalo(playercolor):
        return "colorful light blue Magic particles funky, fiery, fantasy, photo realistic"

    def projectile(playercolor,element):
        return "colorful ((single)) "+playercolor+" (("+element+" projectile)), funky, fiery, fantasy, photo realistic, against black background"

    def projectileNeg():
        return "reflections"

    def splash(element,splash):
        return "single ("+element+") "+splash+", photo realistic, against black background"

    def splashEvo(element,splash):
        return "single ("+element+") "+splash+", particles photo realistic, against black background"

    def splashNeg():
        return "reflections, text"

    # Todo, take noise pattern, add black edge around it, send to SD, capture and add another black thin edge over it. dark Graywash 20% 
    def floorMaterial(style,scenario):
        return "Given a character which is a "+style+" walking around in the following environment:\n"+scenario+".\n\nShe walks on a floor with a material made of "
        
    def element(first_name,chosen_style,personality_response_final,description_response_final,specialization_response_final):
        return first_name+" is a "+chosen_style+" specialized in "+specialization_response_final+" with personality: "+personality_response_final+", and looks: "+description_response_final+". If "+first_name+" were to be in a fantasy world with magical powers, her favorite element for casting spells would be the element of"
        
    def explosion(elemental_final):
        return "In a fantasy novel, a detonation from magical bolt of element "+elemental_final+" would visually appear as \n1) a "
        
    def floor(material):
        return "pixel-art, diamond painting, mosaic, ((2d)), sprite, masterpiece, low resolution, illustration, drawing, graphic, painting, image of "+material+" (((floor-tile))), ground, symmetrical, fractal, nintendo, 16-bit, HD, 8K, texture"

    def floorNeg():
        return "reflections, watermark, text, signature, header, people, person, individual, man, woman, girl, boy"
        
    def explosionRender():
        return "A powerful explosion"
        
    def explosionRenderNeg():
        return "watermark, horizon, text, signature, header"
        
    def healthBar():
        return "high resolution, 8k, photo realistic Illustration, (underwater deep sea, blue background) , teal air bubbles, intricate details"
        
    def healthBarNeg():
        return "text, lowres, fish"
        
    def crosshair(color):
        return "intricate details, symmetrical gold "+color+" crosshair, against a black background"
        
    def crosshairNeg():
        return "text, lowres"
        
    def pitTrap():
        return "high resolution, masterpiece, illustration, (((2D))) ((aerial view)),floor texture of a square ((spike trap)), pit ,detailed, professional, unreal engine, photo-realistic, HD, 8K, lifelike texture, nintendo"
        
    def pitTrapNeg():
        return "(worst_quality), (low_quality), (watermark), (text), (signature), (footer), lowres, person, people, individual, man, woman, grayscale, monochrome, aberrations, filmgrain, high ISO, perspective, isometric, 3D"
        
    def gunPrompt(guntype):
        return "high resolution, masterpiece, (((2D))) ((side view)), [black background: horizontal ("+guntype+") on ((black display)), "+guntype+"vault: 2 ], detailed, professional, unreal engine, photo-realistic, HD, 8K, lifelike texture"
        
    def gunPromptNeg():
        return "(worst_quality), (low_quality), (watermark), (text), (signature), person, human, perspective, drop shadow, (gradient), (backdrop)"
        
    def gunUpgradePrompt(color,guntype): 
        return "((intricate details)), futuristic, photorealism, alien, brightly "+color+" {((vains))|LED lighting}, ((spotlighting)), fireworks, lamps, beam of light, ((reflective metal)), Metalworks, chrome, ((("+guntype+"))). high resolution, masterpiece, (((2D))) ((side view)), horizontal ("+guntype+") on ((black display)), "+guntype+"vault, detailed, professional, unreal engine, photo-realistic, HD, 8K, lifelike texture"
        
    def gunUpgradePromptNeg():
        return "(worst_quality), (low_quality)"
