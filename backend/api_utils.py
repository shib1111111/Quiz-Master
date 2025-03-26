import socket
import os
import psutil
import platform
import subprocess
from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from user_agents import parse  # Make sure to install: pip install pyyaml ua-parser user-agents
from model import User, Admin
from datetime import datetime
import pytz

def get_current_ist():
    """Returns the current datetime in Asia/Kolkata timezone."""
    return datetime.now(pytz.timezone("Asia/Kolkata"))

def admin_required():
    def wrapper(fn):
        from functools import wraps
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['role'] != 'admin':
                return jsonify(msg="Admins only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def user_required():
    def wrapper(fn):
        from functools import wraps
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['role'] != 'user':
                return jsonify(msg="User only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """Fetch the current logged-in user or admin from the JWT identity."""
    identity = get_jwt_identity()  # Email is stored as identity
    user = User.query.filter_by(email=identity).first()
    if user:
        return user

    admin = Admin.query.filter_by(email=identity).first()
    return admin 

def get_mac_from_ip(ip: str):
    try:
        output = subprocess.check_output(f"arp -a {ip}", shell=True).decode('utf-8')
        for line in output.splitlines():
            if ip in line:
                parts = line.split()
                return parts[1]  # Return the MAC address found
    except Exception as e:
        print(f"Error finding MAC address for IP {ip}: {e}")
    return None

def get_mac_address():
    mac_addresses = []
    interfaces = psutil.net_if_addrs()  # Get all network interfaces
    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:  # Check if it's a MAC address
                mac_addresses.append(addr.address)
    return mac_addresses

def get_system_info(request):
    try:
        # Get client IP address
        client_ip = socket.gethostbyname(socket.gethostname())

        # Retrieve MAC addresses for all network interfaces
        mac_addresses = get_mac_address()

        # Get OS info and user-agent info
        os_info = f"{platform.system()} {platform.version()}"
        user_agent_str = request.headers.get("user-agent", "Unknown")
        user_agent = parse(user_agent_str)
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}" if user_agent.browser.family else "Unknown"
        device = f"{user_agent.device.family} ({user_agent.os.family} {user_agent.os.version_string})"

        # System memory and CPU info
        memory_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # Memory in GB
        cpu_cores = os.cpu_count()  # Number of CPU cores

        return {
            "client_ip": client_ip,
            "mac_addresses": mac_addresses,
            "os_info": os_info,
            "browser": browser,
            "device": device,
            "user_agent": user_agent_str,
            "memory_gb": memory_gb,
            "cpu_cores": cpu_cores,
        }
    except Exception as e:
        print(f"Error getting system info: {e}")
        return {
            "client_ip": "Unknown",
            "mac_addresses": [],
            "os_info": "Unknown",
            "browser": "Unknown",
            "device": "Unknown",
            "user_agent": "Unknown",
            "memory_gb": 0,
            "cpu_cores": 0,
        }
