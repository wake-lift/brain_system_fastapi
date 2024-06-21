from fastapi import HTTPException, Request

from app.core.config import templates


async def page_not_found(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request, name='/common_pages/404.html', status_code=404
    )


async def forbidden(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request, name='/common_pages/403.html', status_code=403
    )


async def bad_request(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request, name='/common_pages/400.html', status_code=400
    )


async def too_many_requests(request: Request, exc: HTTPException):
    print(request.headers)
    return templates.TemplateResponse(
        request=request, name='/common_pages/429.html', status_code=429
    )


async def internal_server_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request, name='/common_pages/500.html', status_code=500
    )


custom_error_handlers: dict = {
    404: page_not_found,
    403: forbidden,
    400: bad_request,
    429: too_many_requests,
    500: internal_server_error,
}
