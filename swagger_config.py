from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="This is my restaurant API",
        routes=app.routes,
    )

    # Define Bearer authentication in OpenAPI schema
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Apply authentication to protected routes only
    protected_routes = ["/me", "/me/update", "/food-category/create",
                        "/food_menu/add", "/get_food_menu", "/cart/add",
                        "/cart", "/order/place", "/create/feedback/",
                        "/get/feedback/", "/food_menu/delete/",
                        "/food_menu/update"]  # Add other protected routes here if needed
    for path, methods in openapi_schema["paths"].items():
        for method in methods.values():
            if path in protected_routes:
                method["security"] = [{"BearerAuth": []}]
            else:
                method.pop("security", None)  # Remove authentication requirement for public routes

    app.openapi_schema = openapi_schema
    return openapi_schema

