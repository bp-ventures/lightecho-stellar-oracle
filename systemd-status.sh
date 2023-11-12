#!/usr/bin/env bash

# Specify the services you want to check
services=("feed_all_from_db.service" "feed_all_from_db.timer" "feed_bulk_from_db.service" "feed_bulk_from_db.timer" "bump_instance.service" "bump_instance.timer")
systemctl_cmd="systemctl --user"

# Function to display a table header
print_header() {
    printf "%-30s %-10s %-15s %-15s\n" "Service" "Enabled" "Status" "Uptime"
    printf "%-30s %-10s %-15s %-15s\n" "-------" "-------" "------" "------"
}

# Function to display the status, uptime, and whether the unit is enabled or not
print_status() {
    for service in "${services[@]}"; do
        status=$($systemctl_cmd is-active --quiet $service && echo "Running" || echo "Inactive")
        uptime=$($systemctl_cmd show -p ActiveEnterTimestamp --value $service)
        enabled=$($systemctl_cmd is-enabled --quiet $service && echo "Yes" || echo "No")

        # Calculate the uptime in a readable format
        if [ "$status" == "Running" ]; then
            current_time=$(date +%s)
            start_time=$(date --date="$uptime" +%s)
            uptime_seconds=$((current_time - start_time))
            formatted_uptime=$(date -u -d @"$uptime_seconds" +'%H:%M:%S')
        else
            formatted_uptime="N/A"
        fi

        printf "%-30s %-10s %-15s %-15s\n" "$service" "$enabled" "$status" "$formatted_uptime"
    done
}

# Main script
print_header
print_status
