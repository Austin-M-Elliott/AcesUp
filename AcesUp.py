import random
from collections import namedtuple, defaultdict
import matplotlib.pyplot as plt

Card = namedtuple('Card', ['suit', 'value', 'ace_moved']) #namedtuple to include flag for tracking if an ace has been moved

def create_deck():
    #"""Create a standard deck of cards."""
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    values = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
    return [Card(suit, value, False) for suit in suits for value in values]

def shuffle_deck(deck):
    #"""Shuffle the deck."""
    random.shuffle(deck)
    return deck

def card_value(card):
    #"""Returns the numeric value of a card for comparison purposes."""
    if card.value in ['J', 'Q', 'K']:
        return 11 + ['J', 'Q', 'K'].index(card.value)
    if card.value == 'A':
        return 14
    return card.value

def deal_round_with_stack(deck, board):
    #"""Deal a round of four cards, placing them on top of any existing cards."""
    for i in range(4):
        if deck:
            if len(board) > i:
                board[i].append(deck.pop(0))  # Place card on top of the stack
            else:
                board.append([deck.pop(0)])  # New stack for the position

def discard_face_up_cards(board):
    #"""Discard face-up cards that are lower than other face-up cards of the same suit."""
    cards_discarded = True
    while cards_discarded:
        cards_discarded = False
        highest_face_up_cards = {suit: 0 for suit in ['hearts', 'diamonds', 'clubs', 'spades']}

        # Find the highest face-up card of each suit
        for stack in board:
            if stack:
                top_card = stack[-1]
                top_card_value = card_value(top_card)
                if top_card_value > highest_face_up_cards[top_card.suit]:
                    highest_face_up_cards[top_card.suit] = top_card_value

        # Remove cards that are not the highest of their suit among face-up cards
        for stack in board:
            if stack and card_value(stack[-1]) < highest_face_up_cards[stack[-1].suit]:
                stack.pop()  # Remove the lower card
                cards_discarded = True

# Modify the play_game_with_stacks function to use the updated Ace movement logic
def play_game_with_stacks_updated(deck):
    #"""Game basis."""
    deck = shuffle_deck(deck)
    board = [[] for _ in range(4)]  #Game board
    while deck:
        deal_round_with_stack(deck, board)
        discard_face_up_cards(board)
        move_ace_with_optimal_strategy(board)

    # Count remaining cards on the board
    remaining_on_board = sum(len(stack) for stack in board)
    return remaining_on_board, len(deck)

# Modify the simulate_games_with_stacks function to use the updated play_game function
def simulate_games_with_stacks_updated(num_simulations):
    #"""Simulate the game multiple times and record the outcomes with updated logic."""
    outcomes_board = defaultdict(int)
    outcomes_hand = defaultdict(int)

    for _ in range(num_simulations):
        deck = create_deck()
        board_remaining, hand_remaining = play_game_with_stacks_updated(deck)
        outcomes_board[board_remaining] += 1
        outcomes_hand[hand_remaining] += 1

    return outcomes_board, outcomes_hand

def play_game_with_logging(deck):
    #"""Log each movement for debugging."""
    deck = shuffle_deck(deck)
    board = [[] for _ in range(4)] 
    round_count = 0

    while deck:
        round_count += 1
        print(f"\nRound {round_count}: Dealing cards...")
        deal_round_with_stack(deck, board)

        # Log the dealt cards
        for i, stack in enumerate(board):
            print(f"  Pile {i + 1}: {stack[-1] if stack else 'Empty'} (Top Card)")

        print("\nDiscarding lower cards...")
        discard_face_up_cards(board)

        # Log the face-up cards after discarding
        for i, stack in enumerate(board):
            print(f"  Pile {i + 1} after discard: {stack[-1] if stack else 'Empty'} (Top Card)")

        print("\nChecking and moving aces...")
        move_ace_with_optimal_strategy(board)

        # Log the face-up cards after moving aces
        for i, stack in enumerate(board):
            print(f"  Pile {i + 1} after moving aces: {stack[-1] if stack else 'Empty'} (Top Card)")

    # Count remaining cards on the board
    remaining_on_board = sum(len(stack) for stack in board)
    return remaining_on_board, len(deck)

def can_move_ace(stack):
    return stack and stack[-1].value == 'A' and not stack[-1].ace_moved

def simulate_move_ace(board, from_pile, to_pile):
    new_board = [stack[:] for stack in board]  # Create deep copy of the board
    moved_ace = new_board[from_pile].pop()
    moved_ace = moved_ace._replace(ace_moved=True)  # Mark the ace as moved
    new_board[to_pile].append(moved_ace)
    return new_board

def simulate_subsequent_rounds(board, depth=0, max_depth=5):
    if depth == max_depth:
        return 0  # Stop the recursion

    score = 0
    # Simulate discarding cards
    score += discard_face_up_cards_simulated(board)

    # Check for further ace movements and recursively simulate
    for i, stack in enumerate(board):
        if can_move_ace(stack):
            for j in range(4):
                if j != i and not board[j]:
                    new_board = simulate_move_ace(board, i, j)
                    score += simulate_subsequent_rounds(new_board, depth + 1, max_depth)

    return score

def discard_face_up_cards_simulated(board):
    cards_discarded = True
    discard_count = 0
    while cards_discarded:
        cards_discarded = False
        highest_face_up_cards = {suit: 0 for suit in ['hearts', 'diamonds', 'clubs', 'spades']}

        # Find the highest face-up card of each suit
        for stack in board:
            if stack:
                top_card = stack[-1]
                top_card_value = card_value(top_card)
                if top_card_value > highest_face_up_cards[top_card.suit]:
                    highest_face_up_cards[top_card.suit] = top_card_value

        # Remove cards that are not the highest of their suit among face-up cards
        for stack in board:
            if stack and card_value(stack[-1]) < highest_face_up_cards[stack[-1].suit]:
                stack.pop()  # Remove the lower card
                cards_discarded = True
                discard_count += 1

    return discard_count

def move_ace_with_optimal_strategy(board): #Counting cards, you technically want to move aces in specific order if dealt more than two at once
    movable_aces = [(i, stack) for i, stack in enumerate(board) if can_move_ace(stack)]
    empty_piles = [j for j, stack in enumerate(board) if not stack]

    # If there's only one movable ace and an empty stack, move that ace
    if len(movable_aces) == 1 and empty_piles:
        execute_move_ace(board, movable_aces[0][0], empty_piles[0])
        discard_face_up_cards(board)  # Recheck for possible discards after moving an ace
        return

    # If there are multiple movable aces, use simulation to find the best move
    best_score = 0
    best_moves = []

    for i, _ in movable_aces: #For loop to simulate moving each movable ace and the moves following that. Best move is determined by highest number of following moves.
        for j in empty_piles:
            simulated_board = simulate_move_ace(board, i, j)
            score = simulate_subsequent_rounds(simulated_board)

            if score > best_score:
                best_score = score
                best_moves = [(i, j)]
            elif score == best_score:
                best_moves.append((i, j))

    # Choose randomly among the best moves if there's a tie
    if best_moves:
        chosen_move = random.choice(best_moves)
        execute_move_ace(board, *chosen_move)
        discard_face_up_cards(board)  # Recheck for possible discards after moving an ace

def execute_move_ace(board, from_pile, to_pile):
    moved_ace = board[from_pile].pop()
    moved_ace = moved_ace._replace(ace_moved=True)
    board[to_pile].append(moved_ace)


# Play a single game with logging
single_game_deck = create_deck()
remaining_on_board, remaining_in_deck = play_game_with_logging(single_game_deck)
print("\nGame Over")
print(f"Cards Remaining on Board: {remaining_on_board}")
print(f"Cards Remaining in Deck: {remaining_in_deck}")


# Number of simulations
num_simulations = 100000

# Simulate
simulation_results_with_stacks_updated, hand_remaining_results_with_stacks_updated = simulate_games_with_stacks_updated(num_simulations)

# Calculate probabilities for board outcomes
probabilities_board_with_stacks_updated = {k: v / num_simulations for k, v in simulation_results_with_stacks_updated.items()}

# Sorted probabilities 
probabilities_board_sorted_updated = dict(sorted(probabilities_board_with_stacks_updated.items()))

# Check the probability of having exactly four cards (aces) left. Win condition.
probability_of_four_aces_updated = probabilities_board_with_stacks_updated.get(4, 0)
print("Probability of Ending with Exactly Four Aces:", probability_of_four_aces_updated)

# Data for histogram
x_values_updated = list(range(min(probabilities_board_with_stacks_updated.keys()), 
                              max(probabilities_board_with_stacks_updated.keys()) + 1))
y_values_updated = [probabilities_board_with_stacks_updated.get(x, 0) for x in x_values_updated]

# Create histogram
plt.bar(x_values_updated, y_values_updated, color='blue', alpha=0.7)
plt.xlabel('Number of Cards Remaining on the Board')
plt.ylabel('Probability')
plt.title('Probability Distribution of Cards Remaining on the Board (Updated)')
plt.xticks(x_values_updated, rotation=90)
plt.show()

