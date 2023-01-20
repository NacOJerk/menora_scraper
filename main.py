from scraper import get_all_events_info
from calander_api import CalanderManager, create_hash

SECRET_PATH = "secrets"

if __name__ == "__main__":
    
    events = get_all_events_info()
    events_hashes = [create_hash(*event) for event in events]

    manager = CalanderManager(SECRET_PATH)

    online_events = manager.get_all_events()
    online_events_hashes = [event.get_hash() for event in online_events]

    for event in online_events:
        if event.get_hash() not in events_hashes:
            print("Deleting event, %s" % event)
            manager.delete_event(event)

    
    events_to_upload = []

    for event in events:
        if create_hash(*event) not in online_events_hashes:
            events_to_upload.append(event)
    
    for event in events_to_upload:
        print("Uploading event: %s" % event[0])
        manager.add_menora_event(*event)
    