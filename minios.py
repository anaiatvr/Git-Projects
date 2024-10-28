import os
import subprocess
import psutil
import time
import random
import json
import getpass

class MiniOS:
    
    def __init__(self):
        self.running = True
        self.start_time = time.time()
        
        self.commands = {
            "help": self.help,
            "ls": self.ls,
            "touch": self.touch,
            "rm": self.rm,
            "cat": self.cat,
            "echo": self.echo,
            "ps": self.ps,
            "run": self.run_process,
            "kill": self.kill_process,
            "cpu": self.cpu,
            "memory": self.memory,
            "uptime": self.uptime,
            "calc": self.calc,
            "blackjack": self.blackjack,
            "history": self.history,
            "logout": self.logout,
            "delete_users": self.delete_users,
            "exit": self.exit
        }
        self.processes = {}
        self.command_history = []  # List to store command history
        self.users = self.load_users() # Dictionary to store user credentials
        self.current_user = None  # Track the logged-in user
        
    def load_users(self):
        """Load user data from a JSON file if it exists and is not empty, otherwise return an empty dictionary."""
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r") as file:
                    data = file.read()
                    if data.strip():  # Check if the file is not empty
                        return json.loads(data)
            except json.JSONDecodeError:
                print("Error: The user data file is corrupted. Resetting to an empty user list.")
        return {}

    def save_users(self):
        """Save user data to a JSON file."""
        with open("users.json", "w") as file:
            json.dump(self.users, file)
            
    def login(self):
        while True:
            if self.users:
                print("Registered users:", ", ".join(self.users.keys()))
            action = input("Would you like to 'login' or 'register'? ").strip().lower()
            if action == "login":
                username = input("Username: ")
                password = getpass.getpass("Password: ")
                if self.authenticate(username, password):
                    self.current_user = username
                    print(f"Welcome, {self.current_user}!")
                    break
                else:
                    print("Invalid username or password. Please try again.")
            elif action == "register":
                username = input("Choose a username: ")
                password =getpass.getpass("Choose a password: ")
                if self.register(username, password):
                    print("Registration successful! You can now log in.")
                else:
                    print("Username already exists. Please choose a different username.")
            else:
                print("Invalid action. Please type 'login' or 'register'.")

    def authenticate(self, username, password):
        """Authenticate user with the provided username and password."""
        return self.users.get(username) == password

    def register(self, username, password):
        """Register a new user with a username and password, and save it to file."""
        if username in self.users:
            return False  # Username already exists
        self.users[username] = password
        self.save_users()  # Save users to file after registering a new one
        return True

    def logout(self):
        if self.current_user:
            print(f"Logging out {self.current_user}...")
            self.current_user = None
        else:
            print("No user is currently logged in.")
            
    def run(self):
        print("✩₊˚.⋆☾⋆⁺₊✧- Welcome to MiniOS ᕕ( ᐛ )ᕗ! -✩₊˚.⋆☾⋆⁺₊✧\n\t\tMade by: Tai /ᐠ-˕-マ")
        while self.running:
            if not self.current_user:
                self.login()
            command = input(f"{self.current_user}> ").strip().split()
            if command:
                self.command_history.append(' '.join(command))  #Store command in history
                self.execute_command(command)

    def execute_command(self, command):
        cmd = command[0]
        args = command[1:]
        func = self.commands.get(cmd, None)
        if func:
            try:
                func(*args)
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
        else:
            print(f"Unknown command: {cmd}. Type 'help' for a list of commands.")

    # Core Commands
    def help(self):
        print("Available commands:")
        for cmd in self.commands:
            print(f"  {cmd}")

    def ls(self):
        print("Listing files:")
        for item in os.listdir('.'):
            print(item)

    def touch(self, *filenames):
        for filename in filenames:
            try:
                open(filename, 'a').close()
                print(f"Created file '{filename}'")
            except Exception as e:
                print(f"Error creating file '{filename}': {e}")

    def rm(self, *filenames):
        for filename in filenames:
            try:
                os.remove(filename)
                print(f"Deleted file '{filename}'")
            except FileNotFoundError:
                print(f"File '{filename}' not found.")
            except Exception as e:
                print(f"Error deleting file '{filename}': {e}")

    def cat(self, *filenames):
        for filename in filenames:
            try:
                with open(filename, 'r') as file:
                    print(file.read())
            except FileNotFoundError:
                print(f"File '{filename}' not found.")
            except Exception as e:
                print(f"Error reading file '{filename}': {e}")

    def echo(self, *args):
        if len(args) < 3 or args[-2] != '>':
            print("Usage: echo <message> > <filename>")
            return
        message = ' '.join(args[:-2])
        filename = args[-1]
        try:
            with open(filename, 'w') as file:
                file.write(message)
            print(f"Message written to '{filename}'")
        except Exception as e:
            print(f"Error writing to file '{filename}': {e}")

    # Process Management
    def ps(self):
        if self.processes:
            print("PID   Command")
            for pid, proc in self.processes.items():
                print(f"{pid}   {' '.join(proc.args)}")
        else:
            print("No running processes.")

    def run_process(self, script):
        try:
            process = subprocess.Popen(["python", script])
            self.processes[process.pid] = process
            print(f"Started process with PID {process.pid}")
        except FileNotFoundError:
            print(f"Script '{script}' not found.")
        except Exception as e:
            print(f"Error starting process: {e}")

    def kill_process(self, pid):
        try:
            pid = int(pid)
            process = self.processes.pop(pid, None)
            if process:
                process.terminate()
                print(f"Terminated process with PID {pid}")
            else:
                print(f"No process with PID {pid} found.")
        except ValueError:
            print("Invalid PID.")
        except Exception as e:
            print(f"Error terminating process: {e}")

    # System Monitoring
    def cpu(self):
        try:
            cpu_usage = psutil.cpu_percent()
            print(f"CPU Usage: {cpu_usage}%")
        except Exception as e:
            print(f"Error retrieving CPU usage: {e}")

    def memory(self):
        try:
            mem = psutil.virtual_memory()
            print(f"Memory Usage: {mem.percent}%")
        except Exception as e:
            print(f"Error retrieving memory usage: {e}")

    def uptime(self):
        uptime = time.time() - self.start_time
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"System Uptime: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")

    # Custom Calculator
    def calc(self):
        try:
            expr = input("Enter expression (e.g., 5 + 3 * 2): ")
            result = eval(expr, {"__builtins__": None}, {})
            print(f"Result: {result}")
        except Exception as e:
            print(f"Calculation error: {e}")

    # Blackjack Game
    def blackjack(self):
        def draw_card():
            return random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])

        def calculate_hand(hand):
            total = sum(hand)
            aces = hand.count(11)
            while total > 21 and aces:
                total -= 10
                aces -= 1
            return total

        print("Welcome to Blackjack!")
        play_again = True

        while play_again:
            player_hand = [draw_card(), draw_card()]
            dealer_hand = [draw_card(), draw_card()]

            print(f"Your hand: {player_hand}, total: {calculate_hand(player_hand)}")
            print(f"Dealer's visible card: {dealer_hand[0]}")

            player_bust = False
            while True:
                choice = input("Would you like to 'hit' or 'stand'? ").strip().lower()
                if choice == "hit":
                    player_hand.append(draw_card())
                    player_total = calculate_hand(player_hand)
                    print(f"Your hand: {player_hand}, total: {player_total}")
                    if player_total > 21:
                        print("Bust! You went over 21. Dealer wins!")
                        player_bust = True
                        break
                elif choice == "stand":
                    break
                else:
                    print("Invalid choice. Please type 'hit' or 'stand'.")

            if not player_bust:
                print(f"\nDealer's hand: {dealer_hand}, total: {calculate_hand(dealer_hand)}")
                while calculate_hand(dealer_hand) < 17:
                    dealer_hand.append(draw_card())
                    print(f"Dealer hits: {dealer_hand}, total: {calculate_hand(dealer_hand)}")
                    if calculate_hand(dealer_hand) > 21:
                        print("Dealer busts! You win!")
                        break

            player_total = calculate_hand(player_hand)
            dealer_total = calculate_hand(dealer_hand)
            if player_total <= 21 and dealer_total <= 21:
                print(f"\nFinal hands:\n  Your total: {player_total}\n  Dealer's total: {dealer_total}")
                if player_total > dealer_total:
                    print("You win!")
                elif player_total < dealer_total:
                    print("Dealer wins!")
                else:
                    print("It's a tie!")

            play_again_input = input("\nWould you like to play again? (yes/no): ").strip().lower()
            play_again = play_again_input == "yes"

        print("Thanks for playing Blackjack!")

    # Command History
    def history(self):
        print("Command History:")
        if not self.command_history:
            print("No commands entered yet.")
        else:
            for index, cmd in enumerate(self.command_history, start=1):
                print(f"{index}: {cmd}")
                

    def exit(self):
        self.running = False
        print("Shutting down MiniOS...")
        
    def delete_users(self):
        """Delete all users from the system and clear the users.json file."""
        confirmation = input("Are you sure you want to delete all users? This action cannot be undone (yes/no): ")
        if confirmation.lower() == "yes":
            self.users.clear()  # Clear the users dictionary in memory
            open("users.json", "w").close()  # Clear the contents of users.json
            print("All users have been deleted.")
        else:
            print("Action canceled.")

if __name__ == "__main__":
    os_system = MiniOS()
    os_system.run()
