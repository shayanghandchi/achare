REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "common.common_exception.base_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_RATES": {"user": "5/minute"},
}
