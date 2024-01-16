import math
import uuid

from datetime import datetime

# def calculate_score_obtained_original(acumulated_games_played: int, points_difference: int): 
    
#     if is_winner:
#         score_obtained = 1 + 0.5 * ((points_positive - points_negative) / 100)
#     else:
#         score_obtained = 0 - 0.5 * ((points_negative - points_positive) / 100)
         
#     return score_obtained

def calculate_score_obtained(games_won: int, points_difference: int): 
    return round(games_won + (points_difference / 200), 2)
    
def calculate_score_expected(elo_win_pair: float, elo_lost_pair: float):  
    return round(1 / (1 + 10 ** ((elo_lost_pair - elo_win_pair) / 800)), 2)
 
def calculate_increasing_constant(constant_increase_elo: float, number_games_played: int):  
    return round(constant_increase_elo + (300 / (300 + number_games_played)), 2)
    
def calculate_new_elo(increasing_constant: float, number_games_played: int, score_expected: float, score_obtained: float):  
    return 0 if number_games_played == 0 else round(increasing_constant * (score_obtained - score_expected), 2)
    # return 0 if number_games_played == 0 else round(score_obtained - score_expected, 2)
