# Conference Mapper 

I want to be able to find conferences that I should apply to based on their location. Some filters might include,
- Conference category (e.g. AI, information sciences, mathematics...)
- Conference dates
- Whether the call for proposals is open, and due dates

The conferences should render as pins on a Google Earth-style map render.

## Step One: Scrape the Data
I can scrape *some* conference data from sources like,
- http://www.wikicfp.com, for consistently formatted tables
- conferencealerts.com, for more variety of disciplines, but also more clutter (requiring DOM filtering)
- papercrowd.com, if I want to reverse engineer JSON endpoints to get data reliably (lots of dynamic JS frontend)

## Step Two: Extract Key Information

- Location (city, country) -> use lookup to identify GPS coordinates
- Conference name
- Conference category
- Conference dates
- Call for papers open/closed
- [Optional] Select a pinned conference, then create a chat window that routes to GPT with internet connectivity, so that you can ask questions about the conference

## Step Three: Render

Display a render similar to Google Earth or Google Maps. Allow for search and filter of conferences.

## System Design
- We take a preset list of conference categories
- A cron job runs a nightly scraper to retrieve and store data from each
  - The raw output is piped into postgres, sorted by category
  - A script goes through and creates or updates a new table, adding fields like lat/long
  - Lat/long is stored in a hash index in postgres for cached values, or computed on the spot otherwise
  - The result is a table for each conference category with a set of cleaned values
- Next, build a frontend with folium as a mapping capability
- Then put it all in a Docker container and deploy it 