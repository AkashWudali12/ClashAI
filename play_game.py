from agent.agent import ClashAgent

def play_game():
    print("Playing Game")
    agent = ClashAgent()
    agent.play()
    print("Game Finished")

if __name__ == "__main__":
    play_game()