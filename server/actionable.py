from collections import defaultdict
from .mock import *
from datetime import datetime, timedelta
import statistics
from sklearn.cluster import DBSCAN
import numpy as np

def get_recommendations(quiet_periods, active_periods, current_time):
    # Assuming quiet_periods and active_periods are sorted lists of (start, end) tuples

    # Define preferred nap times and going out times in seconds from midnight
    preferred_nap_start, preferred_nap_end = 13 * 3600, 17 * 3600  # Between 1 PM and 5 PM
    preferred_going_out_start, preferred_going_out_end = 16 * 3600, 20 * 3600  # Between 4 PM and 8 PM
    
    # Filter periods to only include those within the preferred times and on the current day
    nap_times_today = [p for p in quiet_periods if preferred_nap_start <= p[0] % DAY <= preferred_nap_end and p[1] > current_time]
    going_out_times_today = [p for p in active_periods if preferred_going_out_start <= p[0] % DAY <= preferred_going_out_end and p[1] > current_time]

    # Sort the filtered periods by length (longest to shortest)
    nap_times_sorted = sorted(nap_times_today, key=lambda p: p[1] - p[0], reverse=True)
    going_out_times_sorted = sorted(going_out_times_today, key=lambda p: p[1] - p[0], reverse=True)

    # Return the first (longest) period in each list, or None if there are no periods
    recommended_nap_time = nap_times_sorted[0] if nap_times_sorted else None
    recommended_going_out_time = going_out_times_sorted[0] if going_out_times_sorted else None

    return recommended_nap_time, recommended_going_out_time

def format_period(start, end):
    """Formats the period into a string with day and time."""
    # Convert timestamps to datetime objects
    start_datetime = datetime.fromtimestamp(start)
    end_datetime = datetime.fromtimestamp(end)
    
    # Format the datetime objects into strings
    start_str = start_datetime.strftime('%A %H:%M:%S')
    end_str = end_datetime.strftime('%A %H:%M:%S')
    
    return f"Start: {start_str}, End: {end_str}"

def print_periods(periods):
    """Prints the periods with formatted start and end times."""
    for start, end in periods:
        print(format_period(start, end))

def format_period_to_dict(start, end):
    """ Helper function to format a period into a dictionary. """
    start_str = datetime.fromtimestamp(start).strftime('%A %H:%M')
    duration = (end - start) // 60  # Duration in minutes
    day = datetime.fromtimestamp(start).strftime('%A')
    return {
        "day": day,
        "start": start_str,
        "duration": duration,
        "recommendation": "nap" if duration <= 60 else "going out"
    }

def get_clustered_recommendations(periods, eps_duration, min_duration):
    """
    Get clustered recommendations for periods.

    :param periods: List of tuples with (start, end) timestamps.
    :param eps_duration: Duration value for the DBSCAN epsilon parameter.
    :param min_duration: Minimum duration in minutes for a valid period.
    :return: List of dictionaries with the day, start time, duration, and recommendation type.
    """
    recommendations = []

    # Convert to durations and start times for clustering
    starts = np.array([start for start, _ in periods])
    durations = np.array([(end - start) for start, end in periods])
    features = np.stack((starts, durations), axis=-1)

    # Apply DBSCAN clustering
    db = DBSCAN(eps=eps_duration * 60, min_samples=1).fit(features)  # eps now is in seconds
    labels = db.labels_
    unique_labels = set(labels)

    # Map each cluster label to its periods' indices
    clustered_periods = {label: [] for label in unique_labels if label != -1}
    for idx, label in enumerate(labels):
        if label != -1:
            clustered_periods[label].append(periods[idx])

    # Find the longest period in each cluster for a recommendation
    for label, cluster in clustered_periods.items():
        valid_periods = [period for period in cluster if (period[1] - period[0]) >= min_duration * 60]
        if not valid_periods:
            continue  # Skip clusters without valid periods

        recommended_period = max(valid_periods, key=lambda x: x[1] - x[0])
        recommendations.append(format_period_to_dict(recommended_period[0], recommended_period[1]))

    return recommendations


if __name__ == "__main__":
    mock_data = generate_mock_data(users=10)
    chosen_data = mock_data[0]
    flat_data = [entry for entry in chosen_data['data']]
    quiet_periods, active_periods = analyze_noise_data(flat_data)

    # quiet_periods, active_periods = analyze_noise_data(mock_data)
    print("Quiet periods:")
    print_periods(quiet_periods)
    print("\nActive periods:")
    print_periods(active_periods)

    nap_recommendations = get_clustered_recommendations(quiet_periods, eps_duration=60, min_duration=30)
    going_out_recommendations = get_clustered_recommendations(active_periods, eps_duration=120, min_duration=30)

    # Print results
    for rec in nap_recommendations:
        print(f"Recommended Nap Time: {rec['day']} {rec['start']} for {rec['duration']} minutes.")

    for rec in going_out_recommendations:
        print(f"Recommended Going Out Time: {rec['day']} {rec['start']} for {rec['duration']} minutes.")

    