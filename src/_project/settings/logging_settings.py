LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {"format": "%(name)-12s %(levelname)-8s %(message)s"},
        "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
        "file": {"level": "DEBUG", "class": "logging.FileHandler", "formatter": "file", "filename": "_logs/debug.log"},
    },
    "loggers": {"": {"level": "DEBUG", "handlers": ["console", "file"]}},
}