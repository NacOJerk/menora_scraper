# Menora scraper

This is a simple project designed to integrate with google calander.<br>
The project will go and check the <a href="https://www.sportpalace.co.il/menora-mivtachim/%D7%9C%D7%95%D7%97-%D7%90%D7%A8%D7%95%D7%A2%D7%99%D7%9D/">menora website</a>, using the information from the website it will create calander events and that way will let us know which events are going to occur in the upcoming month.

## CLI
The help menu:
```
usage: Menora Scraper [-h] [-d] [-r]

Simple event scraper that adds to calander

optional arguments:
  -h, --help    show this help message and exit
  -d, --delete  Delete all events
  -r, --redo    Delete all events and place them again

No flag combo is allowed
```
All flags are optional

## Setup and usage
First place inside of the secrets folder the following files:
* credentials.json - That can be generated according to this <a href="https://developers.google.com/people/quickstart/python#authorize_credentials_for_a_desktop_application">link</a>, needed scopes are: `[https://www.googleapis.com/auth/calendar.events]`
* attendes.txt - This file will contain a list of the email addresses to summon on the event seperated by new lines

Now for the first time you run the application, it is going to pop up a url for you to agree for the app to use your calander