import argparse
import asyncio
import logging

from osd2f import config

from .logger import logger
from .server import app, start

LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

parser = argparse.ArgumentParser(
    prog="OSD2F webserver", usage="Start the webserver and collect data donations."
)

parser.add_argument(
    "-m",
    "--mode",
    action="store",
    default="Testing",
    help="Specify the mode to run in, defaults to 'Testing'",
    choices=[
        d
        for d in dir(config)
        if not d.startswith("_") and d[0] == d[0].upper() and d != "Config"
    ],
)
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Verbosity of logging output, defaults to default=CRITICAL, "
    "v=WARNING, vv=INFO, vvv=DEBUG",
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    help="test whether endpoints provide 200 code responses,"
    " just to make sure nothing broke.",
)


def parse_and_run():
    args = parser.parse_args()

    if args.verbose == 0:
        level = logging.CRITICAL
    elif args.verbose == 1:
        level = logging.WARNING
    elif args.verbose == 2:
        level = logging.INFO
    elif args.verbose == 3:
        level = logging.DEBUG
    else:
        level = logging.NOTSET

    logging.basicConfig(format=LOGFORMAT, level="WARNING")
    logger.setLevel(level=level)

    logger.debug(
        "If you see this, you are running with debug logging. "
        "DO NOT DO THIS IN PRODUCTION."
    )

    if not args.dry_run:
        start(mode=args.mode)
    else:
        tp = app.test_client()
        assert asyncio.run(tp.get("/")).status_code == 200
        assert asyncio.run(tp.get("/privacy")).status_code == 200
        assert asyncio.run(tp.get("/upload")).status_code == 200
        assert asyncio.run(tp.get("/adv_anonymize_file")).status_code == 200
