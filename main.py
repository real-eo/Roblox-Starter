from src import paths
import subprocess
import sys


# Get list of Roblox versions and the path to the Roblox Player
robloxVersionsDirectory = paths.get('Roblox', 'versions')
robloxPlayerPath = paths.get('Roblox', 'RobloxPlayerBeta')                                      # | DynamicPath with one variable


# Get the directories within the versions folder
robloxVersions = robloxVersionsDirectory.dirs()
if not robloxVersions:
    print("No Roblox versions found.")
    sys.exit(1)


# Find the newest directory by modification time
newestVersionPath = max(robloxVersions, key=lambda d: d.stat().st_mtime)
print(f"Newest Roblox version: {newestVersionPath.name}")


# Substitute the version in the Roblox Player path
robloxPlayerPath = robloxPlayerPath(version=newestVersionPath.name)


# Check if the Roblox Player executable exists
if not robloxPlayerPath.exists():
    print(f"Roblox Player not found at: {robloxPlayerPath}")
    sys.exit(1)


# Start the Roblox Player
print(f"Starting Roblox Player from: {robloxPlayerPath}")
subprocess.Popen([str(robloxPlayerPath)])                                                       # Convert Path object to string for subprocess
