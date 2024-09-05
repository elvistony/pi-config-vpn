from flask import Flask, render_template, redirect, url_for
import os
import subprocess
import glob
from ledblinks import *

def is_connected_to_internet():
    try:
        # Ping Google's DNS to check for internet connectivity
        subprocess.check_call(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

app = Flask(__name__)

# Directory containing your OpenVPN profiles
VPN_DIR = "/etc/openvpn/client"

# Command templates for starting and stopping VPN profiles
START_CMD = "sudo systemctl start openvpn-client@{}.service"
STOP_CMD = "sudo systemctl stop openvpn-client@{}.service"
STATUS_CMD = "systemctl is-active openvpn-client@{}.service"

# Path to WireGuard configurations
WIREGUARD_CONF_PATH = "/etc/wireguard/*.conf"
WIREGUARD_START_CMD = "sudo wg-quick up {}"
WIREGUARD_STOP_CMD = "sudo wg-quick down {}"


# Function to get available VPN profiles
def get_vpn_profiles():
    profiles = []
    print("OPENVPNDIR:",os.listdir(VPN_DIR))
    for filename in os.listdir(VPN_DIR):
        if filename.endswith(".conf"):
            profiles.append(filename[:-5])  # Strip the '.conf' extension
    return profiles

# @app.route('/')
# def index():
#     profiles = get_vpn_profiles()
#     return render_template('index.html', profiles=profiles)

# Function to check if a VPN profile is running
def is_vpn_running(profile):
    result = subprocess.run(STATUS_CMD.format(profile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8').strip() == 'active'

@app.route('/')
def index():
    openvpn_profiles = get_vpn_profiles()
    openvpn_status = {profile: is_vpn_running(profile) for profile in openvpn_profiles}
    print(openvpn_status)
    
    wireguard_profiles = get_wireguard_profiles()
    wireguard_status = {profile: is_wireguard_running(profile) for profile in wireguard_profiles}
    
    return render_template('index.html', 
                           openvpn_profiles=openvpn_profiles, 
                           openvpn_status=openvpn_status,
                           wireguard_profiles=wireguard_profiles,
                           wireguard_status=wireguard_status)

@app.route('/start/<profile>')
def start_vpn(profile):
    subprocess.call(START_CMD.format(profile), shell=True)
    return redirect(url_for('index'))

@app.route('/stop/<profile>')
def stop_vpn(profile):
    subprocess.call(STOP_CMD.format(profile), shell=True)
    return redirect(url_for('index'))

# Get the list of WireGuard profiles
# def get_wireguard_profiles():
#     return [f.split('/')[-1].replace('.conf', '') for f in glob.glob(WIREGUARD_CONF_PATH)]

def get_wireguard_profiles():
    result = subprocess.run(['sudo', 'ls', '/etc/wireguard'], stdout=subprocess.PIPE)
    profiles = []
    for prof in result.stdout.decode().splitlines():
        if('.conf' in prof):
            profiles.append(prof.replace(".conf",""))
    return profiles

def rename_interface(old_name, new_name="wireguard"):
    try:
        subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', old_name, 'down'], check=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', old_name, 'name', new_name], check=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', 'dev', new_name, 'up'], check=True)
        print(f"Renamed {old_name} to {new_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error renaming interface {old_name}: {e}")

def update_iptables_rules(interface_name):
    try:
        subprocess.run(['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', interface_name, '-j', 'MASQUERADE'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'FORWARD', '-i', interface_name, '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'FORWARD', '-o', interface_name, '-j', 'ACCEPT'], check=True)
        print(f"Updated iptables rules for {interface_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error updating iptables rules for {interface_name}: {e}")

# Check if a specific WireGuard profile is running
def is_wireguard_running(profile):
    result = subprocess.run(['sudo', 'wg', 'show'], stdout=subprocess.PIPE)
    return profile in result.stdout.decode()

# Route to start a WireGuard profile
@app.route('/wireguard/start/<profile>')
def start_wireguard(profile):
    # Stop any running VPN profile before starting this one
    stop_all_vpn()
    
    # Start the selected WireGuard profile
    subprocess.call(WIREGUARD_START_CMD.format(profile), shell=True)
    rename_interface(profile)
    # update_iptables_rules(interface_name)
    
    # Set the LED to 1-second blink (VPN is running)
    set_led_blink_1s()

    return redirect(url_for('index'))

# Route to stop a WireGuard profile
@app.route('/wireguard/stop/<profile>')
def stop_wireguard(profile):
    subprocess.call(WIREGUARD_STOP_CMD.format(profile), shell=True)

    # Check if any VPN is still running (OpenVPN or WireGuard)
    if any(is_vpn_running(p) for p in get_vpn_profiles()) or any(is_wireguard_running(p) for p in get_wireguard_profiles()):
        set_led_blink_1s()  # A VPN is still running
    else:
        # No VPN is running, check internet connection
        if is_connected_to_internet():
            set_led_blink_5s()  # Internet connected but no VPN
        else:
            set_led_off()  # No VPN and no internet

    return redirect(url_for('index'))

# Helper function to stop all VPNs (OpenVPN and WireGuard)
def stop_all_vpn():
    # Stop all OpenVPN profiles
    for profile in get_vpn_profiles():
        if is_vpn_running(profile):
            subprocess.call(STOP_CMD.format(profile), shell=True)
    
    # Stop all WireGuard profiles
    for profile in get_wireguard_profiles():
        if is_wireguard_running(profile):
            subprocess.call(WIREGUARD_STOP_CMD.format(profile), shell=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500, debug=True)
