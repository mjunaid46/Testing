import pickle
import time
import sys
import importlib
import task_logic  # Import the task logic module

def save_state(data, filename="state.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_state(filename="state.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

class TaskWithDynamicReload:
    def __init__(self):
        self.state = load_state() or {"step": 1, "retry_count": 0}
        self.max_steps = 5
        self.max_retries = 3

    def reload_task_logic(self):
        """Dynamically reload the task_logic module."""
        if "task_logic" in sys.modules:
            del sys.modules["task_logic"]  # Remove from cache
        global task_logic
        importlib.import_module("task_logic")  # Reimport fresh module
        task_logic = sys.modules["task_logic"]  # Update the reference

    def run(self):
        while self.state["step"] <= self.max_steps:
            try:
                print(f"Starting step {self.state['step']} (Retry {self.state['retry_count']} of {self.max_retries})...")
                self.reload_task_logic()  # Reload the task logic dynamically

                # Run the task logic for the current step
                success = task_logic.TaskLogic.run_step(self.state["step"])

                if success:
                    self.state["step"] += 1
                    self.state["retry_count"] = 0
                    save_state(self.state)

            except Exception as e:
                print(f"Error: {e}. Resolve the issue and press Enter to continue.")
                input("Press Enter to resume...")
                self.state["retry_count"] += 1

                if self.state["retry_count"] > self.max_retries:
                    print("Maximum retries reached. Skipping to the next step.")
                    self.state["step"] += 1
                    self.state["retry_count"] = 0

                save_state(self.state)
                continue

        print("Task completed successfully!")

if __name__ == "__main__":
    task = TaskWithDynamicReload()
    task.run()
