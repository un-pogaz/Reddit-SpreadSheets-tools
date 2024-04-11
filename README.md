## NoP SpreadSheets tools

[The Nature of Predators](https://new.reddit.com/r/HFY/comments/u19xpa/the_nature_of_predators/) (NoP) is a SF story writed by [u/SpacePaladin15](https://new.reddit.com/user/SpacePaladin15/) ([Patreon](https://www.patreon.com/spacepaladin15/posts)) and published freely on the [r/HFY](https://new.reddit.com/r/HFY/) subreddit.

This repository contain various python scripts to fill and manage the [Fan-fic's spreadsheets](https://docs.google.com/spreadsheets/d/1nOtYmv_d6Qt1tCX_63uE2yWVFs6-G5x_XJ778lD9qyU/) create by The Nature of Predators community, centralized on [r/NatureofPredators](https://new.reddit.com/r/NatureofPredators/). You can discute about the spreadsheets on this [reddit post](https://www.reddit.com/r/NatureofPredators/comments/18ldgrt/the_nature_of_predators_literary_universe_the_big/).

<hr/>

`NoP-new.py` is the main script to retrive and push the lasted new fan-fic's posted on the [r/NatureofPredators](https://new.reddit.com/r/NatureofPredators/) subreddit.

`NoP-new-NSFW.py` is to retrive the lasted new fan-fic's posted on the spiccy sub (yes, there is one).

`NoP-sheet-data.py` is to retrive the posts create by specified authors.

`NoP-inspect-sheet.py` little script to check if some error are present in the spreadsheets.

`NoP-file-links.py` retrive the data from file containing a list of urls.

`NoP-readHTML-authors.py` retrive all the reddits usernames inside a HTML file.

`NoP-readHTML-post.py` retrive all the reddits urls inside a HTML file.

<br/>

`common.py` all the real magic is here.

`google_api_client.py` code to interacte with the Google SpreadSheets API.
