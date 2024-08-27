from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError
import logging


class BookerException(Exception):
    """This is the base class for all booker errors"""

    pass


class InvalidToken(BookerException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(BookerException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(BookerException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(BookerException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(BookerException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(BookerException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(BookerException):
    """User does not have the necessary permissions to perform an action."""

    pass


class BookNotFound(BookerException):
    """Book Not found"""

    pass


class TagNotFound(BookerException):
    """Tag Not found"""

    pass


class TagAlreadyExists(BookerException):
    """Tag already exists"""

    pass


class UserNotFound(BookerException):
    """User Not found"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""
    pass


def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    """
    This function returns a callable function that can be used to handle exceptions
    in FastAPI. It takes in a status code and initial details to be included in the
    response and returns a function that takes in a request and an exception and
    returns a JSONResponse with the status code and details.

    Args:
    status_code (int): The status code to be used in the response
    initial_details (Any): The initial details to be included in the response

    Returns:
    Callable[[Request, Exception], JSONResponse]: A function that takes in a request
    and an exception and returns a JSONResponse with the status code and details
    """

    async def exception_handler(request: Request, exc: BookerException) -> JSONResponse:
        logging.error(f"An error occurred: {exc}")
        return JSONResponse(
            status_code=status_code,
            content=initial_detail
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(UserAlreadyExists, create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN, initial_detail={
            "message": "User already exists",
            "error_code": "user_already_exists"
        }))
    app.add_exception_handler(UserNotFound, create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND, initial_detail={
            "message": "User not found",
            "error_code": "user_not_found"
        }
    ))
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "Tag Not Found",
                            "error_code": "tag_not_found"},
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Tag Already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book Not Found",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account Not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details"
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        print(str(exc))
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
