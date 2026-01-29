from fastapi import Request, HTTPException


def validate_query_params(allowed: set[str]):
    async def _validate(request: Request):
        # if the request includes some of allowed params, extra is empty, otherwise 400
        extra = set(request.query_params.keys()) - allowed

        if extra:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query parameters: {', '.join(sorted(extra))}",
            )

    return _validate
