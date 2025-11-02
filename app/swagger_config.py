from flasgger import Swagger

def configure_swagger(app):
    """
    Configure Swagger UI for API documentation
    """
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/api/docs/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    Swagger(app, config=swagger_config)