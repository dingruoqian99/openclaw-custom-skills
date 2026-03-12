import argparse
import requests
import json
import datetime
import os
import sys

# Credentials
API_KEY = "gzr8f1ydiprcomooksnjcims"
ATHLETE_ID = "i512538"
BASE_URL = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}"

def get_auth():
    return ("API_KEY", API_KEY)

def get_headers():
    return {
        "Content-Type": "application/json"
    }

def get_activities(args):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=args.days)
    end_date = today
    
    url = f"{BASE_URL}/activities"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat()
    }
    
    response = requests.get(url, auth=get_auth(), headers=get_headers(), params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    activities = response.json()
    if args.limit and len(activities) > args.limit:
        activities = activities[:args.limit]
        
    print(json.dumps(activities, indent=2))

def get_activity_details(args):
    url = f"{BASE_URL}/activities/{args.id}"
    response = requests.get(url, auth=get_auth(), headers=get_headers())
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    print(json.dumps(response.json(), indent=2))

def get_wellness(args):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=args.days)
    end_date = today
    
    url = f"{BASE_URL}/wellness"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat()
    }
    
    response = requests.get(url, auth=get_auth(), headers=get_headers(), params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    print(json.dumps(response.json(), indent=2))

def get_activities_csv(args):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=args.days)
    end_date = today
    
    url = f"{BASE_URL}/activities.csv"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat()
    }
    
    response = requests.get(url, auth=get_auth(), params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    print(response.text)

def get_events(args):
    today = datetime.date.today()
    start_date = today
    end_date = today + datetime.timedelta(days=args.days)
    
    url = f"{BASE_URL}/events"
    params = {
        "oldest": start_date.isoformat(),
        "newest": end_date.isoformat()
    }
    
    response = requests.get(url, auth=get_auth(), headers=get_headers(), params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    print(json.dumps(response.json(), indent=2))

def update_event(args):
    url = f"{BASE_URL}/events/{args.id}"
    
    # Fetch existing event first to preserve fields
    existing = requests.get(url, auth=get_auth(), headers=get_headers())
    if existing.status_code != 200:
        print(f"Error fetching event: {existing.status_code} - {existing.text}")
        return
    
    event_data = existing.json()
    
    # Parse the updates from the command line (expected as key=value pairs)
    # This is a basic implementation for specific fields we know we want to change
    # Ideally we'd pass a full JSON, but for CLI ease we'll do specific flags
    
    if args.name:
        event_data['name'] = args.name
    if args.description:
        event_data['description'] = args.description
        
    # Update workout structure if provided (simplified for this specific use case)
    # We are hacking this a bit to support the specific request of changing reps/dist
    if args.workout_doc:
        event_data['workout_doc'] = json.loads(args.workout_doc)

    response = requests.put(url, auth=get_auth(), headers=get_headers(), json=event_data)
    if response.status_code != 200:
        print(f"Error updating: {response.status_code} - {response.text}")
        return
    print(json.dumps(response.json(), indent=2))

def main():
    parser = argparse.ArgumentParser(description="Intervals.icu API Tool")
    subparsers = parser.add_subparsers(dest="command")

    # get_activities
    parser_activities = subparsers.add_parser("get_activities")
    parser_activities.add_argument("--days", type=int, default=30, help="Number of days to look back")
    parser_activities.add_argument("--limit", type=int, default=50, help="Max number of activities")

    # get_activity_details
    parser_details = subparsers.add_parser("get_activity_details")
    parser_details.add_argument("id", type=str, help="Activity ID")

    # get_wellness
    parser_wellness = subparsers.add_parser("get_wellness")
    parser_wellness.add_argument("--days", type=int, default=14, help="Number of days to look back")

    # get_activities_csv
    parser_csv = subparsers.add_parser("get_activities_csv")
    parser_csv.add_argument("--days", type=int, default=30, help="Number of days to look back")
    
    # get_events
    parser_events = subparsers.add_parser("get_events")
    parser_events.add_argument("--days", type=int, default=7, help="Number of days to look ahead")

    # update_event
    parser_update = subparsers.add_parser("update_event")
    parser_update.add_argument("id", type=str, help="Event ID")
    parser_update.add_argument("--name", type=str, help="New name")
    parser_update.add_argument("--description", type=str, help="New description")
    parser_update.add_argument("--workout_doc", type=str, help="JSON string of workout_doc")

    args = parser.parse_args()

    if args.command == "get_activities":
        get_activities(args)
    elif args.command == "get_activity_details":
        get_activity_details(args)
    elif args.command == "get_wellness":
        get_wellness(args)
    elif args.command == "get_activities_csv":
        get_activities_csv(args)
    elif args.command == "get_events":
        get_events(args)
    elif args.command == "update_event":
        update_event(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
