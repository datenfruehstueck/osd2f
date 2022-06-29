# Survey Integration

To integrate survey questions, the [GET](https://en.wikipedia.org/wiki/Query_string) parameter `sid` can be appended to the `/upload` page. The content of this parameter (e.g., the id that a survey tool uses to match the survey response to the submitted donation) is then stored along with the donated data.

However, this connection is merely an integration but rather a change in platforms. The "user journey" (from survey to donation platform to OSD2F and potentially back to survey) is interrupted several times and, potentially, participants are lost along the way. 

An alternative is thus to *really* integrate OSD2F into an online survey tool. One such tool is [SoSci Survey](https://www.soscisurvey.de/en/index) which now offers a particular OSD2F question type to be integrated into the usual flow of questions. This not only allows for a smoother "user journey" but also to make use of all the survey tool's functionality, such as multi-lingual questionnaires, randomization, or uniform design that is also responsive to several device sizes.

This page describes how this integration is specified. Ideally, this should help other survey tools to integrate OSD2F in similar vein.


## Workflow

1. OSD2F: Is deployed and runs on a server with the survey mode enabled. An enabled survey mode allows for the survey tool to contact OSD2F directly. The mode also prohibits any other public requests to the platform.
1. Survey Tool: During questionnaire setup, the URL to the OSD2F server is entered by the user. If necessary, the survey tool could then already reach out to the OSD2F server to check for version compatibility.
1. Survey Tool: After setup, the the survey tool can then contact the OSD2F server along with (a) configuration, (b) message/language details, and (c) a JavaScript callback function name. As a response, OSD2F offers a status as well as instructions on (a) the HTML code to present and (b) the JavaScript code to embed. 
1. Survey Tool: During actual participation, the OSD2F-provided HTML code is presented and the OSD2F-provided JavaScript code is embedded. If a user uploads something, OSD2F receives the data through its `/upload` URL endpoint and is thus able to directly manipulate the HTML code to present the uploaded (anonymized) data and to allow filter modalities. Ultimately, users consent and click the donate button (which is presented in the survey tool but originates from OSD2F).
1. OSD2F: Through its JavaScript embedding, OSD2F is able to, in case of errors or in case of final success, call the survey tool's callback function.
1. Survey Tool: Once the callback function is called, the survey tool could proceed to the next page or allow the user to continue.


## Technological Specification

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
  "project_title": "",
  "admin_email": "",
  "js_callback": "callback_function_name",
  "i18n": {
    "consent_popup": {
      "accept_button": "",
      "decline_button": "",
      "end_text": "",
      "lead": "",
      "points": [],
      "title": ""
    },
    "donate_button": "",
    "empty_selection": "",
    "file_indicator_text": "",
    "inspect_button": "",
    "preview_component": {
      "entries_in_file_text": "",
      "explanation": "",
      "next_file_button": "",
      "previous_file_button": "",
      "remove_rows_button": "",
      "search_box_placeholder": "",
      "search_prompt": "",
      "title": ""
    },
    "processing_text": "",
    "thanks_text": "",
    "upload_box": {
      "explanation": "",
      "header": ""
    }
  }
}
```

#### parameters

- project_title: a brief textual name to be able to identify the configuration in the back
- admin_email: an email address of the researcher in question
- js_callback: a JavaScript function name (without brackets or parameters) that is called when the integration runs into problems or ends successfully; the callback function gets called with up to three parameters:
  - parameter 1: success, either true or false, required
  - parameter 2: error, string, empty string if success, error message otherwise, required
  - parameter 3: status, object `{}` with donated file names as keys and objects as values, each with a `n_donated` and `n_deleted` keys and integers as values, optional (only if success == true)
- i18n: key-value map of language aspects as configured in *config.yaml*


### setup response from OSD2F to survey tool

The response to the request is a JSON object that looks as follows.

```json
{
  "success": true,
  "error": "",
  "version": "",
  "js_inclusion": [],
  "html_embed": "",
  "js_embed": ""
}
```

#### parameters

- success: true if server has not run into any errors / limitations
- error: string, empty if success is true, otherwise contains error message (in English)
- version: string, version of the running OSD2F system
- js_inclusion: array with FQDN to JavaScript files to be included in the HTML header when a participant answers a data donation item
- html_embed: string with HTML code to be put into the position where the data donation item is placed
- js_embed: string with JavaScript code to be put into the HTML code after (!) the embedded HTML code
