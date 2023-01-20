from scraper import get_all_events_info
from calander_api import CalanderManager, create_hash
import argparse
import sys
SECRET_PATH = "secrets"

def main():
    parser = argparse.ArgumentParser(
                    prog = 'Menora Scraper',
                    description = 'Simple event scraper that adds to calander',
                    epilog = 'No flag combo is allowed')


    parser.add_argument('-d', '--delete', help='Delete all events', default=False, action='store_true')
    parser.add_argument('-r', '--redo', help='Delete all events and place them again', default=False, action='store_true')

    args = parser.parse_args()

    if args.delete and args.redo:
        parser.print_usage(sys.stderr)
        print("Only one flag allowed")
        return

    events = get_all_events_info()
    events_hashes = [create_hash(*event) for event in events]

    manager = CalanderManager(SECRET_PATH)

    online_events = manager.get_all_events()
    online_events_hashes = [event.get_hash() for event in online_events]

    for event in online_events:
        if event.get_hash() not in events_hashes or args.delete or args.redo:
            print("Deleting event, %s" % event)
            manager.delete_event(event)

    
    if args.delete:
        return

    events_to_upload = []

    for event in events:
        if create_hash(*event) not in online_events_hashes or args.redo:
            events_to_upload.append(event)
    
    for event in events_to_upload:
        print("Uploading event: %s" % event[0])
        manager.add_menora_event(*event)


if __name__ == "__main__":
    main()