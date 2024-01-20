import pygame
import random
import math
import asyncio
import pandas as pd

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound
wrong_guess_sound = pygame.mixer.Sound('wordle/sfx/buzzer.ogg')  
correct_guess_sound = pygame.mixer.Sound('wordle/sfx/correct.ogg')

# Set up the display
WIDTH, HEIGHT = 1400, 800
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Altıgen Kelime Tahmin Etme Oyunu")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

button_rect = pygame.Rect(WIDTH - 150, 100, 125, 50)  # Button position and size
letter_rect = pygame.Rect(WIDTH - 150, 200, 100, 50)  # Letter position and size



random_game_num = random.randint(1, 30)
print("Selected game number: ", random_game_num)


sheet_name = f"{random_game_num}.OYUN"
words_xlsx = pd.read_excel('wordle/sfx/sorular.xlsx', sheet_name=sheet_name)


def turkish_replace(word):
    word = word.replace('İ', 'i')
    word = word.replace('Ç', 'ç')
    word = word.replace('Ş', 'ş')
    word = word.replace('Ğ', 'ğ')
    word = word.replace('Ü', 'ü')
    word = word.replace('Ö', 'ö')
    word = word.replace('I', 'ı')
    return word

def random_word_xlsx(words_xlsx):
    chosen_word = random.choice(words_xlsx.iloc[:,1].values)
    word_length = len(chosen_word)
    word_description = words_xlsx.loc[words_xlsx['CEVAP'] == chosen_word, 'SORU'].iloc[0]
    indexes = [i for i in range(len(chosen_word))]
    point_of_word = 100 * len(chosen_word)
    guessed_letters = ['_'] * word_length
    words_xlsx = words_xlsx.drop(words_xlsx.loc[words_xlsx['CEVAP'] == chosen_word].index, inplace=True)
    return chosen_word, word_length, word_description, indexes, point_of_word, guessed_letters

def random_word(words):
    chosen_word = random.choice(list(words.keys()))
    word_length = len(chosen_word)
    word_description = words[chosen_word]
    indexes = [i for i in range(len(chosen_word))]
    point_of_word = 100 * len(chosen_word)
    guessed_letters = ['_'] * word_length
    words.pop(chosen_word)
    return chosen_word, word_length, word_description, indexes, point_of_word, guessed_letters

def reveal_random_letter(chosen_word, indexes, guessed_letters):
    index = random.choice(indexes)
    guessed_letters[index] = chosen_word[index]
    indexes.remove(index)

# Hexagon properties
side_length = 40
hex_width = math.sqrt(3) * side_length
hex_height = 2 * side_length

# Function to draw a hexagon
def draw_hexagon(x, y):
    points = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        points.append((x + side_length * math.cos(angle_rad),
                       y + side_length * math.sin(angle_rad)))
    pygame.draw.polygon(win, BLACK, points, 2)

# Function to reveal a random letter
chosen_word, word_length, word_description, indexes, point_of_word, guessed_letters = random_word_xlsx(words_xlsx)
guess = ''
guess_font = pygame.font.SysFont(None, 36)
input_rect = pygame.Rect(50, 300, 300, 40)  # Input field position and size
active = False  # Flag to control the input field focus

# Game loop
running = True
total_point = 0

timer_running = True
time_limit = 120  # Two minutes in seconds

async def main():
    start_time = pygame.time.get_ticks()  # Start time in milliseconds
    paused_time = 0
    global timer_running, active, guess, chosen_word, word_length, word_description, indexes, point_of_word, guessed_letters, total_point, running
    while running:
         
        if not timer_running:
            ## quit game if paused time is more than 15 seconds
            if pygame.time.get_ticks() - paused_start_time > 15000:
                ## display a message
                running = False
                break
            
        win.fill(WHITE)  # Fill the window with white color    
        await asyncio.sleep(0)
        
        # Display total point
        font = pygame.font.SysFont(None, 36)
        text = font.render('Toplam puan: ' + str(total_point), True, BLACK)
        win.blit(text, (50, 20))

        # Display remaining word point
        font = pygame.font.SysFont(None, 36)
        text = font.render('Kalan Harf Puanı: ' + str(point_of_word), True, BLACK)
        win.blit(text, (50, 50))
        
        # Draw hexagon grid for guessed letters
        offset_x = 50
        offset_y = 150  # Adjust the offset to position the hexagons lower
        text_offset_y = offset_y - 30  # Offset for the text above hexagons
        for i in range(word_length):
            draw_hexagon(offset_x + i * (hex_width + 10), offset_y)
        
        font = pygame.font.SysFont(None, 24)
        text = font.render('Açıklama: ' + word_description, True, BLACK)
        text_rect = text.get_rect(midtop=(WIDTH // 2, offset_y + hex_height + 20))
        win.blit(text, text_rect)
        
        # Draw the button
        pygame.draw.rect(win, BLACK, button_rect)  # Draw the button rectangle
        font = pygame.font.SysFont(None, 24)
        text = font.render("Süreyi Durdur", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        win.blit(text, text_rect)  # Display text on the button
        
        # Draw the letter button
        pygame.draw.rect(win, BLACK, letter_rect)  # Draw the button rectangle
        font = pygame.font.SysFont(None, 24)
        text = font.render("Harf Al", True, WHITE)
        text_rect = text.get_rect(center=letter_rect.center)
        win.blit(text, text_rect)  # Display text on the button
        
        if active:
            pygame.draw.rect(win, BLACK, input_rect, 2)  # Draw the input field rectangle
            text_surface = guess_font.render(guess, True, BLACK)
            win.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))  # Display the guess text

        if timer_running:  # Check if the timer is running
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_time - paused_time) // 1000  # Convert to seconds
            remaining_time = max(time_limit - elapsed_time, 0)
            timer_text = f"Kalan Süre: {remaining_time // 60:02}:{remaining_time % 60:02}"
            timer_surface = font.render(timer_text, True, BLACK)
            timer_rect = timer_surface.get_rect(topright=(WIDTH - 20, 50))
            win.blit(timer_surface, timer_rect)
        else:
            timer_text = "Süre Durduruldu"  # Display a message when the timer is stopped
            timer_surface = font.render(timer_text, True, BLACK)
            timer_rect = timer_surface.get_rect(topright=(WIDTH - 20, 50))
            win.blit(timer_surface, timer_rect)
            
        if remaining_time <= 0:
            running = False
            break
            
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # implement the event handling for touch events
            elif event.type == pygame.KEYDOWN:
                if active:  # Check if the input field is active
                    if event.key == pygame.K_RETURN:  # If Enter is pressed, check the guess
                        if guess == chosen_word or turkish_replace(guess).lower() == turkish_replace(chosen_word).lower():
                            total_point += point_of_word
                            correct_guess_sound.play()
                            try:
                                chosen_word, word_length, word_description, indexes, point_of_word, guessed_letters = random_word_xlsx(words_xlsx)
                            except IndexError:
                                running = False
                                break
                            guess = ''
                            active = False
                            timer_running = True
                            paused_time += pygame.time.get_ticks() - paused_start_time
                        else:
                            guess = ''
                            wrong_guess_sound.play()  
                            
                    elif event.key == pygame.K_BACKSPACE:  # Handle backspace to delete characters
                        guess = guess[:-1]  # Remove the last character from the guess
                    else:
                        guess += event.unicode  # Add typed characters to the guess
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    if timer_running:
                        timer_running = False  # Stop the timer when the button is clicked
                        paused_start_time = pygame.time.get_ticks()  # Record the time when the timer is paused
                    # timer_running = False
                    active = True  # Toggle input field focus
                if letter_rect.collidepoint(event.pos):
                    try:
                        reveal_random_letter(chosen_word, indexes, guessed_letters)
                        point_of_word -= 100
                    except:
                        try:
                            chosen_word, word_length, word_description, indexes, point_of_word, guessed_letters = random_word_xlsx(words_xlsx)
                        except IndexError:
                            running = False
                            break
                    
        # Render guessed letters
        font = pygame.font.SysFont(None, 36)
        for i, letter in enumerate(guessed_letters):
            text = font.render(letter, True, BLACK)
            win.blit(text, (offset_x + i * (hex_width + 10) - 10, offset_y - 20))
        
        pygame.display.update()  # Update the display


    # After the game loop ends:
    final_score_font = pygame.font.SysFont(None, 48)
    final_score_text = final_score_font.render(f'Toplam Skor: {total_point}', True, BLACK)
    final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    win.fill(WHITE)  # Clear the screen
    win.blit(final_score_text, final_score_rect)
    pygame.display.update()

    pygame.time.wait(3000)  # Wait for 3 seconds before quitting (adjust as needed)
    pygame.quit()  # Quit Pygame

asyncio.run(main())
