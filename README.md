This is a web scraper built using Python's `Scrapy` framework in order to aggregate data from Supreme Court oral argument calendars from 2015-2016 into a standardized JSON format.

This scraper was developed for use by the Legal Information Institute at Cornell Law School in a data pipeline in an effort to make legal information more accessible to the general public.

If you'd like to try it out, download the project, navigate to the root directory of the project (that is, the directory holding the `scrapy.cfg` file) and execute 

`python crawl ArgCalendar -o output.json`

The project will create a JSON file called `output.json` (or whatever value you pass into the -o flag) containing information from the argument calendars.

```
[ 
    {
        "term": the month of cases this calendar refers to,
        "link": link to the calendar,
        "cases": 
            [
                {
                    "date": date the cases took place,
                    "link": link to the case,
                    "docket": case id,
                    "name": case name,
                    "consolidated_with": an array holding names of cases this case is grouped with, if any
                }
            ],
    }
]
```

If you'd like to take a peek at the source code, exercise caution. Government websites are not known for their elegant codebase. 
Since this scraper has to parse the Supreme Court website, things can get ugly. Garbage in, garbage out. ¯\\\_(ツ)\_/¯
