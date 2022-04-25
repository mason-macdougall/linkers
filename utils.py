import pandas as pd
import numpy as np
from scipy import stats

def get_raw_scores(current_user, logged_users, N_options=5):
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
    raw_scores = np.nansum(np.abs(users_matrix - current_user_arr),axis=1)
    
    N_qs = np.count_nonzero(~np.isnan(current_user_arr))
    max_score = N_qs*N_options
    #uncertainty = np.sqrt(N_qs*N_options)
    
    return raw_scores, max_score#, uncertainty

def get_filtered(users, preference):
    users_df = pd.DataFrame(users).T
    
    preference_dict = {'female': ['female'],
                       'male': ['male'],
                       'non-binary': ['non-binary'],
                       'anyone': ["", "female", "male", "non-binary", "gender-fluid", "transgender", "other"],
                       'other': ["", "gender-fluid", "transgender", "other"]
                      }
    
    users_df_filtered = users_df[users_df['gender'].isin(preference_dict[preference])].T
    return users_df_filtered.to_dict()

def get_pop_scores(raw_scores, limit):
    pop_scores_CI = [[100-stats.percentileofscore(raw_scores, raw_score+np.sqrt(raw_score)), 100-stats.percentileofscore(raw_scores, raw_score), 100-stats.percentileofscore(raw_scores, raw_score-np.sqrt(raw_score))] for raw_score in raw_scores[:limit]]
    return pop_scores_CI

def get_prox_scores(raw_scores, max_score, limit):
    raw_scores = raw_scores[:limit]
    prox_scores = (max_score-raw_scores)/max_score*100
    return prox_scores




def get_multiselect_answers(multiselect_list, full_list): #, skip=True):
    #if skip == True:
    #    return [np.nan]*len(full_list)
    answers = np.array([option in multiselect_list for option in full_list], dtype=int)
    return list(answers)

def get_answers(users):
    answers = {user_id: get_multiselect_answers(users[user_id]['music'], genres_list)+\
               get_multiselect_answers(users[user_id]['sports'], sports_list)+\
               list(users[user_id]['answers']) for user_id in users.keys()}
    return answers




def get_top_scores(current_user, logged_users, limit, N_options=5):
    current, logged = get_answers(current_user), get_answers(logged_users)
    raw_scores_all, max_score = get_raw_scores(current, logged, N_options=N_options)

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
            'name': top_profiles[user_id]['name']['first'],
            'age': top_profiles[user_id]['age'],
            'gender': top_profiles[user_id]['gender'],
            'pronouns': top_profiles[user_id]['pronouns'],
            'bio': top_profiles[user_id]['bio'],
            'score': score[1],
            'score_lower_est': score[0],
            'score_upper_est': score[2]
        }
        profile_list[user_id] = profile_brief
    return profile_list





