# Conference Mapper 
Fun little app to visualize and search for upcoming conferences.

## Todo

**UI Cleanup**
- ~~Clean up UI buttons~~
- ~~Break out components from application~~
- ~~Move API address out of Map.js, into config somewhere~~

**Bug Fixes**
- Set up timers for operations in the cleaning process: after a first geolocation pass, should 
be much faster than it is
- Fix "open CFP" boolean search

**Deployment** 
- ~~Set up the automatic database refresh~~
- ~~Finish Docker postgres persistence/initialization~~
- Update READMEs for all components
- Remove dummy credentials
- Set start date to date of search

**New Features**
- ~~Better date control for past conferences~~
- Add LLM chat widget
  - Host an LLM in vLLM 
  - Allow DB search, location, date filter as tools
