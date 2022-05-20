# Sheet Links To Discord

A custom-built Discord bot using `discord.py` that shares links to helpful resources on the "Sri Lankan Data Enthusiasts" Discord server.

## Brief Description of the Bot's Operation

The bot uses `pygsheets` to periodically load a Google Sheet of links with associated titles, descriptions, and image URLs. Since the Google Sheet is periodically loaded (according to a specified timer), the document can be continuously updated with no need to amend any code.

The bot uses the scheduled dates and times provided on the same document to determine when/if a link should be shared. Links are shared as rich "embed" messages as opposed to standard chat messages to distinguish them from the latter.

A flag is updated on the Google Sheet when a link is shared to prevent the same link being shared multiple times.

## Structure of the Google Sheet

|id |to_publish_date_lka|to_publish_time_lka|url                 |title  |message                                                      |image_url                                 |posted_indicator|
|---|-------------------|-------------------|--------------------|-------|-------------------------------------------------------------|------------------------------------------|----------------|
|1  |5/21/22            |12                 |https://datatau.net/|DataTau|A fan of Hacker News? This is the equivalent for us data folk|https://datatau.net/static/img/datatau.png|0               |

* `to_publish_time_lka` is in 24 hour format.
* `posted_indicator` is updated to `1` when the link is shared.

## Potential Future Enhancements

* Have the bot automatically pull an image from the link's meta tags so I don't have to manually do it myself.
* Allow users to browse through links that have already been shared (perhaps the last 10).