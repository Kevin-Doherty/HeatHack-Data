# testbook

We want to produce plots of temperature and RH data from the venues.  There are around 40 venues with different data feeds.  We do not want the venues to be identifiable in case that increases the risk of theft.   The plots should be produced automatically using Jupyter Book.  It would be better if there are 40 books in a list rather than one book with 40 "chapters" because that would reduce processing time - the entire book wouldn't be rebuilt every time one data file changes - but I think this is very difficult.  In practice, the more venues we have at once in the programme and the more of them that have internet, the less likely we are to do enough processing to get charged for it. 

## Two uses cases:

- Internet-connected sensors (this is most venues, we think): Each venue has one device sending data to Thingspeak, and therefore one Thingspeak feed identified by id number with a Read API key.  We only intend to use ThingSpeak for reassurance that the data is there, and port the data to Github for plotting properly.

- Standalone sensors for venues without wifi:  they email data to our automated mailbox every week or two.  There is a unique id for the device included in the header line for each file. Every download is the complete flash contents for the device and therefore may contain data this is redundant with what's already been downloaded.

## Inputs:

:TODO: CK check that I'm describing how the feeds/devices are identified correctly in both cases below, create these CSV files from your database, ensure there is a realistic example data file for standalone version in Github or on Google Drive, depending on what's being written and tested, plus upload a calibration data file to Github.

1. A CSV file with one row per internet-connected venue containing a human-friendly (short alphabetic) code to use in the book to identify the venue, the Thingspeak feed ID and Read API key, and filename for its data archive.
2. A CSV file one with row per standalone venue containing a human-friendly (short alphabetic) code to use in the book to identify the venue, the unique id for the device, and the filename for its data archive.
3. Thingspeak feeds and new data files.
4. DESIRABLE:  hand-authored space use diary as a csv file with the days of the weeks as rows and the times when occupancy changes; what temperature each change requires.  Example:

    Monday, 9:00, 18, 11:00, 10, 17:00, 21, 18:00, 10
    ...

These are their timeswitch settings; it's pairs of times and temperatures (deg C).  For some venues, it might be what they want to achieve rather than actual control they have!  This has real benefits because we could then perhaps highlight times when the users are in the space using vertical bars and shading and summmarise how often they are way over or under their intentions.  They could submit them using a Google form and we can move them over to Github by hand.  This means for some venues, this file is likely to be missing and graphs relying on it (or plot shading and bars) should be omitted.

5. Calibration data sets - rows are timestamps, columns are output temp and RH readings from around 10 devices at a time with a header that uses some value from (1) and (2), uploaded to Github by hand.  

## Data storage

Data archive files, one per venue: 

- a CSV file that always contains all of the data acquired so far for that venue. :TODO: how big will these get over the year at 5 min intervals?  Still small enough to be OK, right?  When do we need to worry about splitting it up - once a year or once a decade?

## Intended automation:

1. Google App Script (standalone only): Once a day, look for all new data email attachments (from standalone venues) and place in a Google Drive. Keep the emailed data in Google Drive for safety but ensure it doesn't get processed twice.  Status:  API calls tested but needs refinement to get the right attachments, those sent to data@heathack.org, which is only an alias.  Probably still needs error logs for us to clean up problems.

:TODO: CK upload here.

2. GitHub Action or Google App Script (standalone only):  Once a day, after (1) will have finished, fetch any new data files (dated since last run) to a temporary filespace on Github. This and (3) are once a day because seeing the data will be on their minds once they've sent it to us.  Status:  method suggested using Google App Script, needs security review and implemented, think it was push and we might need pull.  Could sandbox using a throwaway gmail address if that helps security.

:TODO: upload RK's documentation for how to use App Script to do this.

3. GitHub Action (standalone only):  Once a day, after (2) will have finished, check for new data files on Github, remove redundancy by comparing to existing data archive for that venue, append new data lines to the archive.  Commit changed file and push.  Status:  believed working, automation not yet set up.  TODO: can we use matplotlib to do this more robustly, as we can be surer it works properly under different conditions? Otherwise, does it error log for us?

:TODO: workflow doesn't work, no such thing as temporary filespace on Github? - does it help to combine (2) and (3)  and has to be Github Action? Or maybe we can commit the "temporary" files and put up with the extra processing.   

4.  Github Action (internet-connected only): Once a week, traverse the rows of the CSV file listing the internet-connected venues.  Check the last timestamp in the data archive for the venue and using the feed id and Read API, fetch all new data from the feed.  Append to the archive.   This is once a week because we expect daily data coming in and don't want to get too close to the processing limit that will trigger payments to Github.

5. GitHub Action (both): triggered on repository changes, build the book containing the plots on Github Pages. Status: experimentation towards what we want only.

## Desired plots

The plots are about doing what's usable and possible easily - we should specify them functionally with minimal requirements and what we'd ideally like to see.  Even just the basic plot with pan and zoom is a step up from what the users usually have.

1. basic plot as below.

1.  a plot that lets people judge whether they are keeping their users within comfortable temperature bounds when the space is in use.  Minimally, this is a horizontal line at 16C, the Child Care Commission minimum.  If we can handle space diaries and manage vertical bars with shading plus perhaps a text label with the demand temperature, that would be brilliant. Summaries of performance for each timeslot  (Monday 9-11: 90% within 1C of 18C or some summary plot, and so on).

2. dropdown a start date and end date (or always a week or month at a time?), choose temperature or RH, and just create a basic plot that way with the usual plotly pan/zoom etc options.  This is to make it easier to explore the data; after a year the initial plots will be hard to read if we use the whole data archive.   

3.  Calibration plot - graph the 10 devices against each other with a legend that lets individual devices be hidden.

 ## Implementation notes

Plotly express is syntactic sugar over graph_objects; drop down into the graph_objects themselves allows more possibilities for formatting.  Some very useful plotting capabilities, like dropdown menus allowing date choices, might require further libraries (that start to be paid quickly, I think), cf Dash.  UI controls don't necessarily need to be in the plots themselves.

- minimal version, horizontal line at 16C (the child care commission minimum).
- (not relevant for this particular data, just a test).  This plot is also useful for assessing temperature control, especially on a short test for overshoot that tries holding a building at a temperature - cheapest in autumn.  We'll want similar plots showing suggested RH bounds for the comfort of people and for organs/oil paintings and so on.

Note pan, zoom, etc - not beautiful, but even this basic level of plot would work.  I wonder whether they'll be worried by the rogue readings.  We could probably remove based on improbably fast temperature changes.

On our current thingspeak feeds, temperature is field1 and RH is field2 - we may be able to assign better names in future.  I think I had to change the time format so that's either some scripting or a configuration change on the platform.



Information about non-plotly approaches:  https://jupyterbook.org/interactive/interactive.html One consideration is whether they're going to need internet access to look at graphs - they might not have that when they're together if they meet on the premises.  Altair sounded like it might be useful in that situation.

:TODO: find out if we can hide the code.

The graphs look terrible in pdf as generated via html.

