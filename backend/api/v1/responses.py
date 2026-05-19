from flask import jsonify


def successResponse(data=None, statusCode=200):
    return jsonify({
        "success": True,
        "data": data,
        "error": None,
    }), statusCode


def errorResponse(code: str, message: str, statusCode=400):
    return jsonify({
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }), statusCode
