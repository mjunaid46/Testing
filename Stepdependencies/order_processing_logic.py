import random  # To simulate random failures

def process_step(step):
    """Process a specific step in the order processing."""
    if step == 1:
        print("Verifying payment...")
        # if random.choice([True, False]):  # Simulate random failure
        #     raise Exception("Payment verification failed.")
        return True
    
    elif step == 2:
        print("Preparing items for shipment...")
        # if random.choice([True, False]):  # Simulate random failure
        #     raise Exception("Inventory issue encountered.")
        return True
    
    elif step == 3:
        print("Generating invoice...")
        # if random.choice([True, False]):  # Simulate random failure
        #     raise Exception("Failed to generate invoice.")
        return True
    
    elif step == 4:
        print("Updating inventory...")
        # if random.choice([True, False]):  # Simulate random failure
        # raise Exception("Failed to update inventory.")
        return True
    
    elif step == 5:
        print("Sending shipment confirmation...")
        # if random.choice([True, False]):  # Simulate random failure
        #     raise Exception("Shipping confirmation failed.")
        return True

    return False
