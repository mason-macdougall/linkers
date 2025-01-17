import pandas as pd
import numpy as np
from scipy import stats
from all_options import *

'''
Need to fix:

Need to fix the raw scores such that they reflect the total overlap of questions
Otherwise, fewer question overlap means lower score which is better - but incorrect

I answered all questions
John answered 1, which we match up on
John has the lowest score when matched up against mine
John needs to be penalized for having only answered 1 question

'''



def get_raw_scores(current_user, logged_users):
    '''
    Args:
        current_user (dict): dictionary with current user ID as the key (str) and 
            current user answers to the questions as an array of values
        logged_users (dict): dictionary with all logged user IDs as keys (str) and
            all logged user answers as an array of values
    Returns:
        raw_scores (array): array of raw scores between current user and all logged
            users; sum of differences between each user with current user across 
            all questions
    '''
    users_matrix = np.array(list(logged_users.values()))
    current_user_arr = np.array(list(current_user.values()))
    
    diff_matrix = np.abs(users_matrix - current_user_arr)
    raw_scores = np.nansum(diff_matrix, axis=1)
    N_overlap = [np.count_nonzero(~np.isnan(diff_arr)) for diff_arr in diff_matrix]
    
    N_multiselect = len(genres_list) + len(sports_list)
    N_qs = np.count_nonzero(~np.isnan(current_user_arr[0][N_multiselect:]))
    N_ms = np.count_nonzero(~np.isnan(current_user_arr[0][:N_multiselect]))
    max_score = N_qs*5+N_ms
    
    return raw_scores, max_score, N_overlap



def get_filtered(users, preference):
    users_df = pd.DataFrame(users).T
    
    users_df_filtered = users_df[users_df['gender'].isin(preference_dict[preference])].T
    return users_df_filtered.to_dict()

def get_pop_scores(raw_scores, limit):
    pop_scores_CI = [[100-stats.percentileofscore(raw_scores, raw_score+np.sqrt(raw_score)), 100-stats.percentileofscore(raw_scores, raw_score), 100-stats.percentileofscore(raw_scores, raw_score-np.sqrt(raw_score))] for raw_score in raw_scores[:limit]]
    return pop_scores_CI

def get_prox_scores(raw_scores, max_score, limit):
    raw_scores = raw_scores[:limit]
    prox_scores = (max_score-raw_scores)/max_score*100
    return prox_scores




def get_multiselect_answers(multiselect_list, full_list, current=False):
    if len(multiselect_list) == 0:
        return [np.nan]*len(full_list)
    
    answers = np.array([option in multiselect_list for option in full_list], dtype=float)
    if current == True:
        answers[answers==0] = np.nan
    return list(answers)

def get_answers(users, current=False):
    answers = {user_id: get_multiselect_answers(users[user_id]['music'], genres_list, current)+\
               get_multiselect_answers(users[user_id]['sports'], sports_list, current)+\
               list(users[user_id]['answers']) for user_id in users.keys()}
    return answers




def get_top_scores(current_user, logged_users, limit):
    current = get_answers(current_user, current=True)
    logged = get_answers(logged_users)
    raw_scores_all, max_score, N_overlap = get_raw_scores(current, logged)

    argsort_idx = raw_scores_all.argsort()
    raw_scores_sorted = np.array(raw_scores_all)[argsort_idx]

    top_pop_scores_CI = get_pop_scores(raw_scores_sorted, limit=limit)
    top_prox_scores = get_prox_scores(raw_scores_sorted, max_score, limit=limit)

    top_final_scores = [(np.array(pop)+prox)/2.0 for pop, prox in zip(top_pop_scores_CI, top_prox_scores)]
    
    return top_final_scores, argsort_idx

def get_top_profiles(logged_users, argsort_idx, limit):
    top_user_ids = np.array(list(logged_users.keys()))[argsort_idx][:limit]
    top_profiles = {user_id: logged_users[user_id] for user_id in top_user_ids}
    
    return top_profiles


def get_profile_list(top_profiles, top_final_scores):
    profile_list = {}
    for user_id, score in zip(top_profiles.keys(), top_final_scores):
        profile_brief = {
            'score': round(score[1],2),
            'user_id': user_id,
            'name': top_profiles[user_id]['name']['first'],
            'age': top_profiles[user_id]['age'],
            'gender': top_profiles[user_id]['gender'],
            'pronouns': top_profiles[user_id]['pronouns'],
            'bio': top_profiles[user_id]['bio'],
            'music': top_profiles[user_id]['music'],
            'sports': top_profiles[user_id]['sports'],
            'score_CI': [round(score[0],2), round(score[2],2)],
        }
        profile_list[user_id] = profile_brief
    return profile_list








'''
def get_raw_scores(current_user, logged_users):

    users_matrix = np.array(list(logged_users.values()))
    current_user_arr = np.array(list(current_user.values()))
    raw_scores = np.nansum(np.abs(users_matrix - current_user_arr),axis=1)
    
    N_multiselect = len(genres_list) + len(sports_list)
    N_qs = np.count_nonzero(~np.isnan(current_user_arr[N_multiselect:]))
    N_ms = np.count_nonzero(~np.isnan(current_user_arr[:N_multiselect]))
    max_score = N_qs*5+N_ms
    
    return raw_scores, max_score



def get_filtered(users, preference):
    users_df = pd.DataFrame(users).T
    
    users_df_filtered = users_df[users_df['gender'].isin(preference_dict[preference])].T
    return users_df_filtered.to_dict()

def get_pop_scores(raw_scores, limit):
    pop_scores_CI = [[100-stats.percentileofscore(raw_scores, raw_score+np.sqrt(raw_score)), 100-stats.percentileofscore(raw_scores, raw_score), 100-stats.percentileofscore(raw_scores, raw_score-np.sqrt(raw_score))] for raw_score in raw_scores[:limit]]
    return pop_scores_CI

def get_prox_scores(raw_scores, max_score, limit):
    raw_scores = raw_scores[:limit]
    prox_scores = (max_score-raw_scores)/max_score*100
    return prox_scores




def get_multiselect_answers(multiselect_list, full_list):
    if len(multiselect_list) == 0:
        return [np.nan]*len(full_list)
    answers = np.array([option in multiselect_list for option in full_list], dtype=int)
    return list(answers)

def get_answers(users):
    answers = {user_id: get_multiselect_answers(users[user_id]['music'], genres_list)+\
               get_multiselect_answers(users[user_id]['sports'], sports_list)+\
               list(users[user_id]['answers']) for user_id in users.keys()}
    return answers




def get_top_scores(current_user, logged_users, limit):
    current = get_answers(current_user)
    logged = get_answers(logged_users)
    raw_scores_all, max_score = get_raw_scores(current, logged)

    argsort_idx = raw_scores_all.argsort()
    raw_scores_sorted = np.array(raw_scores_all)[argsort_idx]

    top_pop_scores_CI = get_pop_scores(raw_scores_sorted, limit=limit)
    top_prox_scores = get_prox_scores(raw_scores_sorted, max_score, limit=limit)

    top_final_scores = [(np.array(pop)+prox)/2.0 for pop, prox in zip(top_pop_scores_CI, top_prox_scores)]
    
    return top_final_scores, argsort_idx

def get_top_profiles(logged_users, argsort_idx, limit):
    top_user_ids = np.array(list(logged_users.keys()))[argsort_idx][:limit]
    top_profiles = {user_id: logged_users[user_id] for user_id in top_user_ids}
    
    return top_profiles


def get_profile_list(top_profiles, top_final_scores):
    profile_list = {}
    for user_id, score in zip(top_profiles.keys(), top_final_scores):
        profile_brief = {
            'score': score[1],
            'name': top_profiles[user_id]['name']['first'],
            'age': top_profiles[user_id]['age'],
            'gender': top_profiles[user_id]['gender'],
            'pronouns': top_profiles[user_id]['pronouns'],
            'bio': top_profiles[user_id]['bio'],
            'music': top_profiles[user_id]['music'],
            'sports': top_profiles[user_id]['sports'],
            'score_CI': [score[0], score[2]],
        }
        profile_list[user_id] = profile_brief
    return profile_list
'''




