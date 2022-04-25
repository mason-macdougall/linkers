from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from datetime import date
import streamlit as st
from streamlit.components.v1 import iframe
import numpy as np
import pandas as pd
import json
from scipy import stats
from utils import *

limit = 20

st.set_page_config(layout="centered", page_icon="🔗", page_title="Linker UCLA")
st.title("Linker UCLA")

st.write(
    "Matching people based on personality!"
)

options = ["strongly disagree", "somewhat disagree", "neutral", "somewhat agree", "strongly agree"]

N_options = len(options)
options_dict = {}
for i, opt in enumerate(options):
    options_dict[opt] = i+1

form = st.form(key="annotation")

genders_list = ["", "female", "male", "non-binary", "gender-fluid", "transgender", "other"]
preference_list = ["anyone", "female", "male", "non-binary", "other"]
pronouns_list = ["", "she/her", "he/him", "they/them", "he/they", "she/they", "xie/xir", "ze/zir", "other"]
bio_default = "Let\'s link!"

genres_list = ['k-pop', 'pop', 'rock', 'alt', 'rap', 'hip hop', 'indie', 
               'country', 'r&b', 'latin', 'house', 'edm', 'punk', 'instrumental', 'other']
sports_list = ['running', 'hiking', 'lifting', 'swimming', 'soccer', 'basketball', 'baseball',
               'softball', 'football', 'tennis', 'cricket', 'badminton', 'climbing', 'kayaking', 
               'walking', 'martial arts', 'golf', 'hockey', 'gymnastics', 'gym', 'volleyball', 'other']

with form:
    cols1 = st.columns((1, 1))
    first = cols1[0].text_input("First:")
    last = cols1[1].text_input("Last:")

    cols2 = st.columns((1, 1))
    age = cols2[0].text_input("Age:")
    pronouns = cols2[1].selectbox(
        "Preferred pronouns:",
        pronouns_list,
        index=0,
    )

    cols3 = st.columns((1, 1))
    gender = cols3[0].selectbox(
        "Preferred gender:",
        genders_list,
        index=0,
    )
    preference = cols3[1].selectbox(
        "Preferred gender to link with (if any):",
        preference_list,
        index=0,
    )

    bio = st.text_input("Bio:", value=bio_default, max_chars=50)
    questions_df = pd.read_csv('questions.csv', delimiter='%')
    questions = questions_df.Questions.values

    answers = []
    skips = []

    cols4 = st.columns(2)
    music = cols4[0].multiselect(
         'What music genres are you into (if any)?',
         genres_list)
    skips += [cols4[1].checkbox("Skip music?", value=True)]*len(genres_list)

    cols5 = st.columns(2)
    sports = cols5[0].multiselect(
         'What sports or exercise are you into (if any)?',
         sports_list)
    skips += [cols5[1].checkbox("Skip sports?", value=True)]*len(sports_list)

    answers += get_multiselect_answers(music, genres_list)
    answers += get_multiselect_answers(sports, sports_list)

    for i, q in enumerate(questions):
        cols = st.columns(2)
        answers.append(cols[0].select_slider("Q"+str(i+1)+".  "+q, options=options, value="neutral"))
        skips.append(cols[1].checkbox("Skip Q"+str(i+1)+"?", value=True))

    submitted = st.form_submit_button(label="Get linked!")

if submitted: 

    with open('users.json') as json_file:
        users = json.load(json_file)
    json_file.close()

    answers_final = []
    for i, ans in enumerate(answers):
        if skips[i] == True:
            answers_final.append(np.nan)
        else:
            answers_final.append(options_dict[ans])

    current_user = {'user_0': {'name': {'first': first, 'last': last},
                  'age': age,
                  'gender': gender,
                  'pronouns': pronouns,
                  'preference': preference,
                  'public': True,
                  'bio': bio,
                  'answers': np.array(answers_final)}}

    if gender == 'male' and preference == 'female':
        preference = 'anyone'

    users = get_filtered(users, preference)
    top_final_scores, argsort_idx = get_top_scores(current_user, users, limit, N_options=N_options)
    top_profiles = get_top_profiles(users, argsort_idx, limit)
    profile_list = get_profile_list(top_profiles, top_final_scores)

    df = pd.DataFrame(profile_list).T
    df_display = df.reset_index().drop('index',axis=1).copy()

    st.subheader("Here are your strongest links 👇 ")
    st.text("")

    st.table(df_display)




#st.write("")
#st.write("")
#st.write("")
#st.write("")
#st.write(
#    r"DISCLAIMER: This is for reference and estimation purposes only. We\'re pretty sure the calculations are right, but you never know ¯\\\_(ツ)\_/¯"
#)
#st.write("")
#st.write("")
#st.write(
#    "To report a bug, email jobcompcalc@gmail.com with a description of the issue and we\'ll be sure to look into it!"
#)
