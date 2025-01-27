import pickle
import time
import sys
import importlib
import order_processing_logic  # Import the order processing logic module

def save_state(data, filename="order_state.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_state(filename="order_state.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

class OrderProcessingWithRetry:
    def __init__(self):
        self.state = load_state() or {"step": 1, "retry_count": 0}
        self.max_steps = 5
        self.max_retries = 3

    def reload_task_logic(self):
        """Dynamically reload the order_processing_logic module."""
        if "order_processing_logic" in sys.modules:
            del sys.modules["order_processing_logic"]  # Remove from cache
        global order_processing_logic
        importlib.import_module("order_processing_logic")  # Reimport fresh module
        order_processing_logic = sys.modules["order_processing_logic"]  # Update the reference

    def run(self):
        while self.state["step"] <= self.max_steps:
            try:
                print(f"Processing Step {self.state['step']} (Retry {self.state['retry_count']} of {self.max_retries})...")
                self.reload_task_logic()  # Reload the task logic dynamically

                # Run the task logic for the current step
                success = order_processing_logic.process_step(self.state["step"])

                if success:
                    self.state["step"] += 1
                    self.state["retry_count"] = 0
                    save_state(self.state)
                    print(f"Step {self.state['step'] - 1} completed successfully!")

            except Exception as e:
                print(f"Error: {e}. Resolve the issue and press Enter to continue.")
                input("Press Enter to resume...")  # Wait for user to resolve the issue
                self.state["retry_count"] += 1

                if self.state["retry_count"] > self.max_retries:
                    print(f"Maximum retries reached for Step {self.state['step']}. Skipping to the next step.")
                    self.state["step"] += 1
                    self.state["retry_count"] = 0

                save_state(self.state)
                continue

        print("Order processing completed successfully!")

if __name__ == "__main__":
    order_processor = OrderProcessingWithRetry()
    order_processor.run()
