# Conference Mapper 
An entirely unnecessary widget for browsing the locations of academic conferences. Data is sourced from 
[WikiCFP](http://www.wikicfp.com/cfp/home) and organized according to their category structure. The author makes 
no claims as to the validity of the data therein, and the data scraping/cleaning pipeline is provided as-is 
with no guaranteess of accuracy or correctness.

This repository comprises four parts: a web scraper for WikiCFP, a PostgreSQL database, an API to read from that 
database, and a React web application for user interaction.

### Installation
Each subdirectory runs inside its own Docker image. To deploy the full system at once,
```bash
docker compose build && docker compose up
```
This will start the GUI at port 3000 on your machine. 

### TODO
There are items which I haven't had time to address yet, namely
- Set up a better logging architecture, especially for the scraper. Debugging can be finicky.
- Expand the repertoire of data sources, and/or take greater care for comprehensiveness and accuracy of ingesting 
the WikiCFP data.

