import pickle
import sys
import importlib
import task_logic

def save_state(data, filename="state.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_state(filename="state.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

class TaskWithDependencyHandling:
    def __init__(self):
        self.state = load_state() or {"step": 1, "retry_count": 0, "needs_revalidation": False}
        self.max_steps = 5
        self.max_retries = 3

    def reload_task_logic(self):
        """Reload the task_logic module dynamically."""
        if "task_logic" in sys.modules:
            del sys.modules["task_logic"]
        global task_logic
        importlib.import_module("task_logic")
        task_logic = sys.modules["task_logic"]
        print("Reloaded task_logic module.")

    def revalidate_steps(self):
        """Revalidate all steps up to the current step if necessary."""
        print("Revalidation triggered...")
        for step in range(1, self.state["step"]):
            try:
                print(f"Revalidating step {step}...")
                success = task_logic.TaskLogic.run_step(step)
                if not success:
                    print(f"Step {step} failed during revalidation. Restarting from step {step}.")
                    self.state["step"] = step
                    self.state["retry_count"] = 0
                    save_state(self.state)
                    return False
            except Exception as e:
                print(f"Error during revalidation of step {step}: {e}")
                self.state["step"] = step
                self.state["retry_count"] = 0
                save_state(self.state)
                return False
        print("Revalidation completed successfully.")
        return True

    def run(self):
        while self.state["step"] <= self.max_steps:
            if self.state["retry_count"] == 0:
                print(f"Starting step {self.state['step']}...")
            try:
                # Reload task logic only when revalidation is needed
                if self.state["needs_revalidation"]:
                    self.reload_task_logic()

                    # Revalidate all steps up to the current step
                    if not self.revalidate_steps():
                        continue

                    # Reset revalidation flag
                    self.state["needs_revalidation"] = False

                # Execute the current step
                success = task_logic.TaskLogic.run_step(self.state["step"])
                if success:
                    self.state["step"] += 1
                    self.state["retry_count"] = 0
                    save_state(self.state)
            except Exception as e:
                print(f"Error: {e}. Resolve the issue and press Enter to continue.")
                input("Press Enter to resume...")
                self.state["needs_revalidation"] = True
                self.state["retry_count"] += 1

                if self.state["retry_count"] > self.max_retries:
                    print(f"Maximum retries reached for step {self.state['step']}. Skipping to the next step.")
                    self.state["step"] += 1
                    self.state["retry_count"] = 0

                save_state(self.state)
                continue

        print("Task completed successfully!")

if __name__ == "__main__":
    task = TaskWithDependencyHandling()
    task.run()
