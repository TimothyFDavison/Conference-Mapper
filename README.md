# Conference Mapper 
An entirely unnecessary widget for browsing the locations of academic conferences. Data is sourced from 
[WikiCFP](http://www.wikicfp.com/cfp/home) and organized according to WikiCFP's category structure. The author makes 
no claims as to the validity of the data therein, and the data scraping/cleaning pipeline is provided as-is 
with no guaranteess of accuracy or correctness.

This repository comprises four parts: a web scraper for WikiCFP, a PostgreSQL database, an API to read from that 
database, and a React web application for user interaction.

### Installation
Each subdirectory runs inside its own Docker image. To deploy the full system at once,
```bash
docker compose build && docker compose up
```
This will start the GUI at port 3000 on your machine. Alternatively, you can build the components individually. See 
the subdirectories' respective READMEs.

### Deployment 
This app has been deployed on an AWS EC2 instance to https://conference-mapper.com.

The steps for deployment included,
- Setting up an AWS EC2 instance
  - Copying the code to that instance
  - Obtaining a certificate from Let's Encrypt to support HTTPS
  - Configuring nginx for port routing
  - Building and running the Docker images
- Setting up the domain name,
  - Purchasing domain from a third party
  - Created a Route 53 hosted zone on AWS
  - Creating DNS records to associate the domain with the EC2 instance

For posterity, the nginx configuration that I'm using is below:
```yaml
```

### To-Do
There area few items which I haven't had time to address yet, namely:
- Set up a better logging architecture, especially for the scraper. Scraping is brittle and debugging can be finicky.
- Refactor the frontend for better separation of concerns and functional components. Especially the map filters
and the associated CSS for each component.
- Stop the filters window from closing when you "deselect all" of the selected categories. 

