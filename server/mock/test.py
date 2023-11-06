from scipy.stats import norm

def calculate_class_weights(mean_db, sd_db, num_classes):
    # Get the percentile value for 'neutral' which is at the 50th percentile
    neutral_weight = norm.cdf(0.5, mean_db, sd_db)
    
    # Calculate the remaining weight to be distributed among other classes
    remaining_weight = 1.0 - neutral_weight
    
    # Distribute the remaining weight evenly among the other classes
    other_weights = [remaining_weight / (num_classes - 1)] * (num_classes - 1)
    
    # Combine the weights for 'neutral' and the other classes
    class_weights = other_weights + [neutral_weight]
    
    # Since we want 'neutral' to be at the bottom 50%, make sure it's the last weight
    class_weights[-1], class_weights[0] = class_weights[0], class_weights[-1]
    
    return class_weights

# Define your mean and standard deviation for decibels
mean_db = 65.0
sd_db = 10.0

# Calculate the weights for 9 sound classes plus 'neutral'
weights = calculate_class_weights(mean_db, sd_db, 10)

print(weights)
