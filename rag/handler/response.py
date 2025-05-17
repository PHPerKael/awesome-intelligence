from fastapi.responses import JSONResponse

def format_json_response(msg: any, code=0) -> JSONResponse:
    return JSONResponse(content={
        "code": code,
        "msg": msg,
    })
