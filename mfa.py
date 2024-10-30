from termcolor import colored
import sys
import re
from collections import defaultdict

def finder(file_path):
    # Define regex patterns to find DeviceName, DeviceToken, and PhoneAppVersion values
    device_name_pattern = r'"DeviceName":"([^"]+)"'
    device_token_pattern = r'"DeviceToken":"([^"]+)"'
    app_version_pattern = r'"PhoneAppVersion":"([^"]+)"'

    # Read the content of the file
    with open(file_path, 'r') as file:
        input_string = file.read()

    # Clean and process the string
    input_string = re.sub(r'\\', '', input_string)  # Remove escaped backslashes
    input_string = input_string.replace('\n', '')   # Remove newlines

    # Find all matches for DeviceName, DeviceToken, and PhoneAppVersion
    device_names = re.findall(device_name_pattern, input_string)
    device_tokens = re.findall(device_token_pattern, input_string)
    app_versions = re.findall(app_version_pattern, input_string)

    # Check that the number of DeviceNames matches the number of DeviceTokens
    if len(device_names) != len(device_tokens) or len(device_names) != len(app_versions):
        raise ValueError("Mismatch between number of DeviceNames, DeviceTokens, and PhoneAppVersions")

    # Combine DeviceNames, DeviceTokens, and PhoneAppVersions into a list of tuples
    device_data = list(zip(device_names, device_tokens, app_versions))

    # Count occurrences of each DeviceToken and track the devices, app versions for each token
    token_count = defaultdict(int)
    device_for_token = defaultdict(set)
    version_for_token = defaultdict(set)
    device_version_for_token = defaultdict(lambda: defaultdict(set))

    for name, token, version in device_data:
        token_count[token] += 1
        device_for_token[token].add(name)
        version_for_token[token].add(version)
        device_version_for_token[token][name].add(version)

    # Find tokens with exactly 1 occurrence
    tokens_with_one_occurrence = [token for token, count in token_count.items() if count == 1]

    # Find devices associated with tokens that occur only once
    devices_with_single_token = defaultdict(set)
    for token in tokens_with_one_occurrence:
        for device in device_for_token[token]:
            devices_with_single_token[device].add(token)

    # Alert for devices with token changes
    print(colored("Alert: Devices with token changes:", 'red'))
    device_token_map = defaultdict(set)
    for token, devices in device_for_token.items():
        for device in devices:
            device_token_map[device].add(token)

    token_change_alerts = []
    for device, tokens in device_token_map.items():
        if len(tokens) > 1:
            # Create a message indicating token changes
            sorted_tokens = sorted(tokens)
            changes = [f"from {sorted_tokens[i]} to {sorted_tokens[i+1]}" for i in range(len(sorted_tokens) - 1)]
            changes_message = ', '.join(changes)
            token_change_alerts.append(f"DeviceName: {device} has had a token change {changes_message}")

    if token_change_alerts:
        for alert in token_change_alerts:
            print(colored(alert, 'red'))
    else:
        print(colored("No token changes detected for devices", 'green'))

    # Find tokens with exactly 2 occurrences
    tokens_with_two_occurrences = [token for token, count in token_count.items() if count == 2]

    # Check if the corresponding DeviceNames and app versions match for tokens with 2 occurrences
    valid_tokens = []
    for token in tokens_with_two_occurrences:
        if len(device_for_token[token]) == 1 and len(version_for_token[token]) == 1:
            # Add a tuple of (token, device_name, app_version) to the valid_tokens list
            valid_tokens.append((token, next(iter(device_for_token[token])), next(iter(version_for_token[token]))))

    # Print results
    print("\nTokens with exactly 2 occurrences and matching DeviceNames and App Versions:")
    for token, device_name, app_version in valid_tokens:
        print(colored(f"DeviceName: {device_name}, Token: {token}, App Version: {app_version}", 'green'))
        print(" ")

    ver_diff = False
    # Alert for device version variations
    print("Alert: Devices with different app versions for the same token:")
    for token, devices in device_version_for_token.items():
        for device, versions in devices.items():
            if len(versions) > 1:
                print(colored(f"DeviceName: {device}, Token: {token} has versions: {', '.join(versions)}", 'red'))
                ver_diff = True 
    if not ver_diff:
        print(colored("No changes in device app versions", 'green'))

if __name__ == "__main__":
    import sys

    # Get the file path from the command-line arguments
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'data.txt'

    # Call the finder function with the determined file path
    finder(file_path)
