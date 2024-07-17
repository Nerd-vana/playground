import os
import google.generativeai as genai
#pip install -U google-generativeai


# Access your API key as an environment variable.
genai.configure(api_key=os.environ['API_KEY'])
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')

#prompt = "Translate to Taiwan traditional Chinese without pinyin.  'How are you today?'"
prompt = "Translate to French.  'October arrived, spreading a damp chill over the grounds and into the castle. Madam Pomfrey, the nurse, was kept busy by a sudden spate of colds among the staff and students. Her Pepperup potion worked instantly, though it left the drinker smoking at the ears for several hours afterward. Ginny Weasley, who had been looking pale, was bullied into taking some by Percy. The steam pouring from under her vivid hair gave the impression that her whole head was on fire.'"

prompt = "translate to English : 'Octobre arriva, répandant une fraîcheur humide sur les terrains et dans le château. Madame Pomfresh, l'infirmière, était débordée par une soudaine vague de rhumes parmi le personnel et les élèves. Sa potion Réchauffante agissait instantanément, bien qu'elle laissait le buveur fumer des oreilles pendant plusieurs heures après. Ginny Weasley, qui avait l'air pâle, fut forcée de prendre de la potion par Percy. La vapeur qui s'échappait sous ses cheveux vifs donnait l'impression que toute sa tête était en feu. '"

prompt = "Translate to French, German, Spanish, Walch, Irish, Vietnamese, Traditional Chinese, Japanese, Korean.  'How are you today?'"

response = model.generate_content(prompt)

print(response.text)

