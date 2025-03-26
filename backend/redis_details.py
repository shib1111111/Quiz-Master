import redis
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Redis config with defaults
REDIS_HOST = os.getenv("CACHE_REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("CACHE_REDIS_PORT", 6379))

# Function to list used databases and count unused ones
def print_used_redis_databases():
    try:
        # Test connection to Redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        if not r.ping():
            raise Exception("Redis PING failed")
        print("Redis server is running and accessible!")

        # Get total number of databases
        num_dbs = int(r.config_get("databases").get("databases", 16))
        print(f"Total databases configured: {num_dbs}")

        # Counters for used and unused databases
        used_dbs = 0

        # Check each database
        for db in range(num_dbs):
            r_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=db)
            keys = r_db.keys("*")
            if keys:
                used_dbs += 1
                print(f"\nDatabase {db}:")
                print(f"  Number of keys: {len(keys)}")
                print(f"  Keys: {keys}")
            r_db.close()

        # Calculate and print totals
        unused_dbs = num_dbs - used_dbs
        print(f"\nTotal used databases: {used_dbs}")
        print(f"Total unused databases: {unused_dbs}")

    except redis.ConnectionError as e:
        print(f"Error: Redis not running at {REDIS_HOST}:{REDIS_PORT} - {e}")
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        r.close()


if __name__ == "__main__":
    
    print_used_redis_databases()