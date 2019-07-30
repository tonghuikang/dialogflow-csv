# Dialogflow to Spreadsheet converter.

Given a `.zip` file exported from Dialogflow, this code converts and uploads it into Google Sheets.


### To deploy converter endpoint at Google Cloud Functions
`token.pickle` needs to be inside `./df-to-csv` is necessary to create, edit and make public Google Sheets.
Reference: https://developers.google.com/sheets/api/quickstart/python

Log in to you Google account with GCP CLI ```gcloud auth login```. 
You need a billing account to run Cloud Functions even though you are unlikely to break the free tier.
> Cloud Functions provides a perpetual free tier for compute-time resources, which includes 
an allocation of both GB-seconds and GHz-seconds. In addition to the 2 million invocations, 
the free tier provides 400,000 GB-seconds, 200,000 GHz-seconds of compute time and 5GB of 
Internet egress traffic per month. Note that even for free tier usage, we require a valid 
billing account.
 

Inside the folder `df-to_csv` and `csv-to-df` respectively, run:
```gcloud functions deploy df_to_csv --runtime python37 --trigger-http```
```gcloud functions deploy csv_to_df --runtime python37 --trigger-http```

A working version should be available on https://dialogflow-csv-stable.glitch.me/

Demo video on its usage to be included soon.

