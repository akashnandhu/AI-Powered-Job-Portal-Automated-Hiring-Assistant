def safe_run(func, fallback=None):
    try:
        return func()
    except Exception as e:
        return {
            "error": str(e),
            "fallback": fallback,
            "status": "handled"
        }
