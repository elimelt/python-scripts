# Scripts for Google Forms

## usage:

### get-form-data

Note that you need to have logged into the form and viewed in edit mode. the form url should look like `https://docs.google.com/forms/d/{formID}/edit`. Generate an auth token using Google's [OAuth 2.0 playground](https://developers.google.com/oauthplayground), giving access to the following:

- /auth/drive.readonly
- /auth/forms.body.readonlyi
- /auth/forms.responses.readonly


```bash
python ./get-form-data.py <url> <auth-token> 
``` 

### parse-responses

Reads response data from stdin, outputting the parsed response data to stdout based on availability

```bash
python ./get-form-data.py <url> <auth-token> | python parse-responses.py
```

### group

Reads parsed data from stdin and outputs groupings to maximize overlapping in schedules to stdout

```bash
python ./get-form-data.py <url> <auth-token> | python parse-responses.py | python group.py
```



## tips

use `jq` for prettier output

```bash
python ./get-form-data.py <url> <auth-token> | python parse-responses.py | python group.py | jq
```
