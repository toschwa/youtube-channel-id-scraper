# YouTube Channel ID Scraper for Glance

Python app that scrapes all YouTube channel IDs which a given channel is subscribed to.  
Output is written to a file named `channels.yml` in the same directory where the script resides, which you can then reference in your `glance.yml` like so:

```
      widgets:
      - type: videos
        channels:
          $include: channels.yml
```

## Pre-requisites
- A working `python3` installation
- The channel ID of the channel from which you'd like to scrape the subscriptions
- Google Cloud API Key
- YouTube Data API enabled

## How to get your channel ID
If you're looking for your own channel ID, the quickest way is to navigate to the [advanced account settings page](https://www.youtube.com/account_advanced) and click on the copy button next to it:

![Advanced account settings](https://github.com/user-attachments/assets/cc2d660b-d305-493d-87aa-d56874eda33b)

Now make sure your Subscriptions are not set to private by going to [account privacy](https://www.youtube.com/account_privacy) and disabling the toggle for "Keep all my subscriptions private":

![Account privacy settings](https://github.com/user-attachments/assets/3e1d7c63-f02c-4099-882c-4f9b7dcdefa6)

If you want to scrape another channel's subscriptions, go to that channel and click on the channel description.  
In the pop-up, scroll all the way down to the share button and click on "Copy Channel ID":

![Copy channel ID from channel description](https://github.com/user-attachments/assets/d2fa2165-82ac-40c2-ad82-c43b6f69e0aa)

This also requires that channel to not have its subscriptions set to private!

## How to enable the YouTube Data API & get an API Key
Go to the [YouTube Data API V3 on Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com) and click on "Enable":

![YouTube Data API V3 on Google Cloud Console](https://github.com/user-attachments/assets/420f5f46-3182-4bc0-912f-fd1cb4ff33d5)

If you haven't used Google Cloud before, this might take a little while, so be patient.

A new Google Cloud Project will be created in the background.

After it's done creating your project and the API metrics page has finished loading, you can click on the credentials tab and then create a new API key:

![Creating an API key](https://github.com/user-attachments/assets/5c43206a-1c73-4185-a517-a4f24a7966d7)

## Running the App

1. **Start the app**  
   Open a terminal, navigate to the project directory, and run:
   ```
   python src/main.py
   ```
   or
   ```
   py src/main.py
   ```

2. **Enter your Channel ID and API Key**  
   When the UI opens, enter your Channel ID and API Key in the provided fields.  
   You can use the provided links in the app to quickly find your Channel ID and API Key.

3. **Save your configuration**  
   Click the "Save Config" button to store your Channel ID and API Key for future use.

4. **Fetch channel subscriptions**  
   Click "Fetch Channels" to retrieve the list of channels your account is subscribed to.  
   The results will appear in a list. You can select which channels to include in the output.

5. **Save selected channels**  
   Click "Save Selected Channels" to write the selected channel IDs to `channels.yml`.

Depending on how many subscriptions the given channel has, this might take a while.  
The expected total and actually fetched total of subscriptions might differ depending on how many channels in the subscription are private or have been deleted.  
After it's done, the `channels.yml` file is ready to be included in your `glance.yml`.

## Automating the process

To sync the `channels.yml` periodically, you can set up a cronjob or scheduled task to run the app in the background.

On most Linux distributions, you can type `crontab -e` and add a new line with your desired schedule and the path where you've put the script.  
For example, if your `glance.yml` resides in the directory `/opt/glance` and you've put the script there as well, your cronjob entry could look like this:
```
# m h  dom mon dow   command
  0 0  *   *   *     python /opt/glance/src/main.py
```

This would run the script every day at midnight.
