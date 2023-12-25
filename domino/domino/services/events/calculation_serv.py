import math
import uuid

from datetime import datetime

def calculate_score_obtained(points_positive: int, points_negative: int, is_winner:bool): 
    
    if is_winner:
        score_obtained = 1 + 0.5 * ((points_positive - points_negative) / 100)
    else:
        score_obtained = 0 - 0.5 * ((points_negative - points_positive) / 100)
         
    return score_obtained

def calculate_score_expected(elo_win_pair: float, elo_lost_pair: float):  
    
    score_expected = 1 / 1 + 10 ** ((elo_lost_pair/elo_win_pair) / 800)
    
    return score_expected

def calculate_increasing_constant(number_games_played: int):  
    
    increasing_constant = 2 + (300 / 100 + number_games_played)
    
    return increasing_constant

def calculate_new_elo(current_elo: float, number_games_played: int, points_positive: int, points_negative: int, 
                      is_winner:bool, elo_win_pair: float, elo_lost_pair: float):  
    
    increasing_constant = calculate_increasing_constant(number_games_played)
    score_obtained = calculate_score_obtained(points_positive, points_negative, is_winner)
    score_expected = calculate_score_expected(elo_win_pair, elo_lost_pair)
    
    new_elo = current_elo + increasing_constant * (score_obtained - score_expected)
    
    return new_elo