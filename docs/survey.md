# Survey Integration

To integrate survey questions, the [GET](https://en.wikipedia.org/wiki/Query_string) parameter `sid` can be appended to the `/upload` page. The content of this parameter (e.g., the id that a survey tool uses to match the survey response to the submitted donation) is then stored along with the donated data.

However, this connection is merely an integration but rather a change in platforms. The "user journey" (from survey to donation platform to OSD2F and potentially back to survey) is interrupted several times and, potentially, participants are lost along the way. 

An alternative is thus to *really* integrate OSD2F into an online survey tool. One such tool is [SoSci Survey](https://www.soscisurvey.de/en/index) which now offers a particular OSD2F question type to be integrated into the usual flow of questions. This not only allows for a smoother "user journey" but also to make use of all the survey tool's functionality, such as multi-lingual questionnaires, randomization, or uniform design that is also responsive to several device sizes.

This page describes how this integration is specified. Ideally, this should help other survey tools to integrate OSD2F in similar vein.

## Workflow

1. _OSD2F_: Is deployed and runs on a server with the survey mode enabled. An enabled survey mode allows for the survey tool to contact OSD2F directly. The mode also disables the usual user interface to the platform. Furthermore, an environment variable `OSD2F_SURVEY_TOKEN` has to be specified for basic authentication reasons. 
1. **Survey Tool**: During questionnaire setup, the URL to the OSD2F server is entered by the user. If necessary, the survey tool could then already reach out to the OSD2F server to check for version compatibility. No token is required for this step.
1. **Survey Tool**: After setup, the survey tool can contact the OSD2F server along with (a) the secret token as well as (b) configuration, (c) message/language details, and (d) a JavaScript callback function name. As a response, OSD2F offers a status as well as instructions on (a) the HTML code to present and (b) the JavaScript code to embed. 
1. **Survey Tool**: During actual participation, the OSD2F-provided HTML code is presented and the OSD2F-provided JavaScript code is embedded. Therein, an identifier for the current respondent can be placed (usually, this is a pseudonymized ID). If a user uploads something, OSD2F receives the data through its `/upload` URL endpoint and is thus able to directly manipulate the HTML code to present the uploaded (anonymized) data and to allow filter modalities. Ultimately, users consent and click the donate button (which is presented in the survey tool but originates from OSD2F).
1. _OSD2F_: Through its JavaScript embedding, OSD2F is able to, in case of errors or in case of final success, call the survey tool's callback function.
1. **Survey Tool**: Once the callback function is called, the survey tool could proceed to the next page or allow the user to continue.


## Technological Specification

### OSD2F server configuration

OSD2F has to be run in "survey" mode. This is ensured through the respective mode setting (e.g., `-m Survey`). Moreover, a secret server token has to be set, against which the survey tool can "authenticate." The secret server token has to be set as a `OSD2F_SURVEY_TOKEN` environment variable. 

If you were to [deploy OSD2F as a container](deploying_as_a_container.md), you could, for example, use the following configuration:

```bash
docker run -it \
    -e OSD2F_MODE="Survey" \
    -e OSD2F_BASIC_AUTH='user;pass' \
    -e OSD2F_SECRET="a big secret here" \
    -e OSD2F_DB_URL="sqlite://:memory:" \
    -e OSD2F_SURVEY_TOKEN="another big secret" \
    -p 8000:8000 \
    osd2f
```

### survey tool server configuration

The survey tool has to have [libarchive.js](https://github.com/nika-begiashvili/libarchivejs) installed (i.e., placed in a public directory, ready to be accessible). This includes three files, the `worker-bundle.js` as well as, in a `wasm-gen/`-entitled sub directory to the worker bundle, `libarchive.js` and `libarchive.wasm`. The library allows JavaScript to directly connect to an instance of the [libarchive C package](https://github.com/libarchive/libarchive) that is capable of unpacking ZIP files. As we try not to send participants' raw data through the web, this approach is taken to unpack ZIP files without any connection to OSD2F's Python files. 

### seminal setup version compatibility check from survey tool to OSD2F

To check for reachability and compatibility, a simple *GET* request can be posed to the OSD2F installation's base URL with the endpoint `/survey`. The OSD2F installation will then respond with a rather simple response.

```json
{
  "success": true,
  "error": "",
  "version": ""
}
```

#### parameters

- success: true if server has not run into any errors / limitations
- error: string, empty if success is true, otherwise contains error message (in English)
- version: string, version of the running OSD2F system

### setup request from survey tool to OSD2F

The request is directed at the OSD2F installation's base URL with the endpoint `/survey` as a *POST* request with the following parameters.

```json
{
  "token": "",
  "project_title": "",
  "admin_email": "",
  "js_callback_after_upload": "callback_function_name",
  "upload": {
    "(^|/|\\)comments.json": {
      "in_key": "comment_information",
      "anonymizers": [
        { "redact_text": "" }
      ],
      "accepted_fields": [
        "timestamp",
        "title",
        "information.comment.comment_text"
      ]
    }
  },
  "content": {
    "blocks": [],
    "upload_box": {
      "explanation": [],
      "header": ""
    },
    "donate_button": "",
    "empty_selection": "",
    "file_indicator_text": "",
    "inspect_button": "",
    "preview_component": {
      "entries_in_file_text": "",
      "explanation": [],
      "next_file_button": "",
      "previous_file_button": "",
      "remove_rows_button": "",
      "search_box_placeholder": "",
      "search_prompt": "",
      "title": ""
    },
    "consent_popup": {
      "accept_button": "",
      "decline_button": "",
      "end_text": "",
      "lead": "",
      "points": [],
      "title": ""
    },
    "processing_text": "",
    "thanks_text": ""
  }
}
```

#### parameters

- token: the exact same survey token configured server-side (see "server configuration" above)
- project_title: a brief textual name to be able to identify the configuration in the back
- admin_email: an email address of the researcher in question
- js_callback: a JavaScript function name (without brackets or parameters) that is called when the integration runs into problems or ends successfully; the callback function gets called with up to three parameters:
  - parameter 1: success, either true or false, required
  - parameter 2: error, string, empty string if success, error message otherwise, required
  - parameter 3: status, object `{}` with donated file names as keys and objects as values, each with a `n_donated` and `n_deleted` keys and integers as values, optional (only if `success` is `true`), example: 
    ```javascript
    js_callback(true, "", {
      "commments.json": { "n_donated": 12, "n_deleted": 0 },
      "ads_clicks.json": { "n_donated": 0, "n_deleted": 3 },
      "posts_1.json": { "n_donated": 418, "n_deleted": 3 }
    });
    ```
- upload: key-value map of files and respective patterns as configured in *default_upload_settings.yaml* for the respective OSD2F version (the example includes the mock-data *comments.json*)
- content: key-value map of language aspects as configured in *default_content_settings.yaml* for the respective OSD2F version


### setup response from OSD2F to survey tool

The response to the request is a JSON object that looks as follows.

```json
{
  "success": true,
  "error": "",
  "config_id_content": "",
  "config_id_upload": "",
  "head_inclusion": [],
  "html_embed": "",
  "js_embed": "",
  "js_embed_placeholder_surveyid": "",
  "js_embed_placeholder_libarchivejs": ""
}
```

#### parameters

- success: true if server has not run into any errors / limitations
- error: string, empty if success is true, otherwise contains error message (in English)
- config_id_content: a (numeric) identifier of the now-server-stored content configuration, for logging purposes only
- config_id_upload: a (numeric) identifier of the now-server-stored upload configuration, for logging purposes only
- head_inclusion: array with one of two types of instructions, both of which need to be included in the HTML header when a participant answers a data donation item
  - FQDN to JavaScript file (string, starting with `http://` or `https://` and ending in `.js`) (could, by the survey tool, be downloaded and served locally)
  - FQDN to CSS file (string, starting with `http://` or `https://` and ending in `.css`) to be included in the HTML header when a participant answers a data donation item (could, by the survey tool, be downloaded and served locally)
- html_embed: string with HTML code to be put into the position where the data donation item is placed
- js_embed: string with JavaScript code to be run after (!) the embedded HTML code is present in the DOM (either include it, encapsulated in `<script>` tags after the *html_embed* part or place it in a `window.onload` pipeline)
- js_embed_placeholder_surveyid: inside *js_embed*, a placeholder is included which, in production, should be replaced with an identifier from the survey tool to later be able to link survey responses with donated data; this parameter holds the placeholder as a string (usually, this is `### SID ###`)
- js_embed_placeholder_libarchivejs: inside *js_embed*, another placeholder is included which, if the survey tool and OSD2F run under separate domains, has to be replaced with the correct domain path to libarchive.js' *worker-bundle.js* (usually, the placeholder is `### LIBARCHIVE.JS ###` and should be replaced with something along the lines of `/static/js/libarchive.js/dist/worker-bundle.js`)
