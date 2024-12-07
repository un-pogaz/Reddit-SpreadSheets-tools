## Reddit SpreadSheets tools

This repository contain various python scripts to fill and manage a Google spreadsheets from a subreddit.

Initialy create for The Nature of Predators community, centralized on [r/NatureofPredators](https://www.reddit.com/r/NatureofPredators/). You can discute about the spreadsheets on this [reddit post](https://www.reddit.com/r/NatureofPredators/comments/18ldgrt/the_nature_of_predators_literary_universe_the_big/).

<hr/>

`new-posts.py` is the main script to retrive and push the lasted new fan-fic's posted on the target subreddit.

`sheet-data.py` is to retrive the posts create by specified authors.

`inspect-sheet.py` little script to check if some error are present in the spreadsheets.

`file-links.py` retrive the data from file containing a list of urls.

`readHTML-authors.py` retrive all the reddits usernames inside a HTML file.

`readHTML-post.py` retrive all the reddits urls inside a HTML file.

To use this script, your need to create a file `config.json` like the one in the `example/` folder. The content of this file follow:

```json
{
  "spreadsheet_id": "<spreadsheet_id>", // the spreadsheet id to wich on to read and push the data
  "settings": {
    "main": {       // a named setting
      "alias": [],  // optional, alias names for this setting
      "name": "<subreddit_name>",   // subreddit or username to target to retrive the posts
      "is_user": false,             // if the name is a subreddit or username
      "kargs": {}   // additionals specific kargs to use, instead of the defaults on the spreadsheet
    }
  }
}
```

The setting "main" is recomanded by default.

<br/>

`common.py` all the real magic is here.

`google_api_client.py` code to interacte with the Google SpreadSheets API.
