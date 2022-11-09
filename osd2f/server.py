import csv
import io
import json
import typing

from osd2f import config, database, security, utils
from osd2f.definitions import Submission, SubmissionList
from osd2f.security.authorization import USER_FIELD
from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry

from quart import Quart, redirect, render_template, request, session
from quart.json import jsonify
from quart.wrappers.response import Response

from quart_cors import route_cors

from pydantic import ValidationError

from .anonymizers import anonymize_submission
from .logger import logger
from .definitions import ContentSettings, UploadSettings
from .database import set_content_config, set_upload_config, get_content_config, get_upload_config

app = Quart(__name__)
OSD2F_VERSION = "0.1.1"


@app.before_serving
async def start_database():
    logger.debug(f"DB URL: {app.config['DB_URL']}")
    await database.initialize_database(app.config["DB_URL"])
    app.logQueue = database.add_database_logging()
    await utils.load_content_settings(use_cache=False)


@app.after_serving
async def stop_database():
    logger.debug("Stopping database")
    await database.stop_database()
    app.logQueue.put("stop-logging")  # signals the database log worker to stop


async def render_page(pagename: str):
    """Get the specified page-specification from the content settings and render it."""

    if app.env == "survey":
        if app.config['BLOCK_RENDERING']:
            await database.insert_log(
                "survey",
                "ERROR",
                "page rendering requested but blocked due to survey mode",
                entry={"pagename": pagename},
                user_agent_string=request.headers["User-Agent"],
            )
            return jsonify({"success": False,
                            "error": "page unavailable"}), 400

    settings = await utils.load_content_settings(use_cache=not app.debug)
    if pagename not in settings.static_pages.keys():
        await database.insert_log(
            "server",
            "INFO",
            "unknown page visited",
            entry={"pagename": pagename},
            user_agent_string=request.headers["User-Agent"],
        )
        return await render_page("home")
    await database.insert_log(
        "server",
        "INFO",
        f"{pagename} visited",
        user_agent_string=request.headers["User-Agent"],
    )
    return await render_template(
        "formats/static_template.html.jinja",
        content_settings=settings,
        current_page=pagename,
    )


@app.route("/")
@app.route("/home")
async def home():
    return await render_page("home")


@app.route("/privacy")
async def privacy():
    return await render_page("privacy")


@app.route("/donate")
async def donate():
    return await render_page("donate")


@app.route("/upload", methods=["GET", "POST"])
@route_cors(allow_origin="*")
async def upload():
    # for users visiting the page
    if request.method == "GET":
        # sid is an ID by which a referrer may identify
        # a user. This could for instance be the id that
        # a survey tool uses to match the survey response
        # to the submitted donation.
        sid = request.args.get("sid", "test")

        await database.insert_log(
            "server",
            "INFO",
            "upload page visited",
            sid,
            user_agent_string=request.headers["User-Agent"],
        )
        upload_settings = utils.load_upload_settings(force_disk=app.debug)
        content_settings = await utils.load_content_settings(use_cache=not app.debug)
        return await render_template(
            "formats/upload_template.html.jinja",
            content_settings=content_settings,
            upload_settings=upload_settings,
            sid=request.args.get("sid", "test"),
            all_links_new_tab=True,
        )
    # for data submissions posted by the interface
    elif request.method == "POST":
        data = await request.get_data()
        try:
            submissionlist = SubmissionList.parse_raw(data)
            logger.info("Received the donation!")
            await database.insert_submission_list(submissionlist=submissionlist)
        except ValueError:
            logger.info("Invallid submission format received")
            await database.insert_log(
                "server",
                "ERROR",
                "unparsable submission received",
                user_agent_string=request.headers["User-Agent"],
            )
            return jsonify({"error": "incorrect submission format", "data": {}}), 400
        return jsonify({"error": "", "data": ""}), 200


@app.route("/login")
@security.authorization_required
async def login():
    return "logged in"


@app.route("/logout")
async def logout():
    if session.get(USER_FIELD):
        session.pop(USER_FIELD)
    return redirect("/")


@app.route("/researcher", strict_slashes=False)
@security.authorization_required
async def researcher():
    content_settings = await utils.load_content_settings(use_cache=not app.debug)
    return await render_template(
        "formats/researcher_template.html.jinja",
        content_settings=content_settings,
        password_protected=bool(app.config["DATA_PASSWORD"]),
    )


@app.route("/researcher/<items>.<filetype>.<zipext>")
@app.route("/researcher/<items>.<filetype>")
@security.authorization_required
async def downloads(items: str = None, filetype: str = None, zipext: str = None):

    if not items:
        return redirect("/researcher")
    elif items == "osd2f_completed_submissions":
        data = await database.get_submissions()
    elif items == "osd2f_pending_participants":
        data = await database.get_pending_participants()
    elif items == "osd2f_activity_logs":
        data = await database.get_activity_logs()
    else:
        return "Unknown export", 404

    if app.config.get("DATA_PASSWORD") and not zipext:
        logger.warning("Non-zip downloaded requested, but OSD2F_DATA_PASSWORD is set.")
        return "Only encrypted `.zip` files are available", 401

    st = io.StringIO()
    if filetype == "json":
        fs = json.dumps(data)
        st.write(fs)
    elif filetype == "csv":
        fields = {key for item in data for key in item}
        dw = csv.DictWriter(st, fieldnames=sorted(fields))
        dw.writeheader()
        dw.writerows(data)
    else:
        return "Unknown filetype", 404

    if zipext:
        filename = f"{items}.{filetype}"
        password = app.config.get("DATA_PASSWORD", "")
        zipfile_body = security.string_to_zipfile(
            file_content=st, filename=filename, password=password
        )

        return Response(zipfile_body, 200, {"Content-type": "application/zip"})

    fs = st.getvalue()
    return Response(fs, 200, {"Content-type": "application/text; charset=utf-8"})


@app.route("/adv_anonymize_file", methods=["POST"])
@route_cors(allow_origin="*")
async def adv_anonymize_file():
    data = await request.get_data()
    logger.debug(f"[anonymization] received: {data}")
    if app.env == 'survey':
        data_json = json.loads(data)
        if 'survey_config_upload_id' in data_json:
            config_upload_id = data_json['survey_config_upload_id']
            del(data_json['survey_config_upload_id'])
            data = json.dumps(data_json)
            settings_db = await get_upload_config(config_upload_id)
            logger.debug(f'survey mode detected, upload config with id #{config_upload_id} loaded')
        else:
            settings_db = await get_upload_config()
        settings = UploadSettings.parse_obj(settings_db.config_blob)
    else:
        settings = utils.load_upload_settings(force_disk=app.debug)
    try:
        submission = Submission.parse_raw(data)
    except ValueError as e:
        logger.debug(f"file anonymization failed: {e}")
        await database.insert_log(
            "server",
            "ERROR",
            "anonymization received unparsable file",
            user_agent_string=request.headers["User-Agent"],
        )
        return jsonify({"error": "incorrect format"}), 400

    await database.insert_log(
        "server",
        "INFO",
        "anonymization received file",
        submission.submission_id,
        user_agent_string=request.headers["User-Agent"],
    )
    submission = await anonymize_submission(submission=submission, settings=settings)
    return jsonify({"error": "", "data": submission.dict()}), 200


@app.route("/log")
@route_cors(allow_origin="*")
async def log():
    position = request.args.get("position")
    level = request.args.get("level")
    sid = request.args.get("sid")
    entry = json.loads(request.args.get("entry")) if request.args.get("entry") else None
    source = "client"
    if app.debug:
        logger.info(f"Received: {level}-{position}({sid}): {entry}")
    await database.insert_log(
        log_level=level,
        log_position=position,
        log_sid=sid,
        log_source=source,
        user_agent_string=request.headers["User-Agent"],
    )
    return "", 200


@app.route("/survey", methods=["GET", "POST"])
@route_cors(allow_origin="*")
async def survey():
    if request.method == "GET":
        if app.env == "survey":
            return jsonify({"success": True,
                            "error": "",
                            "version": OSD2F_VERSION}), 200
        else:
            return jsonify({"success": False,
                            "error": "OSD2F not running in Survey Mode",
                            "version": OSD2F_VERSION}), 200

    elif request.method == "POST":
        try:
            post_config_data = json.loads(await request.get_data())

            if app.config["SURVEY_TOKEN"] is None or app.config["SURVEY_TOKEN"] != post_config_data['token']:
                await database.insert_log("survey",
                                          "ERROR",
                                          "accessed /survey endpoint without adequate SURVEY_TOKEN",
                                          user_agent_string=request.headers["User-Agent"])
                return jsonify({"success": False,
                                "error": "Survey token missing or wrong",
                                "version": OSD2F_VERSION}), 200

            config_content = ContentSettings.parse_obj({"contact_us": post_config_data['admin_email'],
                                                        "project_title": post_config_data['project_title'],
                                                        "upload_page": post_config_data['content'],
                                                        "static_pages": {},
                                                        "survey_base_url": request.base_url.replace('/survey', '/'),
                                                        "survey_js_callback": post_config_data['js_callback_after_upload']})
            await set_content_config(user=post_config_data['admin_email'],
                                     content=config_content)
            await database.insert_log("survey",
                                      "INFO",
                                      "survey configuration received and successfully stored as content configuration",
                                      user_agent_string=request.headers["User-Agent"])
            config_content_db = await get_content_config()

            config_upload = UploadSettings.parse_obj({"files": post_config_data['upload']})
            await set_upload_config(user=post_config_data['admin_email'],
                                    content=config_upload)
            await database.insert_log("survey",
                                      "INFO",
                                      "survey configuration received and successfully stored as upload configuration",
                                      user_agent_string=request.headers["User-Agent"])
            config_upload_db = await get_upload_config()

        except ValidationError as error:
            logger.info("Invalid configuration format received")
            await database.insert_log("survey",
                                      "ERROR",
                                      "unparsable configuration received",
                                      user_agent_string=request.headers["User-Agent"])
            return jsonify({"success": False,
                            "error": f"Incorrect configuration format: {str(error)}"}), 400

        else:
            await database.insert_log("server",
                                      "INFO",
                                      "upload page rendered for survey mode",
                                      user_agent_string=request.headers["User-Agent"])
            placeholder_sid = "### SID ###"
            placeholder_libarchivejs = "### LIBARCHIVE.JS ###"
            return jsonify({"success": True,
                            "error": "",
                            "config_id_content": config_content_db.id,
                            "config_id_upload": config_upload_db.id,
                            "head_inclusion": ["https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css",
                                               "https://code.jquery.com/jquery-3.5.1.slim.min.js",
                                               "https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js"],
                            "html_embed": await render_template("formats/upload_survey_template.html.jinja",
                                                                content_settings=config_content,
                                                                upload_settings=config_upload,
                                                                base_url=request.base_url),
                            "js_embed": await render_template("formats/upload_survey_script.js.jinja",
                                                              content_settings=config_content,
                                                              upload_settings=config_upload,
                                                              sid=placeholder_sid,
                                                              libarchivejs=placeholder_libarchivejs,
                                                              config_upload_id=config_upload_db.id,
                                                              base_url=request.base_url),
                            "js_embed_placeholder_surveyid": placeholder_sid,
                            "js_embed_placeholder_libarchivejs": placeholder_libarchivejs}), 200


def create_app(
    mode: str = "Testing",
    database_url_override: typing.Optional[str] = None,
    app_secret_override: typing.Optional[str] = None,
    data_password_override: typing.Optional[str] = None,
    entry_secret_override: typing.Optional[str] = None,
    entry_decrypt_disable: typing.Optional[bool] = None,
) -> Quart:
    """Create a Quart app instance with appropriate configuration and sanity checks."""
    selected_config: config.Config = getattr(config, mode)()

    if data_password_override:
        logger.debug("Using CLI specified DATA PASSWORD instead of ENV VAR")
        selected_config.DATA_PASSWORD = security.translate_value(data_password_override)
    if app_secret_override:
        logger.debug("Using CLI specified SECRET instead of ENV VAR")
        selected_config.SECRET_KEY = security.translate_value(app_secret_override)
    if database_url_override:
        logger.debug("Using CLI specified DB URL instead of ENV VAR")
        selected_config.DB_URL = security.translate_value(database_url_override)
    if entry_secret_override:
        logger.debug("Using CLI specified Entry encryption secret instead of ENV VAR")
        selected_config.ENTRY_SECRET = security.translate_value(entry_secret_override)

    read_disabed = entry_decrypt_disable or selected_config.ENTRY_DECRYPT_DISABLE

    SecureEntry.set_secret(secret=selected_config.ENTRY_SECRET)
    SecureEntry.decrypt_on_read(must_decrypt_on_read=not read_disabed)

    app.config.from_object(selected_config)
    app.env = mode.lower()

    # Check to make sure the application is never in production with a vacant key
    in_production_mode = mode == "Production"
    key_is_set = app.config["SECRET_KEY"] is not None
    db_is_set = app.config["DB_URL"] is not None
    if in_production_mode:
        logger.info("Starting app in production mode")
        assert key_is_set, ValueError(
            "To run OSD2F in production, the `OSD2F_SECRET` environment "
            "variable MUST be set."
        )

        assert db_is_set, ValueError(
            "To run OSD2F in production, a database url should be specified "
            "either as an env variabel (OSD2f_DB_URL) or via the CLI."
        )

    logger.debug(app.config)
    return app


def start_app(app: Quart):
    """Start Quart application with configured bind, port and debug state."""
    app.run(host=app.config["BIND"], port=app.config["PORT"], debug=app.config["DEBUG"])
