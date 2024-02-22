import math
import uuid

from datetime import datetime

# def calculate_score_obtained_original(acumulated_games_played: int, points_difference: int): 
    
#     if is_winner:
#         score_obtained = 1 + 0.5 * ((points_positive - points_negative) / 100)
#     else:
#         score_obtained = 0 - 0.5 * ((points_negative - points_positive) / 100)
         
#     return score_obtained

def calculate_score_obtained(games_won: int, points_difference: int, number_points_to_win: int): 
    return games_won + (points_difference / number_points_to_win)
    
def calculate_score_expected(elo_pair_ra: float, elo_pair_rb: float):  
    return 1 / (1 + 10 ** ((elo_pair_ra - elo_pair_rb) / 400))
    # return round(1 / (1 + 10 ** ((elo_lost_pair - elo_win_pair) / 800)), 2)
 
def calculate_increasing_constant(constant_increase_elo: float, number_games_played: int): 
    # number_games_played = 9 
    return round(constant_increase_elo + (300 / (300 + number_games_played)), 2)
    
# def calculate_new_elo(increasing_constant: float, number_games_played: int, score_expected: float, score_obtained: float, uses_increasing_constant=True):  
#     value_increasing_constant = increasing_constant if uses_increasing_constant else 1
#     return 0 if number_games_played == 0 else round(value_increasing_constant * (score_obtained - score_expected), 2)
#     # return 0 if number_games_played == 0 else round(score_obtained - score_expected, 2)
    
def calculate_new_elo(number_games_played:int, score_expected: float, score_obtained: float):  
    return score_obtained - score_expected
    # return 0 if number_games_played == 0 else round(score_obtained - score_expected, 2)

def calculate_end_elo(initial_elo:float, summary_elo_obtained: float, k_value: float):  
    return initial_elo + summary_elo_obtained * k_value

def get_motive_closed(motive:str):
    
    dict_motive = {'points': 'Cerrado por puntos',
                   'time': 'Cerrado por tiempo',
                   'penalty': 'Cerrado por penalización',
                   'non_completion': 'Cerrado por no completamiento de mesa',
                   'absences': 'Cerrado por ausencia de jugadores',
                   'abandon': 'Cerrado por abandono de jugadores',
                   'annulled': 'Cerrado por Boleta anulada'}
    
    return dict_motive[motive] if motive in dict_motive else ''

def format_number(number):

    number = "%6f" %number
    return number[:-4]