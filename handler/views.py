from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.cache import never_cache
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
import requests
import os
import time
import pygame
from gtts import gTTS
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

translator = Translator()  
pygame.mixer.init()  

# Create a map 
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def translator_function(spoken_text, from_language, to_language):
    try:
        logger.debug(f"Translating: {spoken_text} from {from_language} to {to_language}")
        translation = translator.translate(spoken_text, src=from_language, dest=to_language)
        
        if translation is not None and hasattr(translation, 'text') and translation.text:
            translated_text = translation.text
            logger.debug(f"Translated Text: {translated_text}")
            return translated_text
        else:
            logger.error("Translation failed or empty response.")
            return None
    except Exception as e:
        logger.exception("Translation Error:")
        return None

def text_to_voice(text, language):
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("output.mp3")
        os.system("start output.mp3")  # Play audio
        return True
    except Exception as e:
        print("Error in text to speech conversion:", e)
        return False

# def text_to_voice(text, language):
#     try:
#         
#         output_dir = settings.BASE_DIR

#         
#         audio_file_path = os.path.join(output_dir, "output.mp3")

#        
#         tts = gTTS(text=text, lang=language, slow=False)
#         tts.save(audio_file_path)
#         # return HttpResponseRedirect(reverse('translate'))
#         
#         #response_data = {'success': True}
#         return redirect('translate')
#     except Exception as e:
#         print("Error in text to speech conversion:", e)
#         #response_data = {'success': False, 'error_message': str(e)}
    
#     #return JsonResponse(response_data)
def translate_view(request):
    languages = LANGUAGES.values()  # Retrieve languages 
    context = {'languages': languages}  # Pass languages 
     
    if request.method == 'POST':
        from_language_name = request.POST.get('from_language')
        to_language_name = request.POST.get('to_language')
        
        # Convert 
        from_language = get_language_code(from_language_name)
        to_language = get_language_code(to_language_name)

        # Translation
        rec = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            rec.pause_threshold = 1
            audio = rec.listen(source, phrase_time_limit=10)

        try:
            print("Processing...")
            spoken_text = rec.recognize_google(audio, language=from_language)
            
            print("Translating...")
            
            translated_text = translator_function(spoken_text, from_language, to_language)

            if translated_text:
                if text_to_voice(translated_text, to_language):
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'error': 'Text-to-speech conversion failed.'})
            else:
                return JsonResponse({'error': 'Translation failed.'})
        
        except Exception as e:
            print("Recognition Error:", e)
            return JsonResponse({'error': str(e)})
    
    else:
        return render(request, 'translate.html', context=context)